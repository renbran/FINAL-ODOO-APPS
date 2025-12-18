# -*- coding: utf-8 -*-

import json
import logging
import re
import requests
from datetime import datetime
from urllib.parse import urlparse, quote_plus

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Technology detection patterns
TECH_PATTERNS = {
    'cms': {
        'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
        'shopify': ['shopify', 'myshopify.com'],
        'wix': ['wix.com', 'wixsite'],
        'squarespace': ['squarespace'],
        'drupal': ['drupal'],
        'joomla': ['joomla'],
        'magento': ['magento', 'mage'],
        'webflow': ['webflow'],
    },
    'analytics': {
        'google_analytics': ['google-analytics', 'gtag', 'ga.js', 'analytics.js'],
        'facebook_pixel': ['facebook.com/tr', 'fbq('],
        'hotjar': ['hotjar'],
        'mixpanel': ['mixpanel'],
    },
    'marketing': {
        'hubspot': ['hubspot', 'hs-scripts'],
        'mailchimp': ['mailchimp'],
        'intercom': ['intercom'],
        'zendesk': ['zendesk'],
        'drift': ['drift'],
        'crisp': ['crisp.chat'],
    },
    'ecommerce': {
        'stripe': ['stripe.com', 'js.stripe'],
        'paypal': ['paypal'],
        'square': ['squareup'],
    },
    'infrastructure': {
        'cloudflare': ['cloudflare'],
        'aws': ['amazonaws.com', 'aws'],
        'google_cloud': ['googleapis', 'gstatic'],
        'azure': ['azure', 'microsoft'],
    }
}

# Social media platforms to check
SOCIAL_PLATFORMS = {
    'linkedin': 'linkedin.com/company/',
    'facebook': 'facebook.com/',
    'twitter': 'twitter.com/',
    'instagram': 'instagram.com/',
    'youtube': 'youtube.com/',
}


