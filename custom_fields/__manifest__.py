{
    'name': 'Custom Fields',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        'data/cleanup_old_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/custom_fields_list_search_views.xml',
    ],
    'installable': True,
    'application': False,
}