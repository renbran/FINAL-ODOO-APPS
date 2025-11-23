# -*- coding: utf-8 -*-

import json
import logging
import requests
import time
from datetime import datetime

from odoo import models, api, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
        Research customer using LLM to find publicly available information

        Args:
            lead: crm.lead record

        Returns:
            str: Research findings
        """
        # Build research context
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
    def calculate_ai_probability_score(self, lead):
        """
        Calculate overall AI probability score combining all factors

        Returns:
            dict: Complete scoring analysis
        """
        # Get individual scores
        completeness = self.analyze_lead_completeness(lead)
        clarity = self.analyze_requirement_clarity(lead)
        engagement = self.analyze_activity_engagement(lead)

        # Get configured weights (cached for performance)
        weights = self._get_scoring_weights()

        # Weight the scores using configured values
        weighted_score = (
            completeness['score'] * weights['completeness'] +
            clarity['score'] * weights['clarity'] +
            engagement['score'] * weights['engagement']
        )

        # Use LLM for final analysis and adjustment
        final_analysis_prompt = f"""As a sales expert, provide a final assessment of this lead's conversion probability:

Completeness Score: {completeness['score']}/100
- {completeness['analysis']}

Requirement Clarity Score: {clarity['score']}/100
- {clarity['analysis']}

Engagement Score: {engagement['score']}/100
- {engagement['analysis']}

Initial Calculated Score: {weighted_score:.1f}/100

Based on this information, provide:
1. A final probability score (0-100) with brief justification
2. Top 2-3 strengths of this lead
3. Top 2-3 concerns or weaknesses
4. Recommended next actions

Keep your response concise and actionable.
"""

        messages = [{'role': 'user', 'content': final_analysis_prompt}]
        llm_result = self.call_llm(messages)

        return {
            'calculated_score': round(weighted_score, 2),
            'completeness_score': completeness['score'],
            'clarity_score': clarity['score'],
            'engagement_score': engagement['score'],
            'completeness_analysis': completeness['analysis'],
            'clarity_analysis': clarity.get('analysis', ''),
            'engagement_analysis': engagement['analysis'],
            'llm_analysis': llm_result['content'] if llm_result['success'] else 'Analysis unavailable',
            'analysis_success': llm_result['success'],
        }
