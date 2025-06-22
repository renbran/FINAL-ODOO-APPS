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
    gross_share = fields.Monetary(string='Gross Share (After External)', compute='_compute_gross_share', store=True)
    total_untaxed_amount = fields.Monetary(string='Total Untaxed Amount', related='sale_order_id.amount_untaxed', store=True)

    @api.depends('commission_line_ids.commission_amount', 'commission_line_ids.commission_party_type')
    def _compute_totals(self):
        for rec in self:
            rec.total_external = sum(l.commission_amount for l in rec.commission_line_ids if l.commission_party_type == 'external')
            rec.total_internal = sum(l.commission_amount for l in rec.commission_line_ids if l.commission_party_type == 'internal')
            rec.total_payable = rec.total_external + rec.total_internal
            rec.company_net_commission = rec.total_untaxed_amount - rec.total_external

    @api.depends('total_untaxed_amount', 'total_external')
    def _compute_gross_share(self):
        for rec in self:
            rec.gross_share = rec.total_untaxed_amount - rec.total_external

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
    commission_amount = fields.Monetary(string='Commission Amount', compute='_compute_commission_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='calculation_id.currency_id', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('commission_basis', 'commission_rate', 'calculation_id.total_untaxed_amount', 'calculation_id.sale_order_id', 'commission_party_type', 'calculation_id.gross_share')
    def _compute_commission_amount(self):
        for line in self:
            base = 0.0
            if line.commission_basis == 'untaxed_total':
                if line.commission_party_type == 'internal':
                    base = line.calculation_id.gross_share
                else:
                    base = line.calculation_id.total_untaxed_amount
            elif line.commission_basis == 'price_unit':
                base = line.calculation_id.sale_order_id.amount_total or 0.0
            elif line.commission_basis == 'fixed':
                base = 0.0
            if line.commission_basis == 'fixed':
                line.commission_amount = line.commission_rate  # For fixed, user enters the amount directly in 'commission_rate' field
            else:
                line.commission_amount = (base * line.commission_rate) / 100.0

    # Only one of partner_id or employee_id should be set, depending on commission_party_type
