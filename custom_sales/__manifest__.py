# -*- coding: utf-8 -*-
{
    'name': 'Custom Sales Module',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Custom Sales Order Management',
    'description': '''
        Custom Sales Module for specialized sales order handling
        - Custom sales order views
        - Enhanced sales workflows
        - Custom fields and logic
    ''',
    'author': 'OSUS Development Team',
    'website': 'https://www.osus.com',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'stock',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/custom_sales_order_views.xml',
        'views/custom_sales_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
