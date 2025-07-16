# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Mates, Walnut Software Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Odoo 17 Dynamic Accounting Reports',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Dynamic Accounting Reports compatible with OM Accounting',
    'description': """
        This module provides dynamic accounting reports compatible with Odoo 17 
        standard accounting module. It includes General Ledger, Trial Balance, 
        Balance Sheet, Profit and Loss, Cash Book, Partner Ledger, Aged Payable, 
        Aged Receivable, Bank book, and Tax Reports.
    """,
    'sequence': '1',
    'website': 'https://www.walnutit.com',
    'author': 'Odoo Mates, Walnut Software Solutions',
    'maintainer': 'Odoo Mates, Walnut Software Solutions',
    'license': 'LGPL-3',
    'support': 'odoomates@gmail.com',
    'depends': [
        'account',
        'accounting_pdf_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/report_views.xml',
        'report/trial_balance.xml',
        'report/general_ledger_templates.xml',
        'report/financial_report_template.xml',
        'report/partner_ledger_templates.xml',
        'report/financial_reports_views.xml',
        'report/balance_sheet_report_templates.xml',
        'report/bank_book_templates.xml',
        'report/aged_payable_templates.xml',
        'report/aged_receivable_templates.xml',
        'report/tax_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'om_dynamic_reports/static/src/xml/general_ledger.xml',
            'om_dynamic_reports/static/src/css/report_styles.css',
            'om_dynamic_reports/static/src/js/general_ledger.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
