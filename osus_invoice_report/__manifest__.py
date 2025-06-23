# -*- coding: utf-8 -*-
{
    'name': 'OSUS Invoice Report',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Custom Invoice and Bill Reports for OSUS Properties',
    'description': """
        Custom Invoice and Bill Reports for OSUS Properties
        ===================================================
        
        This module provides custom invoice and bill report templates for OSUS Properties
        with proper formatting and branding.
        
        Features:
        - Custom Invoice Report with OSUS branding
        - Custom Bill Report with OSUS branding
        - Print buttons in invoice form view
        - Professional PDF output
    """,
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'depends': ['base', 'account'],
    'data': [
        'views/account_move_views.xml',
        'reports/invoice_report.xml',
        'reports/bill_report.xml',
        'reports/report_actions.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}