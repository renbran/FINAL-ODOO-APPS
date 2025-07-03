from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # The field names in the model must match the view exactly
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
    )
    
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits=(16, 2),
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
    )
    
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
    )