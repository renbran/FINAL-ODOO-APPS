# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    default_account_id = fields.Many2one('account.account', string='Default Expense Account',
        help='Default account to use for purchase order lines if not set on product or category.')
    
    # Commission fields for purchase orders (simplified to match sale order structure)
    commission_rate = fields.Float(
        string='Commission Rate (%)', 
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    commission_amount = fields.Monetary(
        string='Commission Amount',
        currency_field='currency_id',
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )
    
    @api.onchange('commission_rate')
    def _onchange_commission_rate(self):
        """Calculate amount when rate is changed"""
        if self.commission_rate and self.amount_total:
            self.commission_amount = self.commission_rate * self.amount_total / 100
    
    @api.onchange('commission_amount')
    def _onchange_commission_amount(self):
        """Calculate rate when amount is changed"""
        if self.commission_amount and self.amount_total:
            self.commission_rate = (self.commission_amount / self.amount_total * 100) if self.amount_total else 0.0
    
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
        help='Account for this purchase line. If not set, will use the default from the purchase order or company.')

    @api.model
    def create(self, vals):
        if not vals.get('account_id') and vals.get('order_id'):
            order = self.env['purchase.order'].browse(vals['order_id'])
            default_account = order.default_account_id or getattr(order.company_id, 'expense_account_id', False)
            if default_account:
                vals['account_id'] = default_account.id
        return super().create(vals)
