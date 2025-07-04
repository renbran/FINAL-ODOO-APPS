from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Deal tracking fields - open for creation with uniform naming
    booking_date = fields.Date(string='Booking Date', tracking=True, help='Date when the deal was booked')
    developer_commission = fields.Float(string='Developer Commission', tracking=True, help='Commission percentage for the developer')
    buyer_id = fields.Many2one('res.partner', string='Buyer', tracking=True, help='Customer who is purchasing the unit')
    deal_id = fields.Integer(string='Deal ID', tracking=True, help='Unique identifier for the deal')
    project_id = fields.Many2one('product.template', string='Project', tracking=True, help='Real estate project')
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id', help='Total value of the sale')
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True, help='Specific unit being sold')

    # Computed field for formatted display
    sale_value_formatted = fields.Char(
        string='Formatted Sale Value',
        compute='_compute_sale_value_formatted',
        help='Human-readable format of the sale value'
    )

    def _prepare_invoice(self):
        """Override to include custom fields in invoice preparation"""
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        
        # Add custom deal fields to invoice
        invoice_vals.update({
            'booking_date': self.booking_date,
            'developer_commission': self.developer_commission,
            'buyer_id': self.buyer_id.id if self.buyer_id else False,
            'deal_id': self.deal_id,
            'project_id': self.project_id.id if self.project_id else False,
            'sale_value': self.sale_value,
            'unit_id': self.unit_id.id if self.unit_id else False,
        })
        
        # Handle sale_order_type_id field from le_sale_type module
        if hasattr(self, 'sale_order_type_id') and self.sale_order_type_id:
            try:
                # Ensure the sale order type record exists
                if self.sale_order_type_id.exists():
                    invoice_vals['sale_order_type_id'] = self.sale_order_type_id.id
            except Exception:
                # If there's any issue, don't include the field
                pass
        
        return invoice_vals