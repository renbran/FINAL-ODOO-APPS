from odoo import models, fields, api

class CommissionCalculation(models.Model):
    _name = 'commission.calculation'
    _description = 'Commission Calculation'

    name = fields.Char(string='Description', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='sale_order_id.currency_id', store=True)
    commission_line_ids = fields.One2many('commission.calculation.line', 'calculation_id', string='Commission Lines')
    notes = fields.Text(string='Notes')
    total_external = fields.Monetary(string='Total External', compute='_compute_totals', store=True)
    total_internal = fields.Monetary(string='Total Internal', compute='_compute_totals', store=True)
    total_payable = fields.Monetary(string='Total Payable', compute='_compute_totals', store=True)
    company_net_commission = fields.Monetary(string='Company Net Commission', compute='_compute_totals', store=True)
    gross_share = fields.Monetary(string='Gross Share (After External)', compute='_compute_totals', store=True)
    total_untaxed_amount = fields.Monetary(string='Total Untaxed Amount', compute='_compute_totals', store=True)

    @api.depends('commission_line_ids.commission_amount', 'commission_line_ids.commission_party_type', 'sale_order_id.amount_untaxed')
    def _compute_totals(self):
        for rec in self:
            rec.total_external = sum(line.commission_amount for line in rec.commission_line_ids if line.commission_party_type == 'external')
            rec.total_internal = sum(line.commission_amount for line in rec.commission_line_ids if line.commission_party_type == 'internal')
            rec.total_payable = rec.total_external + rec.total_internal
            rec.total_untaxed_amount = rec.sale_order_id.amount_untaxed or 0.0
            rec.gross_share = rec.total_untaxed_amount - rec.total_external
            rec.company_net_commission = rec.gross_share - rec.total_internal

class CommissionCalculationLine(models.Model):
    _name = 'commission.calculation.line'
    _description = 'Commission Calculation Line'

    calculation_id = fields.Many2one('commission.calculation', string='Commission Calculation', required=True, ondelete='cascade')
    commission_party_type = fields.Selection([
        ('external', 'External (Vendor/Partner)'),
        ('internal', 'Internal (Employee)'),
    ], string='Commission Party Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor/Partner', domain="[('is_company','=',True)]")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    commission_basis = fields.Selection([
        ('untaxed_total', 'Untaxed Total'),
        ('price_unit', 'Unit Price'),
        ('fixed', 'Fixed (User input)'),
    ], string='Commission Basis', required=True)
    commission_rate = fields.Float(string='Commission Rate (%)')
    commission_amount = fields.Monetary(string='Commission Amount')
    currency_id = fields.Many2one('res.currency', string='Currency', related='calculation_id.currency_id', store=True)
    notes = fields.Text(string='Notes')

    # Only one of partner_id or employee_id should be set, depending on commission_party_type
    @api.constrains('commission_party_type', 'partner_id', 'employee_id')
    def _check_party_type(self):
        for rec in self:
            if rec.commission_party_type == 'external' and not rec.partner_id:
                raise ValueError('External commission lines must have a Vendor/Partner.')
            if rec.commission_party_type == 'internal' and not rec.employee_id:
                raise ValueError('Internal commission lines must have an Employee.')
            if rec.commission_party_type == 'external' and rec.employee_id:
                raise ValueError('External commission lines cannot have an Employee.')
            if rec.commission_party_type == 'internal' and rec.partner_id:
                raise ValueError('Internal commission lines cannot have a Vendor/Partner.')
