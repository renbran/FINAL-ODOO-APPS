# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
