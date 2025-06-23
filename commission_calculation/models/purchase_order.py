from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    commission_sale_order_id = fields.Many2one(
        'sale.order',
        string='Source Sales Order',
        readonly=True
    )

    commission_type = fields.Selection([
        ('broker', 'Broker'),
        ('referral', 'Referral'),
        ('agent', 'Agent'),
        ('manager', 'Manager'),
        ('director', 'Director')
    ], string='Commission Type', readonly=True)