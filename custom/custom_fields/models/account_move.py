from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Add the mixin fields directly to avoid inheritance issues
    booking_date = fields.Date(string='Booking Date', tracking=True)
    developer_commission = fields.Float(string='Broker Commission', tracking=True, digits=(16, 2))
    buyer_id = fields.Many2one('res.partner', string='Buyer', tracking=True)
    deal_id = fields.Integer(string='Deal ID', tracking=True)
    project_id = fields.Many2one('product.template', string='Project Name', tracking=True)
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id')
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True)

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    @api.model
    def create(self, vals_list):
        """Simplified create method with extensive logging"""
        _logger.info("AccountMove.create called with vals_list: %s", vals_list)
        
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
            single_record = True
        else:
            single_record = False
        
        # Process each vals dict
        processed_vals_list = []
        for i, vals in enumerate(vals_list):
            _logger.info("Processing vals[%d]: %s", i, vals)
            
            # Create a new dict with only safe values
            safe_vals = {}
            
            # Copy standard fields
            for key, value in vals.items():
                if key not in self._fields:
                    safe_vals[key] = value
                    continue
                
                field = self._fields[key]
                
                # Handle Many2one fields with extra safety
                if isinstance(field, fields.Many2one):
                    if not value:
                        safe_vals[key] = False
                    elif isinstance(value, int) and value > 0:
                        try:
                            # Check if record exists
                            if self.env[field.comodel_name].browse(value).exists():
                                safe_vals[key] = value
                            else:
                                _logger.warning("Many2one field %s: record ID %d does not exist", key, value)
                                safe_vals[key] = False
                        except Exception as e:
                            _logger.error("Error validating Many2one field %s with value %s: %s", key, value, e)
                            safe_vals[key] = False
                    else:
                        _logger.warning("Many2one field %s: invalid value type %s", key, type(value))
                        safe_vals[key] = False
                else:
                    # For non-Many2one fields, copy as-is
                    safe_vals[key] = value
            
            # Transfer sale order fields only if it's an invoice
            if safe_vals.get('move_type') in ['out_invoice', 'out_refund'] and safe_vals.get('invoice_origin'):
                try:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', safe_vals.get('invoice_origin'))
                    ], limit=1)
                    
                    if sale_order:
                        _logger.info("Found sale order %s, transferring fields", sale_order.name)
                        
                        # Transfer fields safely
                        transfer_fields = {
                            'booking_date': sale_order.booking_date,
                            'developer_commission': sale_order.developer_commission,
                            'deal_id': sale_order.deal_id,
                            'sale_value': sale_order.sale_value,
                        }
                        
                        # Handle Many2one fields with existence checks
                        if sale_order.buyer_id and sale_order.buyer_id.exists():
                            transfer_fields['buyer_id'] = sale_order.buyer_id.id
                        
                        if sale_order.project_id and sale_order.project_id.exists():
                            transfer_fields['project_id'] = sale_order.project_id.id
                        
                        if sale_order.unit_id and sale_order.unit_id.exists():
                            transfer_fields['unit_id'] = sale_order.unit_id.id
                        
                        # Only update if not already set
                        for field_name, field_value in transfer_fields.items():
                            if field_name not in safe_vals and field_value:
                                safe_vals[field_name] = field_value
                                
                except Exception as e:
                    _logger.error("Error transferring sale order fields: %s", e)
            
            processed_vals_list.append(safe_vals)
            _logger.info("Processed safe_vals[%d]: %s", i, safe_vals)
        
        # Call super with processed values
        try:
            if single_record:
                result = super(AccountMove, self).create(processed_vals_list[0])
            else:
                result = super(AccountMove, self).create(processed_vals_list)
            
            _logger.info("AccountMove.create successful, created: %s", result)
            return result
            
        except Exception as e:
            _logger.error("Error in super().create(): %s", e)
            _logger.error("Processed vals_list: %s", processed_vals_list)
            raise

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