# -*- coding: utf-8 -*-

import json
import logging
import re
import requests
import time
from datetime import datetime

from odoo import models, api, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Corporate email domains that indicate business legitimacy
CORPORATE_EMAIL_BONUS = 15
PERSONAL_EMAIL_PENALTY = -10
PERSONAL_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
    'icloud.com', 'mail.com', 'protonmail.com', 'yandex.com', 'zoho.com',
    'live.com', 'msn.com', 'me.com', 'inbox.com', 'gmx.com', 'fastmail.com'
}

# Urgency keywords and their weights
URGENCY_KEYWORDS = {
    'high': ['urgent', 'asap', 'immediately', 'emergency', 'critical', 'rush', 'deadline today'],
    'medium': ['soon', 'this week', 'next week', 'this month', 'q1', 'q2', 'q3', 'q4', 'priority'],
    'low': ['eventually', 'no rush', 'when possible', 'next year', 'exploring', 'researching']
}

# Decision maker titles
DECISION_MAKER_TITLES = [
    'ceo', 'cfo', 'cto', 'coo', 'cmo', 'cio', 'chief', 'president', 'owner',
    'director', 'vp', 'vice president', 'head of', 'manager', 'lead',
    'founder', 'co-founder', 'partner', 'principal', 'executive'
]


