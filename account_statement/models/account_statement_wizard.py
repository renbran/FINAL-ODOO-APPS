from odoo import models, fields, api, _
from datetime import date

class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='End Date', required=True, default=fields.Date.context_today)

    line_ids = fields.One2many('account.statement.wizard.line', 'wizard_id', string='Statement Lines', compute='_compute_lines', store=False)
    total_debit = fields.Monetary(string='Total Debit', compute='_compute_totals', store=False)
    total_credit = fields.Monetary(string='Total Credit', compute='_compute_totals', store=False)
    balance = fields.Monetary(string='Balance', compute='_compute_totals', store=False)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=False)

    @api.depends('partner_id')
    def _compute_currency(self):
        for wizard in self:
            wizard.currency_id = self.env.company.currency_id

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_lines(self):
        for wizard in self:
            lines = []
            if wizard.partner_id and wizard.date_from and wizard.date_to:
                domain = [
                    ('partner_id', '=', wizard.partner_id.id),
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice']),
                    ('date', '>=', wizard.date_from),
                    ('date', '<=', wizard.date_to),
                    ('move_id.state', '=', 'posted'),
                ]
                account_lines = self.env['account.move.line'].search(domain, order='date, id')
                running_balance = 0.0
                for line in account_lines:
                    debit = line.debit
                    credit = line.credit
                    running_balance += debit - credit
                    lines.append((0, 0, {
                        'invoice_date': line.date,
                        'due_date': line.move_id.invoice_date_due,
                        'payment_date': line.move_id.invoice_payment_ref and line.move_id.invoice_payment_date or False,
                        'number': line.move_id.name,
                        'reference': line.ref or line.move_id.ref,
                        'debit': debit,
                        'credit': credit,
                        'running_balance': running_balance,
                    }))
            wizard.line_ids = lines

    @api.depends('line_ids')
    def _compute_totals(self):
        for wizard in self:
            total_debit = sum(line.debit for line in wizard.line_ids)
            total_credit = sum(line.credit for line in wizard.line_ids)
            balance = sum(line.debit - line.credit for line in wizard.line_ids)
            wizard.total_debit = total_debit
            wizard.total_credit = total_credit
            wizard.balance = balance

    def action_generate_pdf(self):
        return self.env.ref('account_statement.account_statement_report_action').report_action(self)

    def action_generate_excel(self):
        # Placeholder for Excel export logic
        pass

class AccountStatementWizardLine(models.TransientModel):
    _name = 'account.statement.wizard.line'
    _description = 'Account Statement Wizard Line'

    wizard_id = fields.Many2one('account.statement.wizard', string='Wizard', ondelete='cascade')
    invoice_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    payment_date = fields.Date(string='Payment Date')
    number = fields.Char(string='Number')
    reference = fields.Char(string='Reference')
    debit = fields.Monetary(string='Debit')
    credit = fields.Monetary(string='Credit')
    running_balance = fields.Monetary(string='Running Balance')
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id', store=False)
