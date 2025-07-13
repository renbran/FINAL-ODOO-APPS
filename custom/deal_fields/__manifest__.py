{
    'name': 'Custom Fields',
    'version': '1.0',
    'depends': ['sale', 'account', 'le_sale_type'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/custom_account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}