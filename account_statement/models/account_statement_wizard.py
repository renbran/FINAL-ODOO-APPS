from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='End Date', required=True, default=fields.Date.context_today)

    line_ids = fields.One2many(
        'account.statement.wizard.line', 'wizard_id',
        string='Statement Lines', compute='_compute_lines', store=False, readonly=True
    )
    total_debit = fields.Monetary(
        string='Total Debit', compute='_compute_totals', store=False, readonly=True, currency_field='currency_id'
    )
    total_credit = fields.Monetary(
        string='Total Credit', compute='_compute_totals', store=False, readonly=True, currency_field='currency_id'
    )
    balance = fields.Monetary(
        string='Balance', compute='_compute_totals', store=False, readonly=True, currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency', compute='_compute_currency', store=False, readonly=True
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise UserError(_('Start date cannot be later than end date.'))

    @api.depends('partner_id')
    def _compute_currency(self):
        company_currency = self.env.company.currency_id
        for wizard in self:
            wizard.currency_id = company_currency

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_lines(self):
        AccountStatementWizardLine = self.env['account.statement.wizard.line']
        for wizard in self:
            lines = []
            if wizard.partner_id and wizard.date_from and wizard.date_to:
                domain = [
                    ('partner_id', '=', wizard.partner_id.id),
                    ('move_id.move_type', 'in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']),
                    ('date', '>=', wizard.date_from),
                    ('date', '<=', wizard.date_to),
                    ('move_id.state', '=', 'posted'),
                    ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                ]
                account_lines = self.env['account.move.line'].search(domain, order='date, id')
                running_balance = 0.0
                for line in account_lines:
                    debit = line.debit or 0.0
                    credit = line.credit or 0.0
                    running_balance += debit - credit
                    payment_date = False
                    if line.move_id.payment_state == 'paid':
                        reconciled_lines = line.matched_debit_ids + line.matched_credit_ids
                        if reconciled_lines:
                            payment_date = max(reconciled_lines.mapped('create_date')).date()
                    lines.append((0, 0, {
                        'invoice_date': line.date,
                        'due_date': line.move_id.invoice_date_due or line.date_maturity,
                        'payment_date': payment_date,
                        'number': line.move_id.name or '',
                        'reference': line.ref or line.move_id.ref or '',
                        'debit': debit,
                        'credit': credit,
                        'running_balance': running_balance,
                    }))
            wizard.line_ids = lines

    @api.depends('line_ids')
    def _compute_totals(self):
        for wizard in self:
            total_debit = sum(line.debit or 0.0 for line in wizard.line_ids)
            total_credit = sum(line.credit or 0.0 for line in wizard.line_ids)
            wizard.total_debit = total_debit
            wizard.total_credit = total_credit
            wizard.balance = total_debit - total_credit

    def action_generate_pdf(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Please select a partner first.'))
        return self.env.ref('account_statement.account_statement_report_action').report_action(self)

    def action_generate_excel(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Please select a partner first.'))
        import base64
        import io
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('Please install xlsxwriter: pip install xlsxwriter'))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Account Statement')

        # Styles
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#800020', 'font_color': 'white', 'border': 1, 'align': 'center'
        })
        cell_format = workbook.add_format({'border': 1, 'align': 'left'})
        amount_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0.00'})
        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
        date_format = workbook.add_format({'border': 1, 'align': 'left', 'num_format': 'yyyy-mm-dd'})

        worksheet.merge_range('A1:H1', 'Account Statement', title_format)
        worksheet.set_row(0, 30)

        worksheet.write('A3', 'Partner:', header_format)
        worksheet.write('B3', self.partner_id.name or '', cell_format)
        worksheet.write('A4', 'Address:', header_format)
        worksheet.write('B4', self.partner_id.contact_address or '', cell_format)
        worksheet.write('A5', 'VAT:', header_format)
        worksheet.write('B5', self.partner_id.vat or '', cell_format)
        worksheet.write('A6', 'Phone:', header_format)
        worksheet.write('B6', self.partner_id.phone or '', cell_format)
        worksheet.write('A7', 'Email:', header_format)
        worksheet.write('B7', self.partner_id.email or '', cell_format)

        worksheet.write('F3', 'Report Generated:', header_format)
        worksheet.write('G3', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cell_format)
        worksheet.write('F4', 'Date Range:', header_format)
        worksheet.write('G4', f"{self.date_from} to {self.date_to}", cell_format)

        headers = [
            'Invoice Date', 'Due Date', 'Payment Date', 'Number', 'Reference',
            'Debit', 'Credit', 'Running Balance'
        ]
        worksheet.write_row('A9', headers, header_format)

        row = 9
        lines = sorted(self.line_ids, key=lambda l: l.invoice_date or fields.Date.today())
        for line in lines:
            worksheet.write(row, 0, line.invoice_date or '', date_format)
            worksheet.write(row, 1, line.due_date or '', date_format)
            worksheet.write(row, 2, line.payment_date or '', date_format)
            worksheet.write(row, 3, line.number or '', cell_format)
            worksheet.write(row, 4, line.reference or '', cell_format)
            worksheet.write_number(row, 5, line.debit or 0.0, amount_format)
            worksheet.write_number(row, 6, line.credit or 0.0, amount_format)
            worksheet.write_number(row, 7, line.running_balance or 0.0, amount_format)
            row += 1

        if lines:
            worksheet.write(row, 4, 'TOTAL', header_format)
            worksheet.write_number(row, 5, self.total_debit or 0.0, amount_format)
            worksheet.write_number(row, 6, self.total_credit or 0.0, amount_format)
            worksheet.write_number(row, 7, self.balance or 0.0, amount_format)

        worksheet.set_column('A:A', 14)
        worksheet.set_column('B:B', 14)
        worksheet.set_column('C:C', 14)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:H', 16)

        workbook.close()
        output.seek(0)
        file_data = output.read()
        output.close()

        data = base64.b64encode(file_data)
        filename = f"Account_Statement_{self.partner_id.name or 'Partner'}_{fields.Date.today()}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': data,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{attachment.id}?download=true",
            'target': 'self',
        }


class AccountStatementWizardLine(models.TransientModel):
    _name = 'account.statement.wizard.line'
    _description = 'Account Statement Wizard Line'

    wizard_id = fields.Many2one('account.statement.wizard', string='Wizard', ondelete='cascade')
    invoice_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    payment_date = fields.Date(string='Payment Date')
    number = fields.Char(string='Number')
    reference = fields.Char(string='Reference')
    debit = fields.Monetary(string='Debit', currency_field='currency_id')
    credit = fields.Monetary(string='Credit', currency_field='currency_id')
    running_balance = fields.Monetary(string='Running Balance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id', store=False, readonly=True)