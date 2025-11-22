# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LLMProvider(models.Model):
    _name = 'llm.provider'
    _description = 'LLM Provider Configuration'
    _order = 'sequence, name'

    name = fields.Char(string='Provider Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    provider_type = fields.Selection([
        ('openai', 'OpenAI'),
        ('groq', 'Groq'),
        ('huggingface', 'HuggingFace'),
        ('anthropic', 'Anthropic (Claude)'),
        ('google', 'Google (Gemini)'),
        ('cohere', 'Cohere'),
        ('mistral', 'Mistral AI'),
        ('custom', 'Custom API'),
    ], string='Provider Type', required=True)

    api_key = fields.Char(string='API Key', required=True)
    api_endpoint = fields.Char(string='API Endpoint', help='Custom API endpoint URL (for custom providers)')
    model_name = fields.Char(string='Model Name', required=True,
                             help='e.g., gpt-4, llama-3.1-70b, claude-3-sonnet')

    active = fields.Boolean(string='Active', default=True)
    is_default = fields.Boolean(string='Default Provider', default=False)

    # Provider Parameters
    temperature = fields.Float(string='Temperature', default=0.7,
                              help='Controls randomness (0.0 to 1.0)')
    max_tokens = fields.Integer(string='Max Tokens', default=2000,
                                help='Maximum tokens in response')
    timeout = fields.Integer(string='Timeout (seconds)', default=30)

    # Usage tracking
    total_requests = fields.Integer(string='Total Requests', readonly=True, default=0)
    failed_requests = fields.Integer(string='Failed Requests', readonly=True, default=0)
    last_used = fields.Datetime(string='Last Used', readonly=True)

    # Configuration
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('is_default')
    def _check_default_provider(self):
        """Ensure only one default provider exists"""
        for record in self:
            if record.is_default:
                other_defaults = self.search([
                    ('is_default', '=', True),
                    ('id', '!=', record.id),
                    ('company_id', '=', record.company_id.id)
                ])
                if other_defaults:
                    raise ValidationError(_('Only one default LLM provider is allowed per company.'))

    @api.model
    def get_default_provider(self):
        """Get the default LLM provider"""
        provider = self.search([
            ('is_default', '=', True),
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if not provider:
            # Fallback to first active provider
            provider = self.search([
                ('active', '=', True),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

        return provider

    def get_api_headers(self):
        """Get API headers for the provider"""
        self.ensure_one()

        headers = {
            'Content-Type': 'application/json',
        }

        if self.provider_type == 'openai':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.provider_type == 'anthropic':
            headers['x-api-key'] = self.api_key
            headers['anthropic-version'] = '2023-06-01'
        elif self.provider_type == 'groq':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.provider_type == 'huggingface':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.provider_type == 'google':
            # Google uses API key in URL params
            pass
        elif self.provider_type == 'cohere':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.provider_type == 'mistral':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.provider_type == 'custom':
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers

    def get_api_url(self):
        """Get API URL for the provider"""
        self.ensure_one()

        if self.api_endpoint:
            return self.api_endpoint

        urls = {
            'openai': 'https://api.openai.com/v1/chat/completions',
            'groq': 'https://api.groq.com/openai/v1/chat/completions',
            'anthropic': 'https://api.anthropic.com/v1/messages',
            'huggingface': 'https://api-inference.huggingface.co/models/' + (self.model_name or ''),
            'google': f'https://generativelanguage.googleapis.com/v1/models/{self.model_name}:generateContent?key={self.api_key}',
            'cohere': 'https://api.cohere.ai/v1/generate',
            'mistral': 'https://api.mistral.ai/v1/chat/completions',
        }

        return urls.get(self.provider_type, '')

    def format_request_payload(self, messages, system_prompt=None):
        """Format request payload based on provider type"""
        self.ensure_one()

        if self.provider_type in ['openai', 'groq', 'mistral']:
            payload = {
                'model': self.model_name,
                'messages': messages,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
            }
            if system_prompt:
                payload['messages'].insert(0, {'role': 'system', 'content': system_prompt})

        elif self.provider_type == 'anthropic':
            payload = {
                'model': self.model_name,
                'messages': messages,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
            }
            if system_prompt:
                payload['system'] = system_prompt

        elif self.provider_type == 'huggingface':
            # HuggingFace typically uses a simpler format
            prompt = '\n'.join([msg.get('content', '') for msg in messages])
            if system_prompt:
                prompt = f"{system_prompt}\n\n{prompt}"
            payload = {
                'inputs': prompt,
                'parameters': {
                    'temperature': self.temperature,
                    'max_new_tokens': self.max_tokens,
                }
            }

        elif self.provider_type == 'google':
            # Google Gemini format
            contents = []
            for msg in messages:
                contents.append({
                    'parts': [{'text': msg.get('content', '')}]
                })
            payload = {
                'contents': contents,
                'generationConfig': {
                    'temperature': self.temperature,
                    'maxOutputTokens': self.max_tokens,
                }
            }

        elif self.provider_type == 'cohere':
            prompt = '\n'.join([msg.get('content', '') for msg in messages])
            if system_prompt:
                prompt = f"{system_prompt}\n\n{prompt}"
            payload = {
                'model': self.model_name,
                'prompt': prompt,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
            }

        else:
            # Default format (OpenAI-compatible)
            payload = {
                'model': self.model_name,
                'messages': messages,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
            }

        return payload

    def parse_response(self, response_json):
        """Parse response based on provider type"""
        self.ensure_one()

        try:
            if self.provider_type in ['openai', 'groq', 'mistral']:
                return response_json.get('choices', [{}])[0].get('message', {}).get('content', '')

            elif self.provider_type == 'anthropic':
                return response_json.get('content', [{}])[0].get('text', '')

            elif self.provider_type == 'huggingface':
                # HuggingFace can return different formats
                if isinstance(response_json, list):
                    return response_json[0].get('generated_text', '')
                return response_json.get('generated_text', '')

            elif self.provider_type == 'google':
                candidates = response_json.get('candidates', [])
                if candidates:
                    return candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')

            elif self.provider_type == 'cohere':
                generations = response_json.get('generations', [])
                if generations:
                    return generations[0].get('text', '')

            else:
                # Try common response formats
                if 'choices' in response_json:
                    return response_json['choices'][0].get('message', {}).get('content', '')
                elif 'content' in response_json:
                    return response_json['content']
                elif 'text' in response_json:
                    return response_json['text']

        except (KeyError, IndexError, TypeError) as e:
            return f"Error parsing response: {str(e)}"

        return "Unable to parse LLM response"

    def increment_usage(self, success=True):
        """Increment usage statistics"""
        self.ensure_one()
        self.write({
            'total_requests': self.total_requests + 1,
            'failed_requests': self.failed_requests + (0 if success else 1),
            'last_used': fields.Datetime.now(),
        })
