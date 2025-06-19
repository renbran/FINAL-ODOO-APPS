{
    'name': 'Account Statement',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Generate Account Statements for Partners',
    'description': """
        Account Statement Module
        ========================
        This module allows you to generate account statements for partners
        showing all invoices and payments within a date range.

        Features:
        - Generate PDF reports
        - Export to Excel
        - Filter by partner and date range
        - Show running balance
        - Comprehensive partner information
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'account', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'views/account_statement_wizard_views.xml',
        'views/account_statement_views.xml',
        'report/account_statement_report_action.xml',
        'report/account_statement_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}