{
    'name': 'Custom Fields',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': False,  # DISABLED: Functionality merged into osus_invoice_report
    'application': False,
}