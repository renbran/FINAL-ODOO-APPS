{
    'name': 'Account Statement',
    'version': '17.0.1.0.0',
    'summary': 'Module for managing account statements',
    'category': 'Accounting',
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_statement_views.xml',
        'views/account_statement_wizard_views.xml',
        'report/account_statement_report_template.xml',
        'report/account_statement_report_action.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}