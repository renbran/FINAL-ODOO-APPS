from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Deal tracking fields
    booking_date = fields.Date(string='Booking Date', tracking=True)
    developer_commission = fields.Float(string='Developer Commission', tracking=True, digits=(16, 2))
    buyer_id = fields.Many2one('res.partner', string='Buyer', tracking=True)
    deal_id = fields.Integer(string='Deal ID', tracking=True)
    project_id = fields.Many2one('product.template', string='Project', tracking=True)
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id')
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True)

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    @api.model
    def _sanitize_vals(self, vals):
        """Ensure all Many2one fields have valid values or False"""
        safe_vals = vals.copy()
        
        # List of all Many2one fields in the model
        m2o_fields = {
            'buyer_id': 'res.partner',
            'project_id': 'product.template',
            'unit_id': 'product.product'
        }
        
        for field_name, model_name in m2o_fields.items():
            if field_name in safe_vals:
                value = safe_vals[field_name]
                
                # Handle empty/False values
                if not value:
                    safe_vals[field_name] = False
                    continue
                
                # Handle record IDs
                if isinstance(value, int):
                    if not self.env[model_name].browse(value).exists():
                        _logger.warning("Invalid reference for %s: %s", field_name, value)
                        safe_vals[field_name] = False
                
                # Handle recordset objects
                elif hasattr(value, '_name') and value._name == model_name:
                    if not value.exists():
                        safe_vals[field_name] = False
                    else:
                        safe_vals[field_name] = value.id
                
                # Handle unknown objects
                elif not isinstance(value, (int, float, bool)):
                    _logger.warning("Invalid type for %s: %s", field_name, type(value))
                    safe_vals[field_name] = False
        
        return safe_vals

    @api.model_create_multi
    def create(self, vals_list):
        """Override create with proper field sanitization"""
        sanitized_vals = []
        
        for vals in vals_list:
            # First sanitize the input values
            safe_vals = self._sanitize_vals(vals)
            
            # Handle sale order field transfer
            if safe_vals.get('move_type') in ('out_invoice', 'out_refund') and safe_vals.get('invoice_origin'):
                try:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', safe_vals['invoice_origin'])
                    ], limit=1)
                    
                    if sale_order:
                        transfer_fields = [
                            'booking_date',
                            'developer_commission',
                            'buyer_id',
                            'deal_id',
                            'project_id',
                            'sale_value',
                            'unit_id'
                        ]
                        
                        for field in transfer_fields:
                            if field not in safe_vals:
                                value = getattr(sale_order, field)
                                if field.endswith('_id'):
                                    if value and value.exists():
                                        safe_vals[field] = value.id
                                elif value:
                                    safe_vals[field] = value
                except Exception as e:
                    _logger.error("Error transferring sale order fields: %s", str(e))
            
            sanitized_vals.append(safe_vals)
        
        return super(AccountMove, self).create(sanitized_vals)

    def write(self, vals):
        """Override write with proper field sanitization"""
        safe_vals = self._sanitize_vals(vals)
        return super(AccountMove, self).write(safe_vals)

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        """Convert amount total to words"""
        for record in self:
            if record.amount_total:
                try:
                    from num2words import num2words
                    amount = record.amount_total
                    currency = record.currency_id.name or 'USD'
                    record.amount_total_words = num2words(amount, lang='en').title() + ' ' + currency
                except ImportError:
                    record.amount_total_words = str(record.amount_total) + ' ' + (record.currency_id.name or 'USD')
            else:
                record.amount_total_words = ''