from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class WebhookController(http.Controller):
    
    @http.route('/webhook/crm/lead', type='json', auth='none', methods=['POST'], csrf=False)
    def webhook_crm_lead(self, **kwargs):
        """Handle webhook for CRM lead creation"""
        try:
            # Get JSON data from request
            webhook_data = request.jsonrequest or {}
            
            # Get source identifier from headers or data
            source_name = request.httprequest.headers.get('X-Webhook-Source')
            if not source_name:
                source_name = webhook_data.get('source', 'default')
            
            _logger.info("Received webhook from source: %s", source_name)
            
            # Create lead from webhook data
            lead = request.env['crm.lead'].sudo().create_from_webhook(webhook_data, source_name)
            
            if lead:
                return {
                    'success': True,
                    'message': 'Lead created successfully',
                    'lead_id': lead.id,
                    'lead_name': lead.name
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create lead'
                }
                
        except Exception as e:
            _logger.error("Webhook error: %s", str(e))
            return {
                'success': False,
                'message': f'Error processing webhook: {str(e)}'
            }
    
    @http.route('/webhook/crm/lead/<string:source>', type='json', auth='none', methods=['POST'], csrf=False)
    def webhook_crm_lead_source(self, source, **kwargs):
        """Handle webhook for CRM lead creation with source in URL"""
        try:
            webhook_data = request.jsonrequest or {}
            
            _logger.info("Received webhook from source: %s", source)
            
            lead = request.env['crm.lead'].sudo().create_from_webhook(webhook_data, source)
            
            if lead:
                return {
                    'success': True,
                    'message': 'Lead created successfully',
                    'lead_id': lead.id,
                    'lead_name': lead.name
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create lead'
                }
                
        except Exception as e:
            _logger.error("Webhook error: %s", str(e))
            return {
                'success': False,
                'message': f'Error processing webhook: {str(e)}'
            }

    @http.route('/webhook/test', type='http', auth='public', methods=['GET'])
    def webhook_test(self):
        """Test endpoint to verify webhook is working"""
        return "Webhook endpoint is active"
