from odoo import api, fields, models
from .deal_fields_mixin import DealFieldsMixin

class AccountMove(models.Model):
    _inherit = ['account.move', 'deal.fields.mixin']

    amount_total_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_total_words',
        store=True,
    )

    def _transfer_sale_order_fields(self, sale_order, vals):
        """Transfer custom fields from sale order to invoice"""
        if not sale_order:
            return vals
        
        # Defensive validation for Many2one fields
        deal_fields = {
            'booking_date': sale_order.booking_date,
            'developer_commission': sale_order.developer_commission,
            'buyer_id': sale_order.buyer_id.id if sale_order.buyer_id and sale_order.buyer_id.exists() else False,
            'deal_id': sale_order.deal_id,
            'project_id': sale_order.project_id.id if sale_order.project_id and sale_order.project_id.exists() else False,
            'sale_value': sale_order.sale_value,
            'unit_id': sale_order.unit_id.id if sale_order.unit_id and sale_order.unit_id.exists() else False,
        }
        
        # Only update vals if the field is not already set
        for field_name, field_value in deal_fields.items():
            if field_name not in vals:
                vals[field_name] = field_value
        
        return vals

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
        
        # Transfer sale order custom fields if this is an invoice from a sale order
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([
                ('name', '=', vals.get('invoice_origin'))
            ], limit=1)
            if sale_order:
                vals = self._transfer_sale_order_fields(sale_order, vals)
        
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        """Override write to handle changes to invoice_origin"""
        result = super(AccountMove, self).write(vals)
        
        # If invoice_origin is being set or changed, transfer sale order fields
        if 'invoice_origin' in vals:
            for move in self:
                if move.move_type in ['out_invoice', 'out_refund'] and move.invoice_origin:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', move.invoice_origin)
                    ], limit=1)
                    if sale_order:
                        update_vals = {}
                        self._transfer_sale_order_fields(sale_order, update_vals)
                        if update_vals:
                            super(AccountMove, move).write(update_vals)
        
        return result

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        """Hook into standard Odoo invoice creation from sale orders"""
        new_vals_list = []
        for vals in vals_list:
            if vals.get('invoice_origin'):
                sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
                if sale_order:
                    vals = self._transfer_sale_order_fields(sale_order, vals)
            new_vals_list.append(vals)
        return super(AccountMove, self)._move_autocomplete_invoice_lines_create(new_vals_list)