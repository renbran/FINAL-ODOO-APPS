{
    'name': 'Real Estate Deal Tracking',
    'version': '1.0.1',
    'category': 'Sales/Real Estate',
    'summary': 'Track real estate deals across sales orders and invoices',
    'description': """
Real Estate Deal Tracking Module
================================

This module adds comprehensive deal tracking fields to sales orders and invoices:

Features:
- Booking date tracking
- Developer commission management
- Buyer information
- Project and unit tracking
- Deal ID management
- Sale value tracking

All fields are open for creation without domain restrictions and use uniform naming conventions.
    """,
    'depends': ['sale', 'account', 'le_sale_type'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}