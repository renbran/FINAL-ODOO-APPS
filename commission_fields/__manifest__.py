# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Management',
    'version': '17.0',
    'summary': 'Comprehensive commission management for sales',
    'description': """
        This module provides advanced commission management capabilities
        for sales teams including internal and external commission tracking,
        calculation, and reporting.
        
        Features:
        - Commission tracking for sales orders
        - Internal and external commission management
        - Broker commission handling
        - Commission payment tracking
        - Advanced reporting
        - Security groups and access rights
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales',
    'depends': [
        'sale_management',
        'hr',
        'account',
        'purchase',
        'product',
        'commission_calculation',  # Added dependency for integration
    ],
    'data': [
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        'data/commission_data.xml',
        'views/menu_items.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/account_move_out_invoice_tree.xml',
        'views/project_unit_views.xml',
        'report/commission_report_templates.xml',
        'report/commission_report_actions.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}