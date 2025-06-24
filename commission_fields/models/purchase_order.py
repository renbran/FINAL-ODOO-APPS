# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    default_account_id = fields.Many2one('account.account', string='Default Expense Account',
        help='Default account to use for purchase order lines if not set on product or category.')
    
    # External Commission Fields (similar to sale.order)
    external_commission_type = fields.Selection([
        ('unit_price', 'Percentage of Unit Price'),
        ('untaxed', 'Percentage of Untaxed Amount'),
        ('fixed', 'Fixed Amount'),
    ], string='External Commission Type', default='unit_price')
    
    external_percentage = fields.Float(string='External Commission %', digits=(16, 2))
    external_fixed_amount = fields.Monetary(string='External Fixed Amount', currency_field='currency_id')
    
    # Computed fields for UI visibility
    show_external_percentage = fields.Boolean(
        string='Show External Percentage',
        compute='_compute_show_commission_fields'
    )
    show_external_fixed_amount = fields.Boolean(
        string='Show External Fixed Amount', 
        compute='_compute_show_commission_fields'
    )
    
    @api.depends('external_commission_type')
    def _compute_show_commission_fields(self):
        """Compute visibility of commission fields based on commission type"""
        for record in self:
            record.show_external_percentage = record.external_commission_type in ['unit_price', 'untaxed']
            record.show_external_fixed_amount = record.external_commission_type == 'fixed'
    
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
