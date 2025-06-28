# -*- coding: utf-8 -*-
{
    'name': 'Sales Commission Management',
    'version': '17.0.1.0.0',
    'summary': 'Comprehensive commission management for sales',
    'description': """
        This module provides advanced commission management capabilities
        for sales teams including internal and external commission tracking,
        calculation, and reporting.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales',
    'depends': [
        'sale',
        'hr',
        'account',
        'report_xlsx',
        'base',
        'web'
    ],
    'data': [
        # Security
        'security/commission_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/commission_data.xml',
        # Reports
        'report/commission_report_templates.xml',
        'report/commission_report_actions.xml',
        # Views
        'views/sale_order_views.xml',
        'views/menu_items.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_out_invoice_tree.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'commission_fields/static/src/css/commission_styles.css',
        ],
        'web.report_assets_common': [
            'commission_fields/static/src/css/commission_report.css',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}