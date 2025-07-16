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


class AccountPartnerLedger(models.TransientModel):
    """For creating Partner Ledger report"""
    _name = 'account.partner.ledger'
    _description = 'Partner Ledger Report'

    @api.model
    def get_dynamic_xlsx_report(self, options, response, report_data, dfr_data):
        """Generate the partner ledger Excel report."""
        report_name = 'Partner Ledger'
        report_file_name = 'Partner Ledger.xlsx'
        
        # Create a new workbook and add a worksheet
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True, 
            'align': 'center', 
            'font_size': 14
        })
        header_format = workbook.add_format({
            'bold': True, 
            'align': 'center', 
            'border': 1,
            'bg_color': '#D3D3D3'
        })
        cell_format = workbook.add_format({
            'border': 1
        })
        
        # Write title
        sheet.merge_range('A1:H1', report_name, title_format)
        
        # Write header
        headers = [
            'Date', 'Journal', 'Account', 'Move', 'Reference',
            'Debit', 'Credit', 'Balance'
        ]
        for col, header in enumerate(headers):
            sheet.write(2, col, header, header_format)
        
        # Example data - in actual implementation, fetch from database
        sheet.write(3, 0, "2023-01-01", cell_format)
        sheet.write(3, 1, "MISC", cell_format)
        sheet.write(3, 2, "101200 Account Receivable", cell_format)
        sheet.write(3, 3, "INV/2023/0001", cell_format)
        sheet.write(3, 4, "Customer Invoice", cell_format)
        sheet.write(3, 5, "1000.00", cell_format)
        sheet.write(3, 6, "0.00", cell_format)
        sheet.write(3, 7, "1000.00", cell_format)
        
        # Adjust column widths
        sheet.set_column('A:A', 12)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:H', 12)
        
        workbook.close()
        output.seek(0)
        
        # Return the generated Excel file
        return {
            'file': base64.b64encode(output.read()),
            'file_name': report_file_name
        }


class AccountTrialBalance(models.TransientModel):
    """For creating Trial Balance report"""
    _name = 'account.trial.balance'
    _description = 'Trial Balance Report'

    @api.model
    def get_dynamic_xlsx_report(self, options, response, report_data, dfr_data):
        """Generate the trial balance Excel report."""
        report_name = 'Trial Balance'
        report_file_name = 'Trial Balance.xlsx'
        
        # Create a new workbook and add a worksheet
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True, 
            'align': 'center', 
            'font_size': 14
        })
        header_format = workbook.add_format({
            'bold': True, 
            'align': 'center', 
            'border': 1,
            'bg_color': '#D3D3D3'
        })
        cell_format = workbook.add_format({
            'border': 1
        })
        
        # Write title
        sheet.merge_range('A1:E1', report_name, title_format)
        
        # Write header
        headers = [
            'Account Code', 'Account Name', 'Debit', 'Credit', 'Balance'
        ]
        for col, header in enumerate(headers):
            sheet.write(2, col, header, header_format)
        
        # Example data - in actual implementation, fetch from database
        sheet.write(3, 0, "101200", cell_format)
        sheet.write(3, 1, "Account Receivable", cell_format)
        sheet.write(3, 2, "1000.00", cell_format)
        sheet.write(3, 3, "0.00", cell_format)
        sheet.write(3, 4, "1000.00", cell_format)
        
        # Adjust column widths
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:E', 12)
        
        workbook.close()
        output.seek(0)
        
        # Return the generated Excel file
        return {
            'file': base64.b64encode(output.read()),
            'file_name': report_file_name
        }
