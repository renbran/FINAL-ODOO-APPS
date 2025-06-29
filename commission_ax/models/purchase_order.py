from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    description = fields.Char(string="Description")
    origin_so_id = fields.Many2one(
        'sale.order',
        string="Source Sale Order",
        ondelete='set null',
        help="The originating Sale Order for this commission purchase order."
    )
    commission_type = fields.Char(string="Commission Type", help="Type of commission for this purchase order.")
