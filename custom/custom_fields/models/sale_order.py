from odoo import models, fields, api
from .deal_fields_mixin import DealFieldsMixin

class SaleOrder(models.Model):
    _inherit = ['sale.order', 'deal.fields.mixin']

    sale_value_formatted = fields.Char(
        string='Formatted Sale Value',
        compute='_compute_sale_value_formatted',
    )

    @api.depends('sale_value')
    def _compute_sale_value_formatted(self):
        from ..utils.number_format import format_amount
        for rec in self:
            rec.sale_value_formatted = format_amount(rec.sale_value)