{
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
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}