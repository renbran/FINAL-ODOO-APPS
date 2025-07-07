from odoo import fields, models

class DealFieldsMixin(models.AbstractModel):
    _name = 'deal.fields.mixin'
    _description = 'Deal Fields Mixin'

    booking_date = fields.Date(string='Booking Date', tracking=True)
    developer_commission = fields.Float(string='Broker Commission', tracking=True)
    buyer_id = fields.Many2one('res.partner', string='Buyer', tracking=True)
    deal_id = fields.Integer(string='Deal ID', tracking=True)
    project_id = fields.Many2one('product.template', string='Project Name', tracking=True)
    sale_value = fields.Monetary(string='Sale Value', tracking=True, currency_field='currency_id')
    unit_id = fields.Many2one('product.product', string='Unit', tracking=True)
