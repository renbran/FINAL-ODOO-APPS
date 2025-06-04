from odoo import models, fields, api

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
                commission.amount = commission.rate
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
                commission.amount = commission.rate
            elif commission.calculation_type == 'percentage_untaxed':
                commission.amount = (commission.rate / 100) * (commission.order_id.amount_untaxed or 0)
            elif commission.calculation_type == 'percentage_sale_value':
                commission.amount = (commission.rate / 100) * (commission.order_id.x_sale_value or 0)

    @api.onchange('calculation_type')
    def _onchange_calculation_type(self):
        if self.calculation_type == 'fixed':
            self.rate = 0.0