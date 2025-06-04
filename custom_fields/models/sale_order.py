from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="The date when the booking was made."
    )
    
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits=(16, 2),
        help="Commission amount for the broker."
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="The buyer associated with this sale order."
    )
    
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
        help="Unique identifier for the deal."
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        help="The project associated with this sale order."
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="The total sale value of the order."
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        domain="[('product_tmpl_id', '=', project_id)]",
        help="The specific unit associated with this sale order."
    )

    # Ensure currency_id is properly defined
    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id.id

    # Override currency_id to ensure it's always set
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        # Ensure currency is set
        if not invoice_vals.get('currency_id'):
            invoice_vals['currency_id'] = self.currency_id.id or self.env.company.currency_id.id
        return invoice_vals