from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Deal Information Fields - Professional naming convention with proper help text
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="Date when the deal was booked"
    )
    
    developer_commission = fields.Float(
        string='Developer Commission',
        tracking=True,
        digits=(16, 2),
        help="Commission percentage for the developer"
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="Customer who is purchasing the property"
    )
    
    deal_id = fields.Char(
        string='Deal Reference',
        tracking=True,
        copy=False,
        help="Unique identifier for this deal"
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project',
        tracking=True,
        domain=[('detailed_type', '=', 'service')],
        help="Select the project for this deal"
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="Total value of the property sale"
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        help="Specific unit being sold"
    )

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Update unit domain when project changes"""
        if self.project_id:
            domain = [('product_tmpl_id', '=', self.project_id.id)]
            return {'domain': {'unit_id': domain}}
        else:
            return {'domain': {'unit_id': []}}