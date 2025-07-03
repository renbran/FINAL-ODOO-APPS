{
    'name': 'Real Estate Deal Management',
    'version': '17.0.1.0.0',
    'summary': 'Comprehensive deal tracking for real estate transactions',
    'description': """
Real Estate Deal Management Module
=================================

This module provides comprehensive deal tracking capabilities for real estate transactions:

Features:
* Deal information tracking on sales orders and invoices
* Buyer management and project-unit relationships
* Developer commission tracking
* Booking date management
* Sale order type integration
* Professional UI with organized tabs

Models Extended:
* sale.order - Added deal tracking fields
* account.move - Added deal tracking fields

Fields Added:
* Buyer (Customer purchasing property)
* Project (Product template representing project)
* Unit (Specific property unit)
* Deal Reference (Unique deal identifier)
* Booking Date (When deal was booked)
* Sale Value (Property sale value)
* Developer Commission (Commission percentage)
* Sale Order Type (From le_sale_type module)
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osus.ae',
    'category': 'Real Estate',
    'depends': ['sale', 'account', 'le_sale_type'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}