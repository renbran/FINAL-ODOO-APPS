# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Mates, Walnut Software Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Odoo 17 Dynamic Accounting Reports',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Dynamic General Ledger Report for Odoo 17',
    'description': """
        This module provides dynamic General Ledger report compatible with Odoo 17 
        standard accounting module. 
        
        Currently implemented:
        - General Ledger Report with dynamic filtering and drill-down capabilities
        
        Note: This is a simplified version. For complete reporting suite including
        Trial Balance, Balance Sheet, Profit & Loss, etc., use the 
        'dynamic_accounts_report' module instead.
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
