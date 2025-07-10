{
    'name': 'OSUS Invoice Report',
    'version': '17.0.1.0.1',
    'summary': 'Professional UAE Tax Invoice Reports for Real Estate Commission',
    'description': '''
        Professional Tax Invoice Reports
        ================================
        - UAE VAT compliant invoice layout
        - Real estate commission specific fields
        - UK date format support
        - Amount in words conversion
        - Professional styling with Bootstrap 5
        - Multi-company support
        - Inheritance-safe implementation
    ''',
    'category': 'Accounting/Accounting',
    'author': 'OSUS Real Estate',
    'website': 'https://www.osus.ae',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/report_bills.xml',
        'views/report_receipt.xml',
        'views/report_action_invoice.xml',
        'views/report_action_bill.xml',
        'data/report_paperformat.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'osus_invoice_report/static/src/css/report_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'auto_install': False,
}