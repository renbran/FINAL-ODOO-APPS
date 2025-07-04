from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Deal tracking fields
    booking_date = fields.Date(string='Booking Date', tracking=True)
    developer_commission = fields.Float(string='Developer Commission', tracking=True)
    buyer_id = fields.Many2one('res.partner', string='Buyer', tracking=True)
    deal_id = fields.Integer(string='Deal ID', tracking=True)
    project_id = fields.Many2one('product.template', string='Project', tracking=True)
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id')
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True)

    sale_value_formatted = fields.Char(
        string='Formatted Sale Value',
        compute='_compute_sale_value_formatted',
    )

    def _prepare_invoice(self):
        """Prepare invoice vals with safe field transfer"""
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        
        # Define fields to transfer with their types
        transfer_fields = {
            'booking_date': 'date',
            'developer_commission': 'float',
            'buyer_id': 'm2o',
            'deal_id': 'integer',
            'project_id': 'm2o',
            'sale_value': 'monetary',
            'unit_id': 'm2o'
        }
        
        for field, field_type in transfer_fields.items():
            value = getattr(self, field)
            
            if field_type == 'm2o':
                invoice_vals[field] = value.id if value and value.exists() else False
            elif value or field_type in ('integer', 'float', 'monetary'):
                invoice_vals[field] = value
        
        return invoice_vals