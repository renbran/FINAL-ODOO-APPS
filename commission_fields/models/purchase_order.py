# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    default_account_id = fields.Many2one('account.account', string='Default Expense Account',
        help='Default account to use for purchase order lines if not set on product or category.')
    
    @api.model
    def create(self, vals):
        order = super().create(vals)
        for line in order.order_line:
            if not line.account_id:
                # Use default_account_id if set, otherwise fallback to company's default expense account (if exists)
                default_account = order.default_account_id or getattr(order.company_id, 'expense_account_id', False)
                if default_account:
                    line.account_id = default_account
        return order

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_id = fields.Many2one('account.account', string='Expense Account',
        help='Account for this purchase line.')

    @api.model
    def create(self, vals):
        if not vals.get('account_id') and vals.get('order_id'):
            order = self.env['purchase.order'].browse(vals['order_id'])
            default_account = order.default_account_id or getattr(order.company_id, 'expense_account_id', False)
            if default_account:
                vals['account_id'] = default_account.id
        return super().create(vals)
