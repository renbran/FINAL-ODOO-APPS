from odoo import models, fields

class CommissionCalculation(models.Model):
    _name = 'commission.calculation'
    _description = 'Commission Calculation'

    name = fields.Char(string='Description', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='sale_order_id.currency_id', store=True)
    commission_line_ids = fields.One2many('commission.calculation.line', 'calculation_id', string='Commission Lines')
    notes = fields.Text(string='Notes')
    total_external = fields.Monetary(string='Total External')
    total_internal = fields.Monetary(string='Total Internal')
    total_payable = fields.Monetary(string='Total Payable')
    company_net_commission = fields.Monetary(string='Company Net Commission')
    gross_share = fields.Monetary(string='Gross Share (After External)')
    total_untaxed_amount = fields.Monetary(string='Total Untaxed Amount')

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
