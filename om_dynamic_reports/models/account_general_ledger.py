# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Mates, Walnut Software Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import io
import json
import calendar
import base64
from dateutil.relativedelta import relativedelta
import xlsxwriter
from odoo import api, fields, models
from datetime import datetime
from odoo.tools import date_utils


class AccountGeneralLedger(models.TransientModel):
    """For creating General Ledger report"""
    _name = 'account.general.ledger'
    _description = 'General Ledger Report'

    @api.model
    def view_report(self, option, tag):
        """
        Retrieve general ledger report data based on options and tags.

        :param option: The options to filter the report data.
        :type option: str

        :param tag: The tag to filter the report data.
        :type tag: str

        :return: A dictionary containing the general ledger report data.
        :rtype: dict
        """
        r = self.env['account.general.ledger'].search([('id', '=', option[0])])
        date_from = datetime.strptime(option[1], '%Y-%m-%d').date()
        date_to = datetime.strptime(option[2], '%Y-%m-%d').date()
        state = option[3]
        journals = []
        if option[4]:
            journals = self.env['account.journal'].search(
                [('id', 'in', option[4])]).mapped('name')
        accounts = []
        if option[5]:
            accounts = self.env['account.account'].search(
                [('id', 'in', option[5])]).mapped('name')
        analytic = []
        if option[6]:
            analytic = self.env['account.analytic.account'].search(
                [('id', 'in', option[6])]).mapped('name')
        company_id = self.env.company
        company_currency_id = company_id.currency_id
        move_lines = {
            'move_lines': [],
            'journals': ','.join([str(x) for x in journals]),
            'accounts': ','.join([str(x) for x in accounts]),
            'analytic': ','.join([str(x) for x in analytic]),
            'company_currency_id': company_currency_id.id,
            'company_currency_symbol': company_currency_id.symbol,
            'company_currency_position': company_currency_id.position,
            'date_from': date_from.strftime('%d-%m-%Y'),
            'date_to': date_to.strftime('%d-%m-%Y'),
            'state': state,
        }
        domain = [('date', '>=', date_from),
                  ('date', '<=', date_to),
                  ('move_id.state', '!=', 'cancel')
                  ]
        if option[4]:
            domain.append(('journal_id', 'in', option[4]))
        if option[5]:
            domain.append(('account_id', 'in', option[5]))
        if option[6]:
            domain.append(('analytic_distribution', '!=', False))

        if state == 'posted':
            domain.append(('move_id.state', '=', 'posted'))

        move_lines['move_lines'] = self.get_move_lines(domain)
        return move_lines

    def get_move_lines(self, domain):
        """Get move lines for the given domain."""
        move_lines = self.env['account.move.line'].search(domain)
        result = []
        for line in move_lines:
            result.append({
                'id': line.id,
                'date': line.date.strftime('%d-%m-%Y'),
                'name': line.name,
                'ref': line.move_id.name,
                'partner': line.partner_id.name if line.partner_id else '',
                'account_id': line.account_id.name,
                'account_code': line.account_id.code,
                'debit': line.debit,
                'credit': line.credit,
                'balance': line.balance,
                'journal': line.journal_id.name,
                'currency': line.company_currency_id.symbol,
                'position': line.company_currency_id.position,
                'move_id': line.move_id.id,
            })
        return result

    @api.model
    def create_general_ledger(self, option):
        """Create general ledger report."""
        report_data = self.view_report(option, '')
        return report_data

    def get_filter_values(self, option):
        """Get filter values from options."""
        data = {}
        date_from = datetime.strptime(option[1], '%Y-%m-%d').date()
        date_to = datetime.strptime(option[2], '%Y-%m-%d').date()
        data['date_from'] = date_from.strftime('%d-%m-%Y')
        data['date_to'] = date_to.strftime('%d-%m-%Y')
        data['state'] = option[3]
        data['journals'] = option[4]
        data['accounts'] = option[5]
        data['analytics'] = option[6]
        return data

    def get_dynamic_xlsx_report(self, options, response, report_data, dfr_data):
        """Generate Excel report for general ledger."""
        from_date = datetime.strptime(options[1], '%Y-%m-%d').date()
        to_date = datetime.strptime(options[2], '%Y-%m-%d').date()
        state = options[3]
        journals = []
        if options[4]:
            journals = self.env['account.journal'].search(
                [('id', 'in', options[4])]).mapped('name')
        accounts = []
        if options[5]:
            accounts = self.env['account.account'].search(
                [('id', 'in', options[5])]).mapped('name')
        
        # Create Excel workbook
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('General Ledger')
        
        # Define formats
        title = workbook.add_format({'font_size': 16, 'bold': True, 'align': 'center'})
        header = workbook.add_format({'font_size': 14, 'bold': True, 'align': 'center'})
        date_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        cell_format = workbook.add_format({'font_size': 12, 'align': 'left'})
        number_format = workbook.add_format({'font_size': 12, 'align': 'right', 'num_format': '#,##0.00'})
        
        # Write headers
        sheet.merge_range(0, 0, 0, 9, 'General Ledger Report', title)
        sheet.merge_range(1, 0, 1, 9, f'From {from_date.strftime("%d-%m-%Y")} to {to_date.strftime("%d-%m-%Y")}', header)
        
        if journals:
            sheet.merge_range(2, 0, 2, 9, f'Journals: {", ".join(journals)}', cell_format)
        if accounts:
            sheet.merge_range(3, 0, 3, 9, f'Accounts: {", ".join(accounts)}', cell_format)
        if state == 'posted':
            sheet.merge_range(4, 0, 4, 9, 'State: Posted Only', cell_format)
        else:
            sheet.merge_range(4, 0, 4, 9, 'State: All Entries', cell_format)
        
        # Column headers
        row_pos = 6
        sheet.write(row_pos, 0, 'Date', header)
        sheet.write(row_pos, 1, 'JRNL', header)
        sheet.write(row_pos, 2, 'Account', header)
        sheet.write(row_pos, 3, 'Ref', header)
        sheet.write(row_pos, 4, 'Partner', header)
        sheet.write(row_pos, 5, 'Name', header)
        sheet.write(row_pos, 6, 'Debit', header)
        sheet.write(row_pos, 7, 'Credit', header)
        sheet.write(row_pos, 8, 'Balance', header)
        
        # Write data rows
        row_pos += 1
        for line in report_data['move_lines']:
            sheet.write(row_pos, 0, line['date'], date_format)
            sheet.write(row_pos, 1, line['journal'], cell_format)
            sheet.write(row_pos, 2, f"{line['account_code']} {line['account_id']}", cell_format)
            sheet.write(row_pos, 3, line['ref'], cell_format)
            sheet.write(row_pos, 4, line['partner'], cell_format)
            sheet.write(row_pos, 5, line['name'], cell_format)
            sheet.write(row_pos, 6, line['debit'], number_format)
            sheet.write(row_pos, 7, line['credit'], number_format)
            sheet.write(row_pos, 8, line['balance'], number_format)
            row_pos += 1
        
        # Finalize workbook
        workbook.close()
        output.seek(0)
        
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'account.general.ledger',
                'options': json.dumps(options),
                'output_format': 'xlsx',
                'report_name': 'General Ledger',
            },
            'report_type': 'xlsx',
            'file': base64.b64encode(output.read()),
            'file_name': 'General Ledger.xlsx',
        }
