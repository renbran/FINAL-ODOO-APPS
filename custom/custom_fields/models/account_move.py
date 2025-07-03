from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Deal tracking fields - open for creation with uniform naming
    booking_date = fields.Date(string='Booking Date', tracking=True, help='Date when the deal was booked')
    developer_commission = fields.Float(string='Developer Commission', tracking=True, digits=(16, 2), help='Commission percentage for the developer')
    buyer_id = fields.Many2one('res.partner', string='Buyer', tracking=True, help='Customer who is purchasing the unit')
    deal_id = fields.Integer(string='Deal ID', tracking=True, help='Unique identifier for the deal')
    project_id = fields.Many2one('product.template', string='Project', tracking=True, help='Real estate project')
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id', help='Total value of the sale')
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True, help='Specific unit being sold')

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    @api.model
    def create(self, vals_list):
        """Enhanced create method with proper field validation and sale order integration"""
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
            
            # Create a copy to avoid modifying original
            safe_vals = vals.copy()
            
            # Validate and clean Many2one fields (removed sale_order_type_id)
            many2one_fields = ['buyer_id', 'project_id', 'unit_id']
            for field_name in many2one_fields:
                if field_name in safe_vals:
                    value = safe_vals[field_name]
                    if not value:
                        safe_vals[field_name] = False
                    elif isinstance(value, int) and value > 0:
                        # Determine the related model based on field name
                        related_model_map = {
                            'buyer_id': 'res.partner',
                            'project_id': 'product.template', 
                            'unit_id': 'product.product'
                        }
                        if field_name in related_model_map:
                            try:
                                related_model = related_model_map[field_name]
                                if self.env[related_model].browse(value).exists():
                                    safe_vals[field_name] = value
                                else:
                                    _logger.warning("Many2one field %s: record ID %d does not exist in %s", 
                                                  field_name, value, related_model)
                                    safe_vals[field_name] = False
                            except Exception as e:
                                _logger.error("Error validating Many2one field %s with value %s: %s", 
                                            field_name, value, e)
                                safe_vals[field_name] = False
                    elif hasattr(value, 'id') and isinstance(getattr(value, 'id', None), int):
                        # Handle recordset objects
                        safe_vals[field_name] = value.id if value.id else False
                    else:
                        _logger.warning("Many2one field %s: invalid value type %s", field_name, type(value))
                        safe_vals[field_name] = False
            
            # Transfer sale order fields for invoices
            if safe_vals.get('move_type') in ['out_invoice', 'out_refund'] and safe_vals.get('invoice_origin'):
                try:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', safe_vals.get('invoice_origin'))
                    ], limit=1)
                    
                    if sale_order:
                        _logger.info("Found sale order %s, transferring fields", sale_order.name)
                        
                        # Only transfer if not already provided
                        transfer_mapping = {
                            'booking_date': sale_order.booking_date,
                            'developer_commission': sale_order.developer_commission,
                            'deal_id': sale_order.deal_id,
                            'sale_value': sale_order.sale_value,
                        }
                        
                        # Handle Many2one fields safely
                        if sale_order.buyer_id and sale_order.buyer_id.exists():
                            transfer_mapping['buyer_id'] = sale_order.buyer_id.id
                        
                        if sale_order.project_id and sale_order.project_id.exists():
                            transfer_mapping['project_id'] = sale_order.project_id.id
                        
                        if sale_order.unit_id and sale_order.unit_id.exists():
                            transfer_mapping['unit_id'] = sale_order.unit_id.id
                        for field_name, field_value in transfer_mapping.items():
                            if field_name not in safe_vals and field_value:
                                safe_vals[field_name] = field_value
                                
                except Exception as e:
                    _logger.error("Error transferring sale order fields: %s", e)
            
            processed_vals_list.append(safe_vals)
            _logger.info("Processed safe_vals[%d]: %s", i, safe_vals)
        
        # Call super with processed values
        try:
            result = super(AccountMove, self).create(processed_vals_list if not single_record else processed_vals_list[0])
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