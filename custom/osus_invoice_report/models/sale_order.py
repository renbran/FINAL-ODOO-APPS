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
        
        # Safe field transfer with existence checks
        def safe_transfer(field):
            value = getattr(self, field)
            if field.endswith('_id') and value:
                return value.id if value.exists() else False
            return value if value else False
        
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
            invoice_vals[field] = safe_transfer(field)
        
        return invoice_vals