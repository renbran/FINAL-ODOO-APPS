# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Mates, Walnut Software Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request
import json
from odoo.exceptions import UserError
import io
import xlsxwriter
from odoo.tools.misc import xlsxwriter
import base64


class DynamicReportController(http.Controller):
    """Controller for dynamic account reports"""
    
    @http.route('/dynamic_reports/dynamic_reports_report', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report(self, report_id, **data):
        """
        Generate report based on report_id and provided data.

        Args:
            report_id (str): ID of the report to generate
            data (dict): Additional data for report generation

        Returns:
            http.Response: Response containing the generated report
        """
        uid = request.session.uid
        report_obj = request.env['account.general.ledger']
        if report_id == 'general_ledger':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['account.general.ledger'].with_user(uid)
        elif report_id == 'partner_ledger':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['account.partner.ledger'].with_user(uid)
        elif report_id == 'trial_balance':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['account.trial.balance'].with_user(uid)
        elif report_id == 'aged_payable':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['aged.payable.report'].with_user(uid)
        elif report_id == 'aged_receivable':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['aged.receivable.report'].with_user(uid)
        elif report_id == 'tax_report':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['tax.report'].with_user(uid)
        elif report_id == 'balance_sheet':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['dynamic.balance.sheet.report'].with_user(uid)
        elif report_id == 'cash_flow':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['cash.book.report'].with_user(uid)
        elif report_id == 'bank_book':
            report_data = json.loads(data.get('options'))
            report_obj = request.env['bank.book.report'].with_user(uid)

        try:
            # Generate the report
            report_values = report_obj.get_dynamic_xlsx_report(report_data, None, None, None)
            response = request.make_response(
                base64.b64decode(report_values['file']),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{report_values["file_name"]}"')
                ]
            )
            return response
        except Exception as e:
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': str(e)
            }
            return request.make_response(json.dumps(error))
