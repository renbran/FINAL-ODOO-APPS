# -*- coding: utf-8 -*-
{
    'name': 'Advanced Commission Management',
    'version': '17.0.1.0.0',
    'summary': 'Complete sales commission management system',
    'description': """
Advanced Commission Management System
===================================

A comprehensive solution for managing sales commissions in Odoo.

Key Features:
------------
* Multi-level commission structure (Brokers, Agents, Managers, Directors)
* External and internal commission tracking
* Flexible commission calculation methods
* Commission approval workflow
* Detailed commission reports
* Commission payment tracking
* Integration with sales and accounting

This module provides a complete system for:
-----------------------------------------
* Setting up commission rules and rates
* Calculating commissions automatically
* Managing commission payments
* Tracking commission history
* Generating commission reports
* Managing commission approvals
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales/Commission',
    'sequence': 1,
    'application': True,
    'installable': True,
    'auto_install': False,
    'depends': [
        'sale',
        'hr',
        'account',
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
    'images': [
        'static/description/banner.png',
        'static/description/icon.png'
    ],
    'license': 'LGPL-3',
}