from odoo import models, fields

class AccountStatement(models.Model):
    _name = 'account.statement'
    _description = 'Account Statement'
    _order = 'date desc, id desc'

    name = fields.Char(string='Statement Name', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    total_debit = fields.Monetary(string='Total Debit', currency_field='currency_id')
    total_credit = fields.Monetary(string='Total Credit', currency_field='currency_id')
    balance = fields.Monetary(string='Balance', currency_field='currency_id')
    line_ids = fields.One2many('account.statement.line', 'statement_id', string='Statement Lines')


class AccountStatementLine(models.Model):
    _name = 'account.statement.line'
    _description = 'Account Statement Line'
    _order = 'invoice_date, id'

    statement_id = fields.Many2one('account.statement', string='Statement', ondelete='cascade')
    invoice_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    payment_date = fields.Date(string='Payment Date')
    number = fields.Char(string='Number')
    reference = fields.Char(string='Reference')
    debit = fields.Monetary(string='Debit', currency_field='currency_id')
    credit = fields.Monetary(string='Credit', currency_field='currency_id')
    running_balance = fields.Monetary(string='Running Balance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='statement_id.currency_id', store=True)