# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard - Odoo 17',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Advanced Sales Dashboard with Analytics and Visual Reports',
    'description': """
Sales Dashboard for Odoo 17
===========================

This module provides a comprehensive sales dashboard with:
* Visual analytics and charts
* Monthly fluctuation data
* Sales performance metrics
* Deal analysis and forecasting
* Mobile-responsive design
* Real-time data updates

Features:
---------
* Interactive charts and graphs
* Sales pipeline visualization
* Performance KPIs
* Monthly/quarterly reports
* Export capabilities
* Multi-currency support
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_dashboard_views.xml',
        'views/sales_dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oe_sale_dashboard_17/static/src/scss/dashboard.scss',
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
            'oe_sale_dashboard_17/static/src/css/dashboard_enhanced.css',
            'oe_sale_dashboard_17/static/src/js/chart.fallback.js',
            'oe_sale_dashboard_17/static/src/js/simple-chart.js',
            'oe_sale_dashboard_17/static/src/js/sales_dashboard.js',
            'oe_sale_dashboard_17/static/src/xml/sales_dashboard_main.xml',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