class LLMService(models.AbstractModel):
    _name = 'llm.service'
    _description = 'LLM Integration Service'

    @api.model
    @tools.ormcache()
    def _get_scoring_weights(self):
        """
        Get scoring weights from configuration with caching for performance

        Returns:
            dict: {'completeness': float, 'clarity': float, 'engagement': float}
        """
        config = self.env['ir.config_parameter'].sudo()
        return {
            'completeness': float(config.get_param('llm_lead_scoring.weight_completeness', '30.0')) / 100.0,
            'clarity': float(config.get_param('llm_lead_scoring.weight_clarity', '40.0')) / 100.0,
            'engagement': float(config.get_param('llm_lead_scoring.weight_engagement', '30.0')) / 100.0,
        }

    @api.model
    @tools.ormcache()
    def _get_config_bool(self, param_name, default='False'):
        """
        Get boolean configuration parameter with caching

        Args:
            param_name: Configuration parameter name
            default: Default value if not set

        Returns:
            bool: Configuration value
        """
        config = self.env['ir.config_parameter'].sudo()
        return config.get_param(param_name, default) == 'True'

    @api.model
    def call_llm(self, messages, provider=None, system_prompt=None, max_retries=3):
        """
        Call LLM API with given messages, including retry logic with exponential backoff

        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: llm.provider record (uses default if not provided)
            system_prompt: Optional system prompt
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            dict: {'success': bool, 'content': str, 'error': str, 'retries': int}
        """
        if not provider:
            provider = self.env['llm.provider'].get_default_provider()

        if not provider:
            return {
                'success': False,
                'content': '',
                'error': 'No LLM provider configured. Please configure an LLM provider in Settings.',
                'retries': 0
            }

        # Retry configuration
        retry_count = 0
        base_delay = 1.0  # Start with 1 second

        while retry_count <= max_retries:
            try:
                url = provider.get_api_url()
                headers = provider.get_api_headers()
                payload = provider.format_request_payload(messages, system_prompt)

                if retry_count > 0:
                    _logger.info("Retry attempt %d/%d for LLM API: %s",
                                retry_count, max_retries, provider.name)
                else:
                    _logger.info("Calling LLM API: %s (%s)", provider.name, provider.provider_type)

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=provider.timeout
                )

                # Success case
                if response.status_code == 200:
                    response_json = response.json()
                    content = provider.parse_response(response_json)
                    provider.increment_usage(success=True)

                    if retry_count > 0:
                        _logger.info("LLM API call succeeded after %d retries", retry_count)

                    return {
                        'success': True,
                        'content': content,
                        'error': '',
                        'retries': retry_count
                    }

                # Rate limit or temporary error - retry
                elif response.status_code in [429, 500, 502, 503, 504]:
                    if retry_count < max_retries:
                        # Exponential backoff: 1s, 2s, 4s, 8s...
                        delay = base_delay * (2 ** retry_count)
                        _logger.warning(
                            "LLM API returned status %d, retrying in %.1f seconds (attempt %d/%d)",
                            response.status_code, delay, retry_count + 1, max_retries
                        )
                        time.sleep(delay)
                        retry_count += 1
                        continue
                    else:
                        # Max retries exceeded
                        error_msg = "API Error %s after %d retries: %s" % (
                            response.status_code, retry_count, response.text[:200]
                        )
                        _logger.error(error_msg)
                        provider.increment_usage(success=False)
                        return {
                            'success': False,
                            'content': '',
                            'error': error_msg,
                            'retries': retry_count
                        }

                # Client error (4xx) - don't retry
                else:
                    error_detail = response.text[:200]
                    
                    # Provide helpful error messages for common issues
                    if response.status_code == 401:
                        if 'invalid_api_key' in error_detail.lower() or 'invalid api key' in error_detail.lower():
                            error_msg = "Invalid API Key: Please update the API key in CRM → Configuration → LLM Providers. Get a valid API key from %s" % provider.get_provider_signup_url()
                        else:
                            error_msg = "Authentication Error (401): The API key may be expired or invalid. Please check your LLM Provider configuration."
                    elif response.status_code == 403:
                        error_msg = "Access Forbidden (403): Your API key doesn't have permission to use this model (%s). Please check your plan or upgrade." % provider.model_name
                    elif response.status_code == 404:
                        error_msg = "Model Not Found (404): The model '%s' doesn't exist or isn't available. Please check the model name in LLM Provider settings." % provider.model_name
                    else:
                        error_msg = "API Error %s: %s" % (response.status_code, error_detail)
                    
                    _logger.error("%s - Provider: %s, Model: %s", error_msg, provider.name, provider.model_name)
                    provider.increment_usage(success=False)
                    return {
                        'success': False,
                        'content': '',
                        'error': error_msg,
                        'retries': retry_count
                    }

            except requests.exceptions.Timeout:
                if retry_count < max_retries:
                    delay = base_delay * (2 ** retry_count)
                    _logger.warning(
                        "Request timeout, retrying in %.1f seconds (attempt %d/%d)",
                        delay, retry_count + 1, max_retries
                    )
                    time.sleep(delay)
                    retry_count += 1
                    continue
                else:
                    error_msg = "Request timeout after %d retries" % retry_count
                    _logger.error(error_msg)
                    provider.increment_usage(success=False)
                    return {
                        'success': False,
                        'content': '',
                        'error': error_msg,
                        'retries': retry_count
                    }

            except requests.exceptions.ConnectionError as e:
                if retry_count < max_retries:
                    delay = base_delay * (2 ** retry_count)
                    _logger.warning(
                        "Connection error: %s, retrying in %.1f seconds (attempt %d/%d)",
                        str(e)[:100], delay, retry_count + 1, max_retries
                    )
                    time.sleep(delay)
                    retry_count += 1
                    continue
                else:
                    error_msg = "Connection error after %d retries: %s" % (retry_count, str(e)[:100])
                    _logger.error(error_msg)
                    provider.increment_usage(success=False)
                    return {
                        'success': False,
                        'content': '',
                        'error': error_msg,
                        'retries': retry_count
                    }

            except Exception as e:
                # Unexpected errors - don't retry
                error_msg = "LLM API Error: %s" % str(e)
                _logger.error(error_msg, exc_info=True)
                provider.increment_usage(success=False)
                return {
                    'success': False,
                    'content': '',
                    'error': error_msg,
                    'retries': retry_count
                }

        # Should not reach here, but safety fallback
        return {
            'success': False,
            'content': '',
            'error': 'Maximum retries exceeded',
            'retries': retry_count
        }

    @api.model
    def research_customer(self, lead):
        """
        Research customer using LLM and optionally live web search
        
        Tries web research first (if enabled), falls back to LLM knowledge

        Args:
            lead: crm.lead record

        Returns:
            str: Research findings (HTML formatted)
        """
        # Check if web research is enabled and configured
        web_research_enabled = self._get_config_bool('llm_lead_scoring.enable_web_research', 'False')
        
        if web_research_enabled:
            # Use live Google Custom Search
            _logger.info("Using live web research for lead: %s", lead.name)
            web_research_service = self.env['web.research.service']
            return web_research_service.research_company_web(lead)
        
        # Fallback: Use LLM's training knowledge (original method)
        _logger.info("Using LLM knowledge base for lead: %s", lead.name)
        
        company_name = lead.partner_name or lead.contact_name or 'Unknown'
        email = lead.email_from or ''
        phone = lead.phone or lead.mobile or ''
        website = lead.website or ''

        research_prompt = f"""You are a professional business researcher. Research and provide insights about the following customer/company:

Company/Contact Name: {company_name}
Email: {email}
Phone: {phone}
Website: {website}

Please provide:
1. Company background and industry (if available)
2. Company size and market presence
3. Key products/services
4. Recent news or developments
5. Business credibility indicators
6. Potential buying signals or business needs

IMPORTANT: Only provide information that would be publicly available. If information is not available, clearly state that. Be factual and concise.
"""

        messages = [
            {'role': 'user', 'content': research_prompt}
        ]

        result = self.call_llm(messages)

        if result['success']:
            return result['content']
        else:
            return f"Research could not be completed: {result['error']}"

    @api.model
    def analyze_lead_completeness(self, lead):
        """
        Analyze how complete the lead information is

        Returns:
            dict: {'score': float (0-100), 'analysis': str, 'missing_fields': list}
        """
        # Define critical and optional fields
        critical_fields = {
            'partner_name': 'Company Name',
            'contact_name': 'Contact Name',
            'email_from': 'Email',
            'phone': 'Phone',
            'description': 'Description/Requirements',
        }

        optional_fields = {
            'mobile': 'Mobile',
            'website': 'Website',
            'street': 'Street Address',
            'city': 'City',
            'country_id': 'Country',
            'user_id': 'Salesperson',
            'team_id': 'Sales Team',
            'tag_ids': 'Tags',
            'expected_revenue': 'Expected Revenue',
        }

        # Calculate completeness
        critical_filled = 0
        critical_total = len(critical_fields)
        missing_critical = []

        for field, label in critical_fields.items():
            value = getattr(lead, field, None)
            if value:
                critical_filled += 1
            else:
                missing_critical.append(label)

        optional_filled = 0
        optional_total = len(optional_fields)
        missing_optional = []

        for field, label in optional_fields.items():
            value = getattr(lead, field, None)
            if value:
                optional_filled += 1
            else:
                missing_optional.append(label)

        # Calculate score (critical fields weight 70%, optional 30%)
        critical_score = (critical_filled / critical_total) * 70
        optional_score = (optional_filled / optional_total) * 30
        total_score = critical_score + optional_score

        # Generate analysis
        analysis_parts = []
        if total_score >= 80:
            analysis_parts.append("Lead information is comprehensive.")
        elif total_score >= 60:
            analysis_parts.append("Lead information is adequate but could be improved.")
        else:
            analysis_parts.append("Lead information is incomplete.")

        if missing_critical:
            analysis_parts.append(f"Missing critical fields: {', '.join(missing_critical)}.")

        if missing_optional and total_score < 90:
            analysis_parts.append(f"Consider adding: {', '.join(missing_optional[:3])}.")

        return {
            'score': round(total_score, 2),
            'analysis': ' '.join(analysis_parts),
            'missing_fields': missing_critical + missing_optional,
            'critical_missing': missing_critical,
            'optional_missing': missing_optional,
        }

    @api.model
    def analyze_requirement_clarity(self, lead):
        """
        Use LLM to analyze how clear the customer requirements are

        Returns:
            dict: {'score': float (0-100), 'analysis': str}
        """
        description = lead.description or ''

        if not description or len(description.strip()) < 10:
            return {
                'score': 0,
                'analysis': 'No requirements or description provided. Customer needs are unclear.',
            }

        clarity_prompt = f"""Analyze the clarity and specificity of the following customer requirement/description. Rate the clarity from 0-100 based on:
- Specificity of needs
- Clear objectives
- Detailed requirements
- Actionable information
- Budget/timeline mentions

Customer Description:
{description}

Provide your response in the following JSON format:
{{
    "score": <number 0-100>,
    "analysis": "<brief analysis of clarity>",
    "key_points": ["<key requirement 1>", "<key requirement 2>"],
    "missing_info": ["<missing info 1>", "<missing info 2>"]
}}
"""

        messages = [{'role': 'user', 'content': clarity_prompt}]
        result = self.call_llm(messages)

        if result['success']:
            try:
                # Try to parse JSON response
                content = result['content']
                # Extract JSON from markdown code blocks if present
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()

                parsed = json.loads(content)
                return {
                    'score': float(parsed.get('score', 50)),
                    'analysis': parsed.get('analysis', ''),
                    'key_points': parsed.get('key_points', []),
                    'missing_info': parsed.get('missing_info', []),
                }
            except (json.JSONDecodeError, ValueError, KeyError):
                # Fallback to simple analysis
                return {
                    'score': 50,
                    'analysis': result['content'][:500],
                }
        else:
            return {
                'score': 50,
                'analysis': f"Could not analyze requirements: {result['error']}",
            }

    @api.model
    def analyze_activity_engagement(self, lead):
        """
        Analyze lead engagement based on activities and logs

        Returns:
            dict: {'score': float (0-100), 'analysis': str}
        """
        # Get activities and messages
        activities = self.env['mail.activity'].search([
            ('res_id', '=', lead.id),
            ('res_model', '=', 'crm.lead')
        ])

        messages = self.env['mail.message'].search([
            ('res_id', '=', lead.id),
            ('model', '=', 'crm.lead'),
            ('message_type', 'in', ['email', 'comment'])
        ], order='date desc', limit=20)

        activity_count = len(activities)
        message_count = len(messages)

        # Calculate engagement score
        activity_score = min(activity_count * 10, 40)  # Max 40 points for activities
        message_score = min(message_count * 3, 40)     # Max 40 points for messages

        # Recent engagement bonus (20 points)
        recent_score = 0
        if messages:
            latest_message = messages[0]
            from odoo import fields
            days_since = (fields.Datetime.now() - latest_message.date).days
            if days_since <= 1:
                recent_score = 20
            elif days_since <= 7:
                recent_score = 15
            elif days_since <= 30:
                recent_score = 10

        total_score = activity_score + message_score + recent_score

        # Generate analysis
        if total_score >= 70:
            engagement_level = "highly engaged"
        elif total_score >= 40:
            engagement_level = "moderately engaged"
        else:
            engagement_level = "low engagement"

        analysis = "Lead shows %s with %d activities and %d interactions." % (
            engagement_level, activity_count, message_count)

        return {
            'score': min(total_score, 100),
            'analysis': analysis,
            'activity_count': activity_count,
            'message_count': message_count,
        }

    @api.model
    def analyze_email_quality(self, lead):
        """
        Analyze email quality and business legitimacy
        
        Corporate emails score higher than personal emails (gmail, yahoo, etc.)
        Valid format and domain matching company name = bonus
        
        Returns:
            dict: {'score': float (0-100), 'analysis': str, 'email_type': str}
        """
        email = (lead.email_from or '').lower().strip()
        company_name = (lead.partner_name or '').lower()
        
        if not email or '@' not in email:
            return {
                'score': 0,
                'analysis': 'No email provided. Cannot verify contact legitimacy.',
                'email_type': 'missing'
            }
        
        # Extract domain
        try:
            local_part, domain = email.split('@')
        except ValueError:
            return {
                'score': 10,
                'analysis': 'Invalid email format.',
                'email_type': 'invalid'
            }
        
        score = 50  # Base score
        analysis_parts = []
        email_type = 'unknown'
        
        # Check if personal email domain
        domain_base = domain.split('.')[0] if '.' in domain else domain
        if domain in PERSONAL_EMAIL_DOMAINS:
            score += PERSONAL_EMAIL_PENALTY
            email_type = 'personal'
            analysis_parts.append(f"Personal email ({domain}) - less reliable for B2B.")
        else:
            # Corporate email - bonus
            score += CORPORATE_EMAIL_BONUS
            email_type = 'corporate'
            analysis_parts.append(f"Corporate email domain ({domain}).")
            
            # Check if domain matches company name
            if company_name:
                company_words = company_name.replace('.', ' ').replace('-', ' ').split()
                domain_clean = domain.replace('.com', '').replace('.net', '').replace('.org', '')
                
                for word in company_words:
                    if len(word) > 3 and word in domain_clean:
                        score += 10
                        analysis_parts.append("Email domain matches company name.")
                        break
        
        # Check for role-based emails (info@, sales@, contact@) - less valuable
        role_prefixes = ['info', 'sales', 'contact', 'support', 'admin', 'hello', 'enquiry', 'enquiries']
        if local_part in role_prefixes:
            score -= 5
            analysis_parts.append("Generic role-based email (not personal contact).")
        
        # Validate email format quality
        if len(local_part) >= 3 and '.' in local_part:
            score += 5  # firstname.lastname format
            analysis_parts.append("Professional email format (firstname.lastname).")
        
        return {
            'score': max(0, min(100, score)),
            'analysis': ' '.join(analysis_parts) if analysis_parts else 'Email analyzed.',
            'email_type': email_type,
            'domain': domain
        }

    @api.model
    def analyze_budget_qualification(self, lead):
        """
        Analyze budget/revenue qualification
        
        Factors:
        - Expected revenue field filled
        - Budget mentioned in description
        - Revenue compared to typical deal size
        
        Returns:
            dict: {'score': float (0-100), 'analysis': str, 'budget_mentioned': bool}
        """
        expected_revenue = lead.expected_revenue or 0
        description = (lead.description or '').lower()
        
        score = 30  # Base score
        analysis_parts = []
        budget_mentioned = False
        
        # Check expected_revenue field
        if expected_revenue > 0:
            score += 25
            analysis_parts.append(f"Expected revenue: {expected_revenue:,.2f}")
            
            # Compare to typical deals (get average from won opportunities)
            try:
                won_leads = self.env['crm.lead'].search([
                    ('type', '=', 'opportunity'),
                    ('stage_id.is_won', '=', True),
                    ('expected_revenue', '>', 0)
                ], limit=100)
                
                if won_leads:
                    avg_revenue = sum(l.expected_revenue for l in won_leads) / len(won_leads)
                    if expected_revenue >= avg_revenue * 1.5:
                        score += 15
                        analysis_parts.append("Above average deal size.")
                    elif expected_revenue >= avg_revenue * 0.5:
                        score += 10
                        analysis_parts.append("Typical deal size.")
                    else:
                        analysis_parts.append("Below average deal size.")
            except Exception:
                pass  # Skip comparison if error
        else:
            analysis_parts.append("No expected revenue specified.")
        
        # Check for budget keywords in description
        budget_patterns = [
            r'budget[:\s]+[\$€£]?[\d,]+',
            r'[\$€£][\d,]+\s*(k|m|million|thousand)?',
            r'budget\s*(is|of|around|approximately)',
            r'(can spend|willing to pay|investment of)',
            r'\d+\s*(k|m)\s*(budget|investment)'
        ]
        
        for pattern in budget_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                budget_mentioned = True
                score += 15
                analysis_parts.append("Budget mentioned in description.")
                break
        
        if not budget_mentioned and expected_revenue == 0:
            analysis_parts.append("No budget information available.")
        
        return {
            'score': max(0, min(100, score)),
            'analysis': ' '.join(analysis_parts),
            'budget_mentioned': budget_mentioned,
            'expected_revenue': expected_revenue
        }

    @api.model
    def analyze_urgency(self, lead):
        """
        Analyze urgency and timeline from description and fields
        
        Detects urgency keywords and deadline mentions
        
        Returns:
            dict: {'score': float (0-100), 'analysis': str, 'urgency_level': str}
        """
        description = (lead.description or '').lower()
        
        # Check date_deadline field
        has_deadline = bool(lead.date_deadline)
        
        score = 40  # Base/neutral score
        urgency_level = 'normal'
        analysis_parts = []
        
        # Check for urgency keywords
        high_urgency_found = False
        medium_urgency_found = False
        low_urgency_found = False
        
        for keyword in URGENCY_KEYWORDS['high']:
            if keyword in description:
                high_urgency_found = True
                break
        
        for keyword in URGENCY_KEYWORDS['medium']:
            if keyword in description:
                medium_urgency_found = True
                break
        
        for keyword in URGENCY_KEYWORDS['low']:
            if keyword in description:
                low_urgency_found = True
                break
        
        # Score based on urgency signals
        if high_urgency_found:
            score += 40
            urgency_level = 'high'
            analysis_parts.append("🔥 HIGH URGENCY detected in requirements.")
        elif medium_urgency_found:
            score += 20
            urgency_level = 'medium'
            analysis_parts.append("⏰ Medium urgency - timeline mentioned.")
        elif low_urgency_found:
            score -= 15
            urgency_level = 'low'
            analysis_parts.append("📅 Low urgency - no immediate need.")
        else:
            analysis_parts.append("No urgency indicators detected.")
        
        # Deadline field bonus
        if has_deadline:
            from odoo import fields
            days_until = (lead.date_deadline - fields.Date.today()).days
            if days_until <= 7:
                score += 25
                analysis_parts.append(f"Deadline in {days_until} days!")
            elif days_until <= 30:
                score += 15
                analysis_parts.append(f"Deadline in {days_until} days.")
            elif days_until <= 90:
                score += 5
                analysis_parts.append(f"Deadline in {days_until} days.")
        
        # Check for timeline/date mentions in description
        timeline_patterns = [
            r'by\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'(next|this)\s+(week|month|quarter)',
            r'within\s+\d+\s+(days|weeks|months)',
            r'deadline[:\s]+',
            r'need\s+by',
            r'(q1|q2|q3|q4)\s+202[4-6]'
        ]
        
        for pattern in timeline_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                if urgency_level == 'normal':
                    score += 10
                    urgency_level = 'medium'
                analysis_parts.append("Timeline mentioned in description.")
                break
        
        return {
            'score': max(0, min(100, score)),
            'analysis': ' '.join(analysis_parts),
            'urgency_level': urgency_level,
            'has_deadline': has_deadline
        }

    @api.model
    def analyze_contact_quality(self, lead):
        """
        Analyze contact quality and decision-maker potential
        
        Checks:
        - Contact name provided
        - Job title/function (decision maker?)
        - Phone number quality
        - Multiple contact methods
        
        Returns:
            dict: {'score': float (0-100), 'analysis': str, 'is_decision_maker': bool}
        """
        contact_name = lead.contact_name or ''
        function = (lead.function or '').lower()
        phone = lead.phone or ''
        mobile = lead.mobile or ''
        
        score = 30  # Base score
        analysis_parts = []
        is_decision_maker = False
        
        # Check contact name
        if contact_name:
            score += 15
            analysis_parts.append("Contact name provided.")
            
            # Check for full name (first + last)
            if ' ' in contact_name.strip():
                score += 5
                analysis_parts.append("Full name available.")
        else:
            analysis_parts.append("No contact name.")
        
        # Check job title/function
        if function:
            score += 10
            # Check if decision maker
            for title in DECISION_MAKER_TITLES:
                if title in function:
                    is_decision_maker = True
                    score += 20
                    analysis_parts.append(f"🎯 Decision maker: {lead.function}")
                    break
            
            if not is_decision_maker:
                analysis_parts.append(f"Title: {lead.function}")
        else:
            analysis_parts.append("Job title unknown.")
        
        # Check phone numbers
        phone_count = 0
        if phone and len(phone) >= 7:
            phone_count += 1
        if mobile and len(mobile) >= 7:
            phone_count += 1
        
        if phone_count >= 2:
            score += 15
            analysis_parts.append("Multiple phone numbers available.")
        elif phone_count == 1:
            score += 10
            analysis_parts.append("Phone number available.")
        else:
            analysis_parts.append("No phone number.")
        
        return {
            'score': max(0, min(100, score)),
            'analysis': ' '.join(analysis_parts),
            'is_decision_maker': is_decision_maker,
            'has_phone': phone_count > 0
        }

    @api.model
    def calculate_ai_probability_score(self, lead):
        """
        Calculate overall AI probability score combining all factors
        
        Enhanced scoring with 7 dimensions:
        - Completeness (how complete is lead info)
        - Clarity (how clear are requirements)
        - Engagement (activity and interaction level)
        - Email Quality (corporate vs personal)
        - Budget (revenue qualification)
        - Urgency (timeline and need)
        - Contact Quality (decision maker detection)

        Returns:
            dict: Complete scoring analysis
        """
        # Get individual scores - Core factors
        completeness = self.analyze_lead_completeness(lead)
        clarity = self.analyze_requirement_clarity(lead)
        engagement = self.analyze_activity_engagement(lead)
        
        # Get individual scores - New enhanced factors
        email_quality = self.analyze_email_quality(lead)
        budget = self.analyze_budget_qualification(lead)
        urgency = self.analyze_urgency(lead)
        contact = self.analyze_contact_quality(lead)

        # Get configured weights (cached for performance)
        weights = self._get_scoring_weights()
        
        # Calculate base weighted score (original 3 factors = 70% weight)
        base_weighted = (
            completeness['score'] * weights['completeness'] +
            clarity['score'] * weights['clarity'] +
            engagement['score'] * weights['engagement']
        )
        
        # Calculate enhanced factors bonus (30% weight total)
        # Each enhanced factor can add or subtract from score
        enhanced_score = (
            email_quality['score'] * 0.08 +  # 8% weight
            budget['score'] * 0.10 +          # 10% weight  
            urgency['score'] * 0.07 +         # 7% weight
            contact['score'] * 0.05           # 5% weight
        )
        
        # Final weighted score (capped at 0-100)
        weighted_score = max(0, min(100, (base_weighted * 0.70) + (enhanced_score)))
        
        # Special bonuses
        if contact.get('is_decision_maker'):
            weighted_score = min(100, weighted_score + 5)  # Decision maker bonus
        if urgency.get('urgency_level') == 'high':
            weighted_score = min(100, weighted_score + 5)  # High urgency bonus

        # Use LLM for final analysis and adjustment
        final_analysis_prompt = f"""As a sales expert, provide a final assessment of this lead's conversion probability.

=== CORE METRICS ===
📋 Completeness Score: {completeness['score']}/100
   {completeness['analysis']}

📝 Requirement Clarity Score: {clarity['score']}/100
   {clarity.get('analysis', 'N/A')}

📈 Engagement Score: {engagement['score']}/100
   {engagement['analysis']}

=== ENHANCED METRICS ===
📧 Email Quality Score: {email_quality['score']}/100
   Type: {email_quality.get('email_type', 'unknown')} | {email_quality['analysis']}

💰 Budget Qualification Score: {budget['score']}/100
   Revenue: {budget.get('expected_revenue', 0):,.2f} | {budget['analysis']}

⏰ Urgency Score: {urgency['score']}/100
   Level: {urgency.get('urgency_level', 'normal')} | {urgency['analysis']}

👤 Contact Quality Score: {contact['score']}/100
   Decision Maker: {'YES' if contact.get('is_decision_maker') else 'No'} | {contact['analysis']}

=== CALCULATED SCORE ===
Initial Score: {weighted_score:.1f}/100

Based on ALL these factors, provide:
1. **Final Probability Score** (0-100) with brief justification
2. **Top 3 Strengths** of this lead
3. **Top 3 Concerns/Risks**
4. **Priority Level**: HIGH / MEDIUM / LOW
5. **Recommended Next Actions** (2-3 specific actions)

Be concise and actionable. Consider all 7 scoring dimensions.
"""

        messages = [{'role': 'user', 'content': final_analysis_prompt}]
        llm_result = self.call_llm(messages)

        return {
            'calculated_score': round(weighted_score, 2),
            # Core scores
            'completeness_score': completeness['score'],
            'clarity_score': clarity['score'],
            'engagement_score': engagement['score'],
            # Enhanced scores
            'email_quality_score': email_quality['score'],
            'budget_score': budget['score'],
            'urgency_score': urgency['score'],
            'contact_quality_score': contact['score'],
            # Analysis text
            'completeness_analysis': completeness['analysis'],
            'clarity_analysis': clarity.get('analysis', ''),
            'engagement_analysis': engagement['analysis'],
            'email_analysis': email_quality['analysis'],
            'budget_analysis': budget['analysis'],
            'urgency_analysis': urgency['analysis'],
            'contact_analysis': contact['analysis'],
            # Special flags
            'is_decision_maker': contact.get('is_decision_maker', False),
            'urgency_level': urgency.get('urgency_level', 'normal'),
            'email_type': email_quality.get('email_type', 'unknown'),
            'budget_mentioned': budget.get('budget_mentioned', False),
            # LLM analysis
            'llm_analysis': llm_result['content'] if llm_result['success'] else 'Analysis unavailable',
            'analysis_success': llm_result['success'],
        }
