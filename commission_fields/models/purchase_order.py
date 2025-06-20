# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    default_account_id = fields.Many2one('account.account', string='Default Expense Account',
        help='Default account to use for purchase order lines if not set on product or category.')

    deal_id = fields.Char(string='Deal ID', copy=False, help="Related Sale Order Deal ID", index=True)

    commission_reference = fields.Char(string='Commission Reference', copy=False, help="Reference number for commission tracking")

    commission_source = fields.Selection([
        ('internal', 'Internal Commission'),
        ('external', 'External Commission'),
        ('broker', 'Broker Commission')
    ], string='Commission Source', 
       help="Source of the commission payment"
    )

    commission_amount = fields.Monetary(string='Commission Amount', currency_field='currency_id', help="Amount of commission to be paid")

    commission_payment_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Payment Status',
       default='draft',
       help="Status of the commission payment"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Set default account for purchase order lines if not set."""
        orders = super().create(vals_list)
        for order in orders:
            for line in order.order_line:
                if not line.account_id:
                    # Use default_account_id if set, otherwise fallback to company's default expense account (if exists)
                    default_account = order.default_account_id or getattr(order.company_id, 'expense_account_id', False)
                    if default_account:
                        line.account_id = default_account
        return orders

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_id = fields.Many2one('account.account', string='Expense Account',
        help='Account for this purchase line. If not set, will use the default from the purchase order or company.')

    @api.model_create_multi
    def create(self, vals_list):
        """Set default account for purchase order line if not set."""
        for vals in vals_list:
            if not vals.get('account_id') and vals.get('order_id'):
                order = self.env['purchase.order'].browse(vals['order_id'])
                default_account = order.default_account_id or getattr(order.company_id, 'expense_account_id', False)
                if default_account:
                    vals['account_id'] = default_account.id
        return super().create(vals_list)
