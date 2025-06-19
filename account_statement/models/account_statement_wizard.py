from odoo import models, fields, api
from datetime import datetime
import io
import xlsxwriter
import base64


class AccountStatementWizard(models.TransientModel):
    _name = 'account.statement.wizard'
    _description = 'Account Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_from = fields.Date(string='Date From', required=True, 
                           default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today())
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)
    total_debit = fields.Monetary(string='Total Debit', currency_field='currency_id', readonly=True)
    total_credit = fields.Monetary(string='Total Credit', currency_field='currency_id', readonly=True)
    balance = fields.Monetary(string='Balance', currency_field='currency_id', readonly=True)
    line_ids = fields.One2many('account.statement.wizard.line', 'wizard_id', string='Statement Lines', readonly=True)

    @api.onchange('partner_id', 'date_from', 'date_to')
    def _onchange_partner_dates(self):
        if self.partner_id and self.date_from and self.date_to:
            self._compute_statement_data()

    def _compute_statement_data(self):
        """Compute statement data based on partner and date range"""
        if not self.partner_id:
            return

        # Clear existing lines
        self.line_ids = [(5, 0, 0)]
        
        # Search for account moves
        moves = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'])
        ])

        lines_data = []
        running_balance = 0.0
        total_debit = 0.0
        total_credit = 0.0

        for move in moves.sorted('date'):
            # Get the receivable/payable line
            for line in move.line_ids:
                if line.account_id.account_type in ['asset_receivable', 'liability_payable']:
                    debit = line.debit
                    credit = line.credit
                    
                    total_debit += debit
                    total_credit += credit
                    running_balance += (debit - credit)
                    
                    lines_data.append({
                        'invoice_date': move.date,
                        'due_date': move.invoice_date_due,
                        'payment_date': move.date if move.payment_state == 'paid' else False,
                        'number': move.name,
                        'reference': move.ref or '',
                        'debit': debit,
                        'credit': credit,
                        'running_balance': running_balance,
                    })
                    break

        self.line_ids = [(0, 0, line_data) for line_data in lines_data]
        self.total_debit = total_debit
        self.total_credit = total_credit
        self.balance = total_debit - total_credit

    def action_generate_pdf(self):
        """Generate PDF report"""
        return self.env.ref('account_statement.action_report_account_statement').report_action(self)

    def action_generate_excel(self):
        """Generate Excel report"""
        import io
        import xlsxwriter
        import base64
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Account Statement')
        header_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D7E4BC'
        })
        subheader_format = workbook.add_format({
            'bold': True, 'font_size': 12, 'bg_color': '#E8F4FD'
        })
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        worksheet.merge_range('A1:H1', f'Account Statement - {self.partner_id.name}', header_format)
        worksheet.write('A2', 'Period:', subheader_format)
        worksheet.write('B2', f'{self.date_from} to {self.date_to}')
        worksheet.write('A4', 'Total Debit:', subheader_format)
        worksheet.write('B4', self.total_debit, currency_format)
        worksheet.write('A5', 'Total Credit:', subheader_format)
        worksheet.write('B5', self.total_credit, currency_format)
        worksheet.write('A6', 'Balance:', subheader_format)
        worksheet.write('B6', self.balance, currency_format)
        headers = ['Invoice Date', 'Due Date', 'Payment Date', 'Number', 'Reference', 'Debit', 'Credit', 'Running Balance']
        for col, header in enumerate(headers):
            worksheet.write(7, col, header, subheader_format)
        row = 8
        for line in self.line_ids:
            worksheet.write(row, 0, line.invoice_date, date_format)
            worksheet.write(row, 1, line.due_date, date_format)
            worksheet.write(row, 2, line.payment_date, date_format)
            worksheet.write(row, 3, line.number)
            worksheet.write(row, 4, line.reference)
            worksheet.write(row, 5, line.debit, currency_format)
            worksheet.write(row, 6, line.credit, currency_format)
            worksheet.write(row, 7, line.running_balance, currency_format)
            row += 1
        worksheet.set_column('A:C', 12)
        worksheet.set_column('D:E', 15)
        worksheet.set_column('F:H', 12)
        workbook.close()
        output.seek(0)
        filename = f'Account_Statement_{self.partner_id.name}_{self.date_from}_{self.date_to}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def action_save_statement(self):
        """Save the statement as a permanent record"""
        statement = self.env['account.statement'].create({
            'name': f'Statement - {self.partner_id.name} ({self.date_from} to {self.date_to})',
            'partner_id': self.partner_id.id,
            'date': fields.Date.today(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'currency_id': self.currency_id.id,
            'total_debit': self.total_debit,
            'total_credit': self.total_credit,
            'balance': self.balance,
        })
        
        # Create statement lines
        for line in self.line_ids:
            self.env['account.statement.line'].create({
                'statement_id': statement.id,
                'invoice_date': line.invoice_date,
                'due_date': line.due_date,
                'payment_date': line.payment_date,
                'number': line.number,
                'reference': line.reference,
                'debit': line.debit,
                'credit': line.credit,
                'running_balance': line.running_balance,
            })
        
        return {
            'name': 'Account Statement',
            'type': 'ir.actions.act_window',
            'res_model': 'account.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'target': 'current',
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
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id', store=True)