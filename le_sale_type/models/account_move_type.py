from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_type_id = fields.Many2one('sale.order.type', string="Sale Order Type", readonly=True)
    sale_order_type_prefix = fields.Char(string="Sale Order Type Prefix", readonly=True)

    @api.model
    def create(self, vals):
        # If this is an invoice created from a sale order, populate the sale order type
        if vals.get('move_type') == 'out_invoice' and vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                vals['sale_order_type_id'] = sale_order.sale_order_type_id.id if sale_order.sale_order_type_id else False
                vals['sale_order_type_prefix'] = sale_order.sale_order_type_id.prefix if sale_order.sale_order_type_id else False
        
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        
        # If the invoice origin is being set or changed, update the sale order type
        if 'invoice_origin' in vals:
            for move in self:
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    move.sale_order_type_id = sale_order.sale_order_type_id
                    move.sale_order_type_prefix = sale_order.sale_order_type_id.prefix if sale_order.sale_order_type_id else False
        
        return res

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        ''' This method is called when creating invoices from the sale order.
        It aims to populate 'invoice_line_ids' with the right product/account/taxes... based on the sale order.
        '''
        new_vals_list = []
        for vals in vals_list:
            if vals.get('invoice_origin'):
                sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
                if sale_order and sale_order.sale_order_type_id:
                    vals['sale_order_type_id'] = sale_order.sale_order_type_id.id
                    vals['sale_order_type_prefix'] = sale_order.sale_order_type_id.prefix
            new_vals_list.append(vals)
        return super(AccountMove, self)._move_autocomplete_invoice_lines_create(new_vals_list)