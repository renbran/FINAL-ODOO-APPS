from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

# Try to import Excel dependencies, handle gracefully if not available
try:
    import io
    import xlsxwriter
    import base64
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    _logger.warning("Excel dependencies not available. Excel export will be disabled.")


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
    
    # Add filter options
    account_type_filter = fields.Selection([
        ('all', 'All Accounts'),
        ('receivable', 'Receivable Only'),
        ('payable', 'Payable Only'),
    ], string='Account Filter', default='all')
    
    show_zero_balance = fields.Boolean(string='Show Zero Balance Lines', default=True)
    excel_available = fields.Boolean(string='Excel Available', compute='_compute_excel_available')

    @api.depends()
    def _compute_excel_available(self):
        for record in self:
            record.excel_available = EXCEL_AVAILABLE

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_('Start date must be before end date'))

    @api.onchange('partner_id', 'date_from', 'date_to', 'account_type_filter')
    def _onchange_partner_dates(self):
        if self.partner_id and self.date_from and self.date_to:
            self._compute_statement_data()

    def _compute_statement_data(self):
        self.ensure_one()
        if not self.partner_id:
            return

        # Clear existing lines
        self.line_ids = [(5, 0, 0)]
        
        try:
            # Build domain based on account type filter
            domain = [
                ('partner_id', '=', self.partner_id.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('move_id.state', '=', 'posted'),
            ]
            
            # Add account type filter
            if self.account_type_filter == 'receivable':
                domain.append(('account_id.account_type', '=', 'asset_receivable'))
            elif self.account_type_filter == 'payable':
                domain.append(('account_id.account_type', '=', 'liability_payable'))
            
            # Fetch all posted move lines for the partner in the date range
            move_lines = self.env['account.move.line'].search(domain, order='date, id')
        except Exception as e:
            raise ValidationError(_('Error fetching account move lines: %s') % str(e))

        lines_data = []
        running_balance = 0.0
        total_debit = 0.0
        total_credit = 0.0

        for line in move_lines:
            debit = line.debit
            credit = line.credit
            
            # Skip zero balance lines if option is disabled
            if not self.show_zero_balance and debit == 0 and credit == 0:
                continue
                
            total_debit += debit
            total_credit += credit
            running_balance += (debit - credit)
            
            lines_data.append({
                'date': line.date,
                'account_name': line.account_id.display_name,
                'account_code': line.account_id.code,
                'label': line.name or line.ref or '',
                'debit': debit,
                'credit': credit,
                'running_balance': running_balance,
            })

        self.line_ids = [(0, 0, line_data) for line_data in lines_data]
        self.total_debit = total_debit
        self.total_credit = total_credit
        self.balance = total_debit - total_credit

    def action_generate_pdf(self):
        """Generate PDF report"""
        # Use the correct external ID for the report action as defined in your manifest and XML
        return self.env.ref('account_statement.action_account_statement_wizard').report_action(self)

    def action_generate_excel(self):
        """Generate Excel report with all accounts and formatted values"""
        self.ensure_one()
        
        if not EXCEL_AVAILABLE:
            raise UserError(_("Excel export is not available. Please install the 'report_xlsx' module and required dependencies."))
        
        try:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Account Statement')
            
            # Formats
            header_format = workbook.add_format({
                'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D7E4BC'
            })
            subheader_format = workbook.add_format({
                'bold': True, 'font_size': 12, 'bg_color': '#E8F4FD'
            })
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            currency_format = workbook.add_format({'num_format': '#,##0.00'})
            
            # Headers
            worksheet.merge_range('A1:H1', f'Account Statement - {self.partner_id.name}', header_format)
            worksheet.write('A2', 'Period:', subheader_format)
            worksheet.write('B2', f'{self.date_from} to {self.date_to}')
            worksheet.write('A3', 'Account Filter:', subheader_format)
            worksheet.write('B3', dict(self._fields['account_type_filter'].selection)[self.account_type_filter])
            
            # Summary
            worksheet.write('A5', 'Total Debit:', subheader_format)
            worksheet.write('B5', self.total_debit, currency_format)
            worksheet.write('A6', 'Total Credit:', subheader_format)
            worksheet.write('B6', self.total_credit, currency_format)
            worksheet.write('A7', 'Balance:', subheader_format)
            worksheet.write('B7', self.balance, currency_format)
            
            # Column headers
            headers = ['Date', 'Account', 'Label', 'Debit', 'Credit', 'Running Balance']
            for col, header in enumerate(headers):
                worksheet.write(8, col, header, subheader_format)
            
            # Data rows
            row = 9
            for line in self.line_ids:
                worksheet.write(row, 0, line.date, date_format)
                worksheet.write(row, 1, f"{line.account_code} {line.account_name}")
                worksheet.write(row, 2, line.label)
                worksheet.write(row, 3, line.debit, currency_format)
                worksheet.write(row, 4, line.credit, currency_format)
                worksheet.write(row, 5, line.running_balance, currency_format)
                row += 1
            
            # Column widths
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 30)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:F', 15)
            
            workbook.close()
            output.seek(0)
            encoded_file = base64.b64encode(output.read())
            output.close()

            filename = f'Account_Statement_{self.partner_id.name}_{self.date_from}_{self.date_to}.xlsx'
            attachment = self.env['ir.attachment'].sudo().create({
                'name': filename,
                'type': 'binary',
                'datas': encoded_file,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        except Exception as e:
            _logger.error("Excel generation error: %s", str(e))
            raise UserError(_("Error generating Excel file: %s") % str(e))

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

        # Create statement lines (include all fields for full traceability)
        for line in self.line_ids:
            self.env['account.statement.line'].create({
                'statement_id': statement.id,
                'date': line.date,
                'account_name': line.account_name,
                'account_code': line.account_code,
                'label': line.label,
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
    date = fields.Date(string='Date')
    account_name = fields.Char(string='Account')
    account_code = fields.Char(string='Account Code')
    label = fields.Char(string='Label')
    debit = fields.Monetary(string='Debit', currency_field='currency_id')
    credit = fields.Monetary(string='Credit', currency_field='currency_id')
    running_balance = fields.Monetary(string='Running Balance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='wizard_id.currency_id', store=True)
