{
    'name': 'Advanced Commission Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Comprehensive commission calculation and processing system',
    'description': """
        This module provides:
        - Advanced commission calculation with external/internal groups
        - Automatic PO generation for commissions
        - Deal information tracking
        - Commission payment processing
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'base',
        'sale',
        'purchase',
        'account',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/commission_calculation_views.xml',
        'views/commission_calculation_menus.xml',
        'data/commission_product_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}