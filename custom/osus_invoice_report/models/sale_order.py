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
            'sale_order_type_id': self.sale_order_type_id.id if self.sale_order_type_id else False,
        })
        
        return invoice_vals