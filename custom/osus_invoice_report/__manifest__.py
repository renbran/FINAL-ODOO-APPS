{
<<<<<<< HEAD
    'name': 'OSUS Invoice Report',
    'version': '17.0.1.0.0',
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
    'depends': ['account', 'base', 'sale'],
    'external_dependencies': {
        'python': ['qrcode', 'num2words'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/report_invoice.xml',
=======
    'name': 'Custom Accounting Reports',
    'version': '17.0.1.0.0',
    'summary': 'Custom Invoice, Bill and Receipt Reports',
    'description': 'UK-formatted documents with UAE receipt standard',
    'category': 'Accounting/Accounting',
    'author': 'Your Company',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/report_bill.xml',
        'views/report_receipt.xml',
>>>>>>> 50419ea8 (QUICK INSTALL)
    ],
    'assets': {
        'web.report_assets_pdf': [
            'osus_invoice_report/static/src/css/report_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
<<<<<<< HEAD
    'auto_install': False,
=======
>>>>>>> 50419ea8 (QUICK INSTALL)
}