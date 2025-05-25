# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Commission Lines
    external_commission_line_ids = fields.One2many(
        'sale.order.external.commission', 'order_id', 
        string="External Commissions")
    internal_commission_line_ids = fields.One2many(
        'sale.order.internal.commission', 'order_id', 
        string="Internal Commissions")
    
    # Computed Fields
    total_external_commission = fields.Monetary(
        string="Total External Commission", 
        compute="_compute_total_commissions", store=True)
    total_internal_commission = fields.Monetary(
        string="Total Internal Commission", 
        compute="_compute_total_commissions", store=True)
    company_net_share = fields.Monetary(
        string="Company Net Share", 
        compute="_compute_total_commissions", store=True)
    remaining_for_internal = fields.Monetary(
        string="Remaining for Internal", 
        compute="_compute_total_commissions")
    
    # Related Fields
    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    purchase_order_count = fields.Integer(compute='_compute_purchase_order_count')
    commission_processed = fields.Boolean(string="Commissions Processed", default=False)
    commission_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('pending_payment', 'Pending Payment'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Commission Processing Status", default='not_started', tracking=True)
    consultant_id = fields.Many2one('res.partner', string="Consultant", domain=[('is_consultant', '=', True)])

    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': {'create': False},
        }

    @api.depends('amount_untaxed', 'x_sale_value', 
                 'external_commission_line_ids.amount', 
                 'internal_commission_line_ids.amount')
    def _compute_total_commissions(self):
        for order in self:
            order.total_external_commission = sum(order.external_commission_line_ids.mapped('amount'))
            order.remaining_for_internal = (order.x_sale_value or order.amount_untaxed or 0) - order.total_external_commission
            order.total_internal_commission = sum(order.internal_commission_line_ids.mapped('amount'))
            order.company_net_share = order.remaining_for_internal - order.total_internal_commission

    def _get_commission_product(self):
        product = self.env['product.product'].search([('name', '=', 'Sales Commission'), ('type', '=', 'service')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'Sales Commission',
                'type': 'service',
                'list_price': 0.0,
                'purchase_ok': True,
                'sale_ok': False,
            })
        return product

    def _prepare_purchase_order_vals(self, partner, amount, description):
        product = self._get_commission_product()
        return {
            'partner_id': partner.id,
            'date_order': fields.Date.today(),
            'origin': f"Commission from {self.name}",
            'description': description,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': description,
                'product_qty': 1.0,
                'product_uom': product.uom_id.id,
                'price_unit': amount,
            })],
            'origin_so_id': self.id,
        }

    def action_process_commissions(self):
        self.ensure_one()
        if not self.external_commission_line_ids and not self.internal_commission_line_ids:
            raise UserError(_("Please add at least one commission line before processing."))
        return self._auto_generate_purchase_orders()

    def action_recalculate_commissions(self):
        self.ensure_one()
        self._compute_total_commissions()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Commissions recalculated."),
                'type': 'success',
                'sticky': False,
            }
        }

    def _auto_generate_purchase_orders(self):
        self.ensure_one()
        if self.commission_processed:
            raise UserError(_("Commissions have already been processed for this order."))

        self.commission_status = 'in_progress'

        for line in self.external_commission_line_ids + self.internal_commission_line_ids:
            if line.partner_id and line.amount > 0:
                commission_type = line.commission_type if hasattr(line, 'commission_type') else line.role
                vals = self._prepare_purchase_order_vals(
                    line.partner_id, 
                    line.amount, 
                    f"{commission_type} Commission for SO: {self.name}")
                self.env['purchase.order'].create(vals)

        self.commission_processed = True
        self.commission_status = 'completed'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Commission purchase orders created successfully."),
                'type': 'success',
                'sticky': False,
            }
        }


class SaleOrderExternalCommission(models.Model):
    _name = 'sale.order.external.commission'
    _description = 'External Commission Line'
    _order = 'sequence, id'

    order_id = fields.Many2one('sale.order', string="Sale Order", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)
    commission_type = fields.Selection([
        ('agency', 'Agency'),
        ('referral', 'Referral'),
        ('cashback', 'Cashback'),
        ('other', 'Other')
    ], string="Commission Type", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, domain=[('is_external_agent', '=', True)])
    rate = fields.Float(string="Commission Rate (%)")
    amount = fields.Monetary(string="Commission Amount", currency_field='currency_id', compute='_compute_amount', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id')
    calculation_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage_untaxed', 'Percentage of Untaxed Total'),
        ('percentage_sale_value', 'Percentage of Sale Value')
    ], string="Calculation Type", default='percentage_sale_value')

    @api.depends('calculation_type', 'rate', 'order_id.amount_untaxed', 'order_id.x_sale_value')
    def _compute_amount(self):
        for commission in self:
            if commission.calculation_type == 'fixed':
                continue
            elif commission.calculation_type == 'percentage_untaxed':
                commission.amount = (commission.rate / 100) * (commission.order_id.amount_untaxed or 0)
            elif commission.calculation_type == 'percentage_sale_value':
                commission.amount = (commission.rate / 100) * (commission.order_id.x_sale_value or 0)

    @api.onchange('calculation_type')
    def _onchange_calculation_type(self):
        if self.calculation_type == 'fixed':
            self.rate = 0.0


class SaleOrderInternalCommission(models.Model):
    _name = 'sale.order.internal.commission'
    _description = 'Internal Commission Line'
    _order = 'sequence, id'

    order_id = fields.Many2one('sale.order', string="Sale Order", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)
    role = fields.Selection([
        ('main_consultant', 'Main Consultant'),
        ('partner_consultant', 'Partner Consultant'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('management', 'Management'),
        ('other', 'Other')
    ], string="Role", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, domain=[('is_internal_agent', '=', True)])
    rate = fields.Float(string="Commission Rate (%)")
    amount = fields.Monetary(string="Commission Amount", currency_field='currency_id', compute='_compute_amount', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id')
    calculation_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage_untaxed', 'Percentage of Untaxed Total'),
        ('percentage_sale_value', 'Percentage of Sale Value')
    ], string="Calculation Type", default='percentage_sale_value')

    @api.depends('calculation_type', 'rate', 'order_id.amount_untaxed', 'order_id.x_sale_value')
    def _compute_amount(self):
        for commission in self:
            if commission.calculation_type == 'fixed':
                continue
            elif commission.calculation_type == 'percentage_untaxed':
                commission.amount = (commission.rate / 100) * (commission.order_id.amount_untaxed or 0)
            elif commission.calculation_type == 'percentage_sale_value':
                commission.amount = (commission.rate / 100) * (commission.order_id.x_sale_value or 0)

    @api.onchange('calculation_type')
    def _onchange_calculation_type(self):
        if self.calculation_type == 'fixed':
            self.rate = 0.0