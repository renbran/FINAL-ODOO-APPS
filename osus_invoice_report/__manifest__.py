{
    'name': 'OSUS Invoice Report',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Custom invoice reports and deal tracking for OSUS',
    'description': """
        This module adds custom invoice reports and deal tracking functionality:
        * Custom invoice, bill, and receipt printing
        * Deal tracking fields on invoices
        * QR code generation for documents
        * Enhanced views for property deals
    """,
    'depends': [
        'base',
        'account',
        'sale',
        'product'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