class WebResearchService(models.AbstractModel):
    _name = 'web.research.service'
    _description = 'Web Research Service with Google Custom Search'

    @api.model
    def search_google_custom(self, query, num_results=5):
        """
        Search using Google Custom Search API
        
        Free Tier: 100 queries/day
        Paid: $5 per 1000 queries after free tier
        
        Args:
            query: Search query string
            num_results: Number of results (1-10, default 5)
            
        Returns:
            dict: {'success': bool, 'results': list, 'error': str}
        """
        config = self.env['ir.config_parameter'].sudo()
        api_key = config.get_param('llm_lead_scoring.google_search_api_key', '').strip()
        search_engine_id = config.get_param('llm_lead_scoring.google_search_engine_id', '').strip()
        
        if not api_key or not search_engine_id:
            return {
                'success': False,
                'error': 'Google Custom Search not configured. Please add API key and Search Engine ID in Settings → CRM → LLM Lead Scoring.',
                'results': []
            }
        
        # Validate Search Engine ID format (should not be an API key)
        if search_engine_id.startswith('AIza'):
            return {
                'success': False,
                'error': 'Invalid Search Engine ID - you entered an API key. Please use the Search Engine ID from Programmable Search Engine.',
                'results': []
            }
        
        # Validate query is not empty
        if not query or len(query.strip()) < 3:
            return {
                'success': False,
                'error': 'Search query is too short or empty.',
                'results': []
            }
        
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query.strip(),
            'num': min(num_results, 10)  # Max 10 per request
        }
        
        try:
            _logger.info("Google Custom Search: %s", query)
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    return {
                        'success': True,
                        'results': [],
                        'message': 'No results found'
                    }
                
                results = []
                for item in items:
                    results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'displayLink': item.get('displayLink', ''),
                    })
                
                _logger.info("Found %d results for query: %s", len(results), query)
                return {
                    'success': True,
                    'results': results,
                    'query_count': len(results)
                }
            
            elif response.status_code == 429:
                return {
                    'success': False,
                    'error': 'Google Custom Search API quota exceeded. Free tier: 100 queries/day.',
                    'results': []
                }
            
            elif response.status_code == 400:
                error_detail = response.json().get('error', {}).get('message', 'Invalid request')
                return {
                    'success': False,
                    'error': f'Google API Error: {error_detail}',
                    'results': []
                }
            
            elif response.status_code == 403:
                return {
                    'success': False,
                    'error': 'Google API authentication failed. Check your API key in Settings.',
                    'results': []
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Google API returned status {response.status_code}: {response.text[:200]}',
                    'results': []
                }
                
        except requests.exceptions.Timeout:
            _logger.warning("Google Custom Search timeout for query: %s", query)
            return {
                'success': False,
                'error': 'Search request timeout (10 seconds)',
                'results': []
            }
        
        except requests.exceptions.ConnectionError as e:
            _logger.error("Google Custom Search connection error: %s", str(e))
            return {
                'success': False,
                'error': f'Connection error: {str(e)[:100]}',
                'results': []
            }
        
        except Exception as e:
            _logger.error("Google Custom Search unexpected error: %s", str(e), exc_info=True)
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)[:100]}',
                'results': []
            }

    @api.model
    def research_company_web(self, lead):
        """
        Enhanced company research using live web search + LLM synthesis
        
        Process:
        1. Extract company info from lead
        2. Perform Google searches (2-3 queries)
        3. Use LLM to synthesize findings
        4. Return structured research report
        
        Args:
            lead: crm.lead record
            
        Returns:
            str: Research report (HTML formatted)
        """
        # Extract lead information
        company_name = lead.partner_name or lead.contact_name or ''
        website = lead.website or ''
        email_domain = lead.email_from.split('@')[1] if lead.email_from and '@' in lead.email_from else ''
        
        # Check if web research is enabled
        config = self.env['ir.config_parameter'].sudo()
        web_research_enabled = config.get_param('llm_lead_scoring.enable_web_research', 'False') == 'True'
        
        if not web_research_enabled:
            return "⚠️ Web research is disabled. Enable it in Settings → CRM → LLM Lead Scoring to get real-time company data."
        
        # Skip web research if no meaningful company identifier
        if not company_name or len(company_name.strip()) < 3:
            if not website and not email_domain:
                return "ℹ️ Web research skipped - no company name, website, or email domain provided in lead. Add company information to enable live web research."
            # If we have website/email but no name, use domain as company name
            if email_domain and not company_name:
                company_name = email_domain.replace('.com', '').replace('.', ' ').title()
        
        # Build search queries (limit to save quota)
        queries = []
        
        # Query 1: Company profile (only if we have a valid name)
        if company_name and len(company_name.strip()) >= 3:
            queries.append(f'"{company_name.strip()}" company profile about')
        
        # Query 2: Recent news (if we have good company name)
        if company_name and len(company_name.strip()) > 3:
            queries.append(f'"{company_name.strip()}" news recent 2024 2025')
        
        # Query 3: Site-specific (if website provided)
        if website:
            domain = website.replace('http://', '').replace('https://', '').split('/')[0]
            queries.append(f'site:{domain} about products services')
        
        # Perform searches (max 3 to stay within free tier)
        all_results = []
        search_summary = []
        
        for i, query in enumerate(queries[:3], 1):  # Limit to 3 searches = 3/100 daily quota
            search_result = self.search_google_custom(query, num_results=3)
            
            if search_result['success']:
                results = search_result['results']
                all_results.extend(results)
                search_summary.append(f"Query {i}: Found {len(results)} results")
                _logger.info("Search %d/%d successful: %d results", i, len(queries), len(results))
            else:
                error_msg = search_result.get('error', 'Unknown error')
                search_summary.append(f"Query {i}: Failed - {error_msg}")
                _logger.warning("Search %d/%d failed: %s", i, len(queries), error_msg)
        
        if not all_results:
            return f"""WEB RESEARCH ATTEMPTED:
{chr(10).join(['   ' + s for s in search_summary])}

No web results available. This may be due to API quota limits (100/day free tier) or the company may not have a strong online presence."""
        
        # Format search results for LLM
        context_parts = []
        for idx, result in enumerate(all_results[:8], 1):  # Limit to 8 best results
            context_parts.append(f"""
**Result {idx}: {result['title']}**
{result['snippet']}
Source: {result['link']}
            """.strip())
        
        web_context = "\n\n".join(context_parts)
        
        # Use LLM to synthesize findings
        llm_service = self.env['llm.service']
        synthesis_prompt = f"""Based on these recent Google search results about "{company_name}", provide a concise company research report.

Company Details:
- Name: {company_name}
- Website: {website if website else 'Not provided'}
- Email Domain: {email_domain if email_domain else 'Not provided'}

Web Search Results ({len(all_results)} found):
{web_context}

Please provide a structured report with:
1. **Company Overview**: Industry, business type, main activities
2. **Company Size & Presence**: Estimated size, locations, market presence (if available)
3. **Products/Services**: Key offerings mentioned
4. **Recent Developments**: Any recent news, funding, launches (if found)
5. **Business Credibility**: Professional website, media mentions, legitimacy indicators
6. **Buying Signals**: Any indicators of growth, expansion, or needs that match our offerings

IMPORTANT: 
- Only include factual information from the search results
- If information is not available in results, clearly state "Not found in available sources"
- Keep the report concise (200-300 words)
- Use bullet points for clarity
"""
        
        messages = [{'role': 'user', 'content': synthesis_prompt}]
        result = llm_service.call_llm(messages)
        
        if result['success']:
            llm_analysis = result['content']
        else:
            llm_analysis = f"LLM synthesis failed: {result['error']}"
        
        # Format final report (Plain Text)
        # Remove markdown formatting from LLM analysis
        clean_analysis = llm_analysis.replace('**', '').replace('*', '')
        
        # Build source list
        source_list = '\n'.join([f'   • {r["displayLink"]}: {r["link"][:60]}...' for r in all_results[:3]])
        
        report = f"""
🌐 LIVE WEB RESEARCH RESULTS

SEARCH SUMMARY:
{chr(10).join(['   ' + s for s in search_summary])}
   Total: {len(all_results)} web results analyzed

ANALYSIS:
{clean_analysis}

TOP SOURCES:
{source_list}
        """.strip()
        
        return report

    @api.model
    def get_daily_quota_usage(self):
        """
        Estimate daily quota usage (approximation)
        Google doesn't provide real-time quota API, so we track in Odoo
        
        Returns:
            dict: {'used': int, 'limit': int, 'remaining': int}
        """
        config = self.env['ir.config_parameter'].sudo()
        
        # Get today's usage count (stored as config parameter)
        today = fields.Date.today().isoformat()
        usage_key = f'llm_lead_scoring.google_search_usage_{today}'
        used_today = int(config.get_param(usage_key, '0'))
        
        # Free tier limit
        daily_limit = 100
        
        return {
            'used': used_today,
            'limit': daily_limit,
            'remaining': max(0, daily_limit - used_today),
            'date': today
        }

    @api.model
    def increment_quota_usage(self, count=1):
        """
        Increment daily quota usage counter
        
        Args:
            count: Number of queries to add (default 1)
        """
        config = self.env['ir.config_parameter'].sudo()
        today = fields.Date.today().isoformat()
        usage_key = f'llm_lead_scoring.google_search_usage_{today}'
        
        current = int(config.get_param(usage_key, '0'))
        new_value = current + count
        
        config.set_param(usage_key, str(new_value))
        
        if new_value >= 90:  # Warning at 90% usage
            _logger.warning("Google Custom Search quota at %d/100 today", new_value)

    # =========================================================================
    # ENHANCED RESEARCH: Google Maps, Digital Presence, Tech Infrastructure
    # =========================================================================

    @api.model
    def search_google_maps(self, company_name, location=None):
        """
        Search Google Maps Places API for business information
        
        Retrieves:
        - Business address & location
        - Ratings & reviews count
        - Business hours
        - Phone number
        - Website
        - Business category
        - Photos count
        
        Args:
            company_name: Company name to search
            location: Optional location hint (city, country)
            
        Returns:
            dict: Google Maps business data
        """
        config = self.env['ir.config_parameter'].sudo()
        maps_api_key = config.get_param('llm_lead_scoring.google_maps_api_key', '')
        
        if not maps_api_key:
            return {
                'success': False,
                'error': 'Google Maps API key not configured',
                'data': None
            }
        
        # Build search query
        search_query = company_name
        if location:
            search_query = f"{company_name} {location}"
        
        try:
            # Step 1: Find Place from Text
            find_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            find_params = {
                'input': search_query,
                'inputtype': 'textquery',
                'fields': 'place_id,name,formatted_address,business_status',
                'key': maps_api_key
            }
            
            response = requests.get(find_url, params=find_params, timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Maps API error: {response.status_code}',
                    'data': None
                }
            
            find_data = response.json()
            
            if find_data.get('status') != 'OK' or not find_data.get('candidates'):
                return {
                    'success': False,
                    'error': 'No business found on Google Maps',
                    'data': None
                }
            
            place_id = find_data['candidates'][0]['place_id']
            
            # Step 2: Get Place Details
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,international_phone_number,website,url,rating,user_ratings_total,reviews,opening_hours,business_status,types,photos',
                'key': maps_api_key
            }
            
            details_response = requests.get(details_url, params=details_params, timeout=10)
            
            if details_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Place details error: {details_response.status_code}',
                    'data': None
                }
            
            details_data = details_response.json()
            
            if details_data.get('status') != 'OK':
                return {
                    'success': False,
                    'error': f'Place details failed: {details_data.get("status")}',
                    'data': None
                }
            
            place = details_data.get('result', {})
            
            # Extract business data
            business_data = {
                'name': place.get('name', ''),
                'address': place.get('formatted_address', ''),
                'phone': place.get('formatted_phone_number', ''),
                'international_phone': place.get('international_phone_number', ''),
                'website': place.get('website', ''),
                'maps_url': place.get('url', ''),
                'rating': place.get('rating', 0),
                'reviews_count': place.get('user_ratings_total', 0),
                'business_status': place.get('business_status', 'UNKNOWN'),
                'business_types': place.get('types', []),
                'photos_count': len(place.get('photos', [])),
                'is_operational': place.get('business_status') == 'OPERATIONAL',
                'has_opening_hours': 'opening_hours' in place,
            }
            
            # Calculate business credibility score from Maps data
            credibility_score = 0
            if business_data['rating'] >= 4.0:
                credibility_score += 25
            elif business_data['rating'] >= 3.0:
                credibility_score += 15
            
            if business_data['reviews_count'] >= 100:
                credibility_score += 25
            elif business_data['reviews_count'] >= 20:
                credibility_score += 15
            elif business_data['reviews_count'] >= 5:
                credibility_score += 10
            
            if business_data['is_operational']:
                credibility_score += 20
            
            if business_data['has_opening_hours']:
                credibility_score += 10
            
            if business_data['photos_count'] >= 5:
                credibility_score += 10
            
            if business_data['website']:
                credibility_score += 10
            
            business_data['credibility_score'] = min(100, credibility_score)
            
            _logger.info("Google Maps found: %s - Rating: %.1f (%d reviews)",
                         business_data['name'], business_data['rating'], business_data['reviews_count'])
            
            return {
                'success': True,
                'error': None,
                'data': business_data
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Google Maps API timeout',
                'data': None
            }
        except Exception as e:
            _logger.error("Google Maps search error: %s", str(e), exc_info=True)
            return {
                'success': False,
                'error': f'Maps error: {str(e)[:100]}',
                'data': None
            }

    @api.model
    def analyze_website_technology(self, website_url):
        """
        Analyze website to detect technology stack
        
        Detects:
        - CMS (WordPress, Shopify, Wix, etc.)
        - Analytics (Google Analytics, etc.)
        - Marketing tools (HubSpot, etc.)
        - E-commerce platforms
        - Infrastructure (Cloudflare, AWS, etc.)
        
        Args:
            website_url: Website URL to analyze
            
        Returns:
            dict: Technology stack analysis
        """
        if not website_url:
            return {
                'success': False,
                'error': 'No website URL provided',
                'data': None
            }
        
        # Normalize URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = f'https://{website_url}'
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(website_url, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Website returned status {response.status_code}',
                    'data': None
                }
            
            html_content = response.text.lower()
            response_headers = {k.lower(): v for k, v in response.headers.items()}
            
            # Detected technologies
            detected = {
                'cms': [],
                'analytics': [],
                'marketing': [],
                'ecommerce': [],
                'infrastructure': [],
                'frameworks': [],
                'other': []
            }
            
            # Check HTML content against patterns
            for category, tools in TECH_PATTERNS.items():
                for tool_name, patterns in tools.items():
                    for pattern in patterns:
                        if pattern.lower() in html_content:
                            if tool_name not in detected.get(category, []):
                                detected[category].append(tool_name)
                            break
            
            # Check response headers for infrastructure
            if 'cf-ray' in response_headers or 'cf-cache-status' in response_headers:
                if 'cloudflare' not in detected['infrastructure']:
                    detected['infrastructure'].append('cloudflare')
            
            if 'x-amz-' in str(response_headers):
                if 'aws' not in detected['infrastructure']:
                    detected['infrastructure'].append('aws')
            
            server_header = response_headers.get('server', '').lower()
            if 'nginx' in server_header:
                detected['infrastructure'].append('nginx')
            elif 'apache' in server_header:
                detected['infrastructure'].append('apache')
            
            # Calculate tech sophistication score
            tech_score = 0
            
            # CMS quality scoring
            if 'wordpress' in detected['cms']:
                tech_score += 10  # Common but legitimate
            if 'shopify' in detected['cms']:
                tech_score += 15  # E-commerce focused
            if 'hubspot_cms' in detected['cms']:
                tech_score += 20  # Enterprise marketing
            
            # Analytics = data-driven
            if detected['analytics']:
                tech_score += 15
            
            # Marketing tools = serious about leads
            if detected['marketing']:
                tech_score += 20
            
            # E-commerce = transactional business
            if detected['ecommerce']:
                tech_score += 15
            
            # CDN/Infrastructure = professional setup
            if 'cloudflare' in detected['infrastructure']:
                tech_score += 10
            if 'aws' in detected['infrastructure'] or 'azure' in detected['infrastructure']:
                tech_score += 15
            
            # Multiple technologies = sophisticated
            total_tech_count = sum(len(v) for v in detected.values())
            if total_tech_count >= 5:
                tech_score += 15
            elif total_tech_count >= 3:
                tech_score += 10
            
            # Check for SSL/HTTPS
            is_https = website_url.startswith('https://')
            if is_https:
                tech_score += 10
            
            tech_data = {
                'url': website_url,
                'is_accessible': True,
                'is_https': is_https,
                'detected_technologies': detected,
                'total_tech_count': total_tech_count,
                'tech_sophistication_score': min(100, tech_score),
                'has_analytics': bool(detected['analytics']),
                'has_marketing_tools': bool(detected['marketing']),
                'has_ecommerce': bool(detected['ecommerce']),
                'primary_cms': detected['cms'][0] if detected['cms'] else None,
            }
            
            _logger.info("Tech analysis for %s: %d technologies detected, score: %d",
                         website_url, total_tech_count, tech_score)
            
            return {
                'success': True,
                'error': None,
                'data': tech_data
            }
            
        except requests.exceptions.SSLError:
            return {
                'success': False,
                'error': 'SSL certificate error',
                'data': {'is_https': False, 'ssl_error': True}
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Website timeout (15s)',
                'data': None
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Website unreachable',
                'data': {'is_accessible': False}
            }
        except Exception as e:
            _logger.error("Tech analysis error for %s: %s", website_url, str(e))
            return {
                'success': False,
                'error': f'Analysis error: {str(e)[:100]}',
                'data': None
            }

    @api.model
    def analyze_digital_presence(self, company_name, website=None, email_domain=None):
        """
        Analyze company's digital presence across platforms
        
        Checks:
        - Social media presence (LinkedIn, Facebook, Twitter, etc.)
        - Website existence and quality
        - Domain age indicators
        - Online visibility score
        
        Args:
            company_name: Company name
            website: Optional website URL
            email_domain: Optional email domain
            
        Returns:
            dict: Digital presence analysis
        """
        presence_data = {
            'platforms_found': [],
            'platforms_not_found': [],
            'estimated_presence_score': 0,
            'linkedin_found': False,
            'website_active': False,
            'social_signals': []
        }
        
        # Search for social media presence using Google
        search_queries = []
        
        # LinkedIn search
        if company_name:
            search_queries.append({
                'platform': 'linkedin',
                'query': f'site:linkedin.com/company "{company_name}"'
            })
            
            # Facebook search
            search_queries.append({
                'platform': 'facebook',
                'query': f'site:facebook.com "{company_name}" page'
            })
        
        # Perform limited searches (to save quota)
        for sq in search_queries[:2]:  # Only 2 searches to conserve quota
            result = self.search_google_custom(sq['query'], num_results=1)
            
            if result['success'] and result['results']:
                presence_data['platforms_found'].append(sq['platform'])
                presence_data['social_signals'].append({
                    'platform': sq['platform'],
                    'url': result['results'][0]['link'],
                    'title': result['results'][0]['title']
                })
                
                if sq['platform'] == 'linkedin':
                    presence_data['linkedin_found'] = True
            else:
                presence_data['platforms_not_found'].append(sq['platform'])
        
        # Check website if provided
        if website:
            try:
                url = website if website.startswith('http') else f'https://{website}'
                response = requests.head(url, timeout=5, allow_redirects=True)
                presence_data['website_active'] = response.status_code == 200
            except:
                presence_data['website_active'] = False
        
        # Calculate presence score
        score = 0
        
        # LinkedIn presence is important for B2B
        if presence_data['linkedin_found']:
            score += 30
        
        # Other social platforms
        other_platforms = [p for p in presence_data['platforms_found'] if p != 'linkedin']
        score += len(other_platforms) * 15
        
        # Active website
        if presence_data['website_active']:
            score += 25
        
        # Has custom email domain (not gmail/yahoo/etc.)
        if email_domain and email_domain.lower() not in [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
        ]:
            score += 20
        
        presence_data['estimated_presence_score'] = min(100, score)
        
        _logger.info("Digital presence for %s: Score %d, LinkedIn: %s, Platforms: %s",
                     company_name, score, presence_data['linkedin_found'],
                     presence_data['platforms_found'])
        
        return {
            'success': True,
            'data': presence_data
        }

    @api.model
    def get_enhanced_company_research(self, lead):
        """
        Comprehensive company research combining all sources
        
        Integrates:
        - Google Search results
        - Google Maps business data
        - Website technology analysis
        - Digital presence check
        
        Args:
            lead: crm.lead record
            
        Returns:
            dict: Complete research data
        """
        company_name = lead.partner_name or lead.contact_name or ''
        website = lead.website or ''
        email = lead.email_from or ''
        email_domain = email.split('@')[1] if '@' in email else ''
        country = lead.country_id.name if lead.country_id else ''
        city = lead.city or ''
        location = f"{city}, {country}".strip(', ') if city or country else None
        
        research_data = {
            'company_name': company_name,
            'web_search': None,
            'google_maps': None,
            'tech_stack': None,
            'digital_presence': None,
            'combined_credibility_score': 0,
            'research_summary': []
        }
        
        # 1. Google Search (existing method)
        # Note: research_company_web already handles this
        
        # 2. Google Maps lookup
        if company_name:
            maps_result = self.search_google_maps(company_name, location)
            if maps_result['success']:
                research_data['google_maps'] = maps_result['data']
                research_data['research_summary'].append(
                    f"📍 Google Maps: {maps_result['data']['rating']}/5 stars ({maps_result['data']['reviews_count']} reviews)"
                )
        
        # 3. Website technology analysis
        if website:
            tech_result = self.analyze_website_technology(website)
            if tech_result['success']:
                research_data['tech_stack'] = tech_result['data']
                tech_count = tech_result['data']['total_tech_count']
                research_data['research_summary'].append(
                    f"🔧 Tech Stack: {tech_count} technologies detected"
                )
        
        # 4. Digital presence check
        if company_name:
            presence_result = self.analyze_digital_presence(company_name, website, email_domain)
            if presence_result['success']:
                research_data['digital_presence'] = presence_result['data']
                platforms = presence_result['data']['platforms_found']
                research_data['research_summary'].append(
                    f"🌐 Digital Presence: Found on {', '.join(platforms) if platforms else 'limited platforms'}"
                )
        
        # Calculate combined credibility score
        scores = []
        
        if research_data['google_maps']:
            scores.append(research_data['google_maps'].get('credibility_score', 0))
        
        if research_data['tech_stack']:
            scores.append(research_data['tech_stack'].get('tech_sophistication_score', 0))
        
        if research_data['digital_presence']:
            scores.append(research_data['digital_presence'].get('estimated_presence_score', 0))
        
        if scores:
            research_data['combined_credibility_score'] = sum(scores) // len(scores)
        
        return research_data
