# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import io
import json
import xlsxwriter
import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AgePayableReport(models.TransientModel):
    """For creating Age Payable report"""
    _name = 'age.payable.report'
    _description = 'Aged Payable Report'

    def _calculate_date_difference(self, date_maturity, today):
        """Helper method to calculate date difference handling various date formats"""
        if not date_maturity:
            return 0
        try:
            if isinstance(date_maturity, str):
                date_maturity = datetime.datetime.strptime(date_maturity, '%Y-%m-%d').date()
            if isinstance(date_maturity, datetime.date):
                return (today - date_maturity).days
        except (ValueError, TypeError):
            pass
        return 0

    def _get_move_lines(self, partner_id, paid_moves):
        """Helper method to get move lines for a partner with proper filtering"""
        move_lines = paid_moves.filtered(lambda r: r.partner_id.id == partner_id.id)
        return move_lines.read([
            'name', 'move_name', 'date', 'amount_currency', 'account_id',
            'date_maturity', 'currency_id', 'credit', 'move_id'
        ])

    def _safe_get_currency(self, currency_data):
        """Safely get currency name from currency data"""
        if currency_data and isinstance(currency_data, (list, tuple)) and len(currency_data) > 1:
            return currency_data[1]
        return ''

    @api.model
    def view_report(self):
        """
        Generate a report with move line data categorized by partner and credit
        difference.
        Returns:
            dict: Dictionary containing move line data categorized by partner
                  names. Each partner's data includes credit amounts and credit
                  differences based on days between maturity date and today. The
                  'partner_totals' key contains summary data for each partner.
        """
        partner_total = {}
        move_line_list = {}
        paid = self.env['account.move.line'].search([
            ('parent_state', '=', 'posted'),
            ('account_type', '=', 'liability_payable'),
            ('reconciled', '=', False)
        ])
        
        currency = self.env.company.currency_id
        partner_ids = paid.mapped('partner_id')
        today = fields.Date.today()

        for partner_id in partner_ids:
            move_line_data = self._get_move_lines(partner_id, paid)
            
            # Process each move line
            for val in move_line_data:
                date_maturity = val.get('date_maturity', False)
                diffrence = self._calculate_date_difference(date_maturity, today)
                
                # Calculate aging buckets
                val['diff0'] = val['credit'] if diffrence <= 0 else 0.0
                val['diff1'] = val['credit'] if 0 < diffrence <= 30 else 0.0
                val['diff2'] = val['credit'] if 30 < diffrence <= 60 else 0.0
                val['diff3'] = val['credit'] if 60 < diffrence <= 90 else 0.0
                val['diff4'] = val['credit'] if 90 < diffrence <= 120 else 0.0
                val['diff5'] = val['credit'] if diffrence > 120 else 0.0

            # Store move lines for this partner
            move_line_list[partner_id.name] = move_line_data
            
            # Calculate totals for this partner
            credit_sum = sum(val['credit'] for val in move_line_data)
            partner_total[partner_id.name] = {
                'credit_sum': credit_sum,
                'diff0_sum': round(sum(val['diff0'] for val in move_line_data), 2),
                'diff1_sum': round(sum(val['diff1'] for val in move_line_data), 2),
                'diff2_sum': round(sum(val['diff2'] for val in move_line_data), 2),
                'diff3_sum': round(sum(val['diff3'] for val in move_line_data), 2),
                'diff4_sum': round(sum(val['diff4'] for val in move_line_data), 2),
                'diff5_sum': round(sum(val['diff5'] for val in move_line_data), 2),
                'currency_id': currency.id,
                'partner_id': partner_id.id
            }

        move_line_list['partner_totals'] = partner_total
        return move_line_list

    @api.model
    def get_filter_values(self, date, partner):
        """
        Retrieve filtered move line data based on date and partner(s).
        Parameters:
            date (str): Date for filtering move lines (format: 'YYYY-MM-DD').
            partner (list): List of partner IDs to filter move lines for.
        Returns:
            dict: Dictionary with filtered move line data organized by partner
                  names. Includes credit amount categorization based on days
                  difference. Contains partner-wise summary under
                  'partner_totals' key.
        """
        partner_total = {}
        move_line_list = {}
        if date:
            paid = self.env['account.move.line'].search(
                [('parent_state', '=', 'posted'),
                 ('account_type', '=', 'liability_payable'),
                 ('reconciled', '=', False), ('date', '<=', date)])
        else:
            paid = self.env['account.move.line'].search(
                [('parent_state', '=', 'posted'),
                 ('account_type', '=', 'liability_payable'),
                 ('reconciled', '=', False)])
        currency_id = self.env.company.currency_id.symbol
        if partner:
            partner_ids = self.env['res.partner'].search(
                [('id', 'in', partner)])
        else:
            partner_ids = paid.mapped('partner_id')
        today = fields.Date.today()
        for partner_id in partner_ids:
            move_line_ids = paid.filtered(
                lambda rec: rec.partner_id in partner_id)
            move_line_data = move_line_ids.read(
                ['name', 'move_name', 'date', 'amount_currency', 'account_id',
                 'date_maturity', 'currency_id', 'credit', 'move_id'])
            for val in move_line_data:
                date_maturity = val.get('date_maturity', False)
                diffrence = self._calculate_date_difference(date_maturity, today)
                val['diff0'] = val['credit'] if diffrence <= 0 else 0.0
                val['diff1'] = val['credit'] if 0 < diffrence <= 30 else 0.0
                val['diff2'] = val['credit'] if 30 < diffrence <= 60 else 0.0
                val['diff3'] = val['credit'] if 60 < diffrence <= 90 else 0.0
                val['diff4'] = val['credit'] if 90 < diffrence <= 120 else 0.0
                val['diff5'] = val['credit'] if diffrence > 120 else 0.0
            move_line_list[partner_id.name] = move_line_data
            partner_total[partner_id.name] = {
                'credit_sum': sum(val['credit'] for val in move_line_data),
                'diff0_sum': round(sum(val['diff0'] for val in move_line_data),
                                   2),
                'diff1_sum': round(sum(val['diff1'] for val in move_line_data),
                                   2),
                'diff2_sum': round(sum(val['diff2'] for val in move_line_data),
                                   2),
                'diff3_sum': round(sum(val['diff3'] for val in move_line_data),
                                   2),
                'diff4_sum': round(sum(val['diff4'] for val in move_line_data),
                                   2),
                'diff5_sum': round(sum(val['diff5'] for val in move_line_data),
                                   2),
                'currency_id': currency_id,
                'partner_id': partner_id.id
            }
        move_line_list['partner_totals'] = partner_total
        return move_line_list

    @api.model
    def get_xlsx_report(self, data, response, report_name, report_action):
        """Generate an Excel report based on the provided data."""
        try:
            data = json.loads(data)
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
            # Get report filters
            filters = data.get('filters', {})
            end_date = filters.get('end_date', '')
            partners = filters.get('partner', [])
            
            # Create worksheet and formats
            sheet = workbook.add_worksheet()
            formats = self._get_xlsx_formats(workbook)
            
            # Set column widths
            self._set_column_widths(sheet)
            
            # Write headers
            self._write_report_headers(sheet, formats, report_name, end_date, partners)
            
            # Write data
            if data and report_action == 'dynamic_accounts_report.action_aged_payable':
                self._write_aged_payable_data(sheet, formats, data)
            
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()
            
        except Exception as e:
            _logger.error("Error generating XLSX report: %s", str(e))
            raise UserError(_("Error generating Excel report. Please try again or contact your administrator."))

    def _get_xlsx_formats(self, workbook):
        """Create and return dictionary of workbook formats"""
        return {
            'head': workbook.add_format({
                'align': 'center', 
                'bold': True, 
                'font_size': '15px'
            }),
            'sub_heading': workbook.add_format({
                'align': 'center', 
                'bold': True, 
                'font_size': '10px',
                'border': 1, 
                'bg_color': '#D3D3D3',
                'border_color': 'black'
            }),
            'filter_head': workbook.add_format({
                'align': 'center', 
                'bold': True, 
                'font_size': '10px',
                'border': 1, 
                'bg_color': '#D3D3D3',
                'border_color': 'black'
            }),
            'txt': workbook.add_format({
                'font_size': '10px', 
                'border': 1
            }).set_indent(2)
        }

    def _set_column_widths(self, sheet):
        """Set the column widths for the worksheet"""
        widths = [30, 20, 15, 15, 20, 20, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        for i, width in enumerate(widths):
            sheet.set_column(i, i, width)

    def _write_report_headers(self, sheet, formats, report_name, end_date, partners):
        """Write report headers and filters"""
                    sheet.merge_range(row, col + 6, row, col + 7, ' ',
                                      txt_name)
                    sheet.write(row, col + 8,
                                data['total'][move_line]['diff0_sum'],
                                txt_name)
                    sheet.write(row, col + 9,
                                data['total'][move_line]['diff1_sum'],
                                txt_name)
                    sheet.write(row, col + 10,
                                data['total'][move_line]['diff2_sum'],
                                txt_name)
                    sheet.write(row, col + 11,
                                data['total'][move_line]['diff3_sum'],
                                txt_name)
                    sheet.write(row, col + 12,
                                data['total'][move_line]['diff4_sum'],
                                txt_name)
                    sheet.write(row, col + 13,
                                data['total'][move_line]['diff5_sum'],
                                txt_name)
                    sheet.write(row, col + 14,
                                data['total'][move_line]['credit_sum'],
                                txt_name)
                    for rec in data['data'][move_line]:
                        row += 1
                        if not rec['name']:
                            rec['name'] = ' '
                        sheet.write(row, col, rec['move_name'] + rec['name'],
                                    txt_name)
                        sheet.write(row, col + 1, rec['date'],
                                    txt_name)
                        sheet.write(row, col + 2, rec['amount_currency'],
                                    txt_name)
                        sheet.write(row, col + 3, rec['currency_id'][1],
                                    txt_name)
                        sheet.merge_range(row, col + 4, row, col + 5,
                                          rec['account_id'][1],
                                          txt_name)
                        sheet.merge_range(row, col + 6, row, col + 7,
                                          rec['date_maturity'],
                                          txt_name)
                        sheet.write(row, col + 8, rec['diff0'], txt_name)
                        sheet.write(row, col + 9, rec['diff1'], txt_name)
                        sheet.write(row, col + 10, rec['diff2'], txt_name)
                        sheet.write(row, col + 11, rec['diff3'], txt_name)
                        sheet.write(row, col + 12, rec['diff4'], txt_name)
                        sheet.write(row, col + 13, rec['diff5'], txt_name)
                        sheet.write(row, col + 14, ' ', txt_name)
                sheet.merge_range(row + 1, col, row + 1, col + 7, 'Total',
                                  filter_head)
                sheet.write(row + 1, col + 8,
                            data['grand_total']['diff0_sum'],
                            filter_head)
                sheet.write(row + 1, col + 9,
                            data['grand_total']['diff1_sum'],
                            filter_head)
                sheet.write(row + 1, col + 10,
                            data['grand_total']['diff2_sum'],
                            filter_head)
                sheet.write(row + 1, col + 11,
                            data['grand_total']['diff3_sum'],
                            filter_head)
                sheet.write(row + 1, col + 12,
                            data['grand_total']['diff4_sum'],
                            filter_head)
                sheet.write(row + 1, col + 13,
                            data['grand_total']['diff5_sum'],
                            filter_head)
                sheet.write(row + 1, col + 14,
                            data['grand_total']['total_credit'],
                            filter_head)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
