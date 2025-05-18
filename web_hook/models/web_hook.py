from odoo import models, fields, api
import requests
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        # Trigger when a new invoice is created
        record = super(AccountMove, self).create(vals)
        self._send_webhook(record)
        return record

    def write(self, vals):
        # Trigger when an invoice is updated
        result = super(AccountMove, self).write(vals)
        for record in self:
            if 'invoice_status' in vals or 'state' in vals:
                self._send_webhook(record)
        return result

    def _send_webhook(self, record):
        # Configuration
        ZAPIER_WEBHOOK_URL = 'https://hooks.zapier.com/hooks/catch/22617065/2xcnm2g/'  # Replace with your Zapier webhook URL
        ODOO_API_KEY = '03c98c26862e802a927ddd6e2c1148bc62ac3674'  # Replace with your Odoo API key

        # Prepare data to send
        data = {
            'id': record.id,
            'name': record.name,
            'partner_id': record.partner_id.name,
            'amount_total': record.amount_total,
            'invoice_date': str(record.invoice_date),
            'state': record.state
        }

        # Send webhook request
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer 03c98c26862e802a927ddd6e2c1148bc62ac3674'
            }
            response = requests.post(ZAPIER_WEBHOOK_URL, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                _logger.info(f"Successfully sent webhook for invoice {record.id}")
            else:
                _logger.error(f"Failed to send webhook for invoice {record.id}. Status code: {response.status_code}")
        except Exception as e:
            _logger.error(f"Error sending webhook for invoice {record.id}: {str(e)}")