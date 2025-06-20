from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountStatement(models.Model):
    _name = 'account.statement'
    _description = 'Account Statement'
    _order = 'date desc, id desc'

    name = fields.Char(string='Statement Name', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today, index=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True)
    date_from = fields.Date(string='Date From', required=True, index=True)
    date_to = fields.Date(string='Date To', required=True, index=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    total_debit = fields.Monetary(string='Total Debit', currency_field='currency_id')
    total_credit = fields.Monetary(string='Total Credit', currency_field='currency_id')
    balance = fields.Monetary(string='Balance', currency_field='currency_id')
    line_ids = fields.One2many('account.statement.line', 'statement_id', string='Statement Lines')

    # Add status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_('Start date must be before end date'))

    _sql_constraints = [
        ('name_partner_date_uniq', 'unique(name,partner_id,date)', 
         'Statement name must be unique per partner and date!')
    ]

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})


class AccountStatementLine(models.Model):
    _name = 'account.statement.line'
    _description = 'Account Statement Line'
    _order = 'date, id'

    statement_id = fields.Many2one('account.statement', string='Statement', ondelete='cascade')
    date = fields.Date(string='Date')
    account_name = fields.Char(string='Account')
    account_code = fields.Char(string='Account Code')
    label = fields.Char(string='Label')
    debit = fields.Monetary(string='Debit', currency_field='currency_id')
    credit = fields.Monetary(string='Credit', currency_field='currency_id')
    running_balance = fields.Monetary(string='Running Balance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='statement_id.currency_id', store=True)