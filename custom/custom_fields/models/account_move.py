from odoo import api, fields, models
from .deal_fields_mixin import DealFieldsMixin

class AccountMove(models.Model):
    _inherit = ['account.move', 'deal.fields.mixin']

    sale_order_type_id = fields.Many2one(
        'sale.order.type',  # Correct model name
        string='Sales Order Type',
        tracking=True,
    )
    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    @api.model
    def create(self, vals):
        # Defensive: Ensure all Many2one fields reference valid records or are set to False
        for field_name, field in self._fields.items():
            if isinstance(field, fields.Many2one) and field_name in vals:
                val = vals[field_name]
                if isinstance(val, int):
                    if val and not self.env[field.comodel_name].browse(val).exists():
                        vals[field_name] = False
                elif hasattr(val, 'exists'):  # Check if it's a recordset
                    if not val.exists():
                        vals[field_name] = False
        
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([
                ('name', '=', vals.get('invoice_origin'))
            ], limit=1)
            if sale_order:
                vals.update({
                    'booking_date': sale_order.booking_date,
                    'developer_commission': sale_order.developer_commission,
                    'buyer_id': sale_order.buyer_id.id if sale_order.buyer_id else False,
                    'deal_id': sale_order.deal_id,
                    'project_id': sale_order.project_id.id if sale_order.project_id else False,
                    'sale_value': sale_order.sale_value,
                    'unit_id': sale_order.unit_id.id if sale_order.unit_id else False,
                    'sale_order_type_id': sale_order.sale_order_type_id.id if sale_order.sale_order_type_id else False,
                })
        return super(AccountMove, self).create(vals)