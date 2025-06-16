# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Management',
    'version': '1.0',
    'summary': 'Comprehensive commission management for sales',
    'description': """
        This module provides advanced commission management capabilities
        for sales teams including internal and external commission tracking,
        calculation, and reporting.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales',
    'depends': ['sale', 'hr', 'account'],
    'data': [
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        'data/commission_data.xml',
        'views/sale_order_views.xml',
        'views/project_unit_views.xml',
        'views/menu_items.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}