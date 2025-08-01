# -*- coding: utf-8 -*-
{
    'name': 'OSUS Executive Sales Dashboard',
    'version': '17.0.1.0.0',
    'summary': 'Executive Sales Dashboard with Charts and KPIs',
    'description': '''
        Executive Sales Dashboard Module for Odoo 17
        
        Features:
        - Interactive sales charts using Chart.js
        - Real-time KPI metrics
        - Monthly fluctuation analysis
        - Sales type distribution
        - Mobile-responsive design
        - Fallback compatibility system
        
        This module provides comprehensive sales analytics with modern charting
        capabilities and robust error handling.
    ''',
    'category': 'Sales/Dashboard',
    'author': 'OSUS Development Team',
    'website': 'https://www.osus.com',
    'depends': [
        'base',
        'web', 
        'sale',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Chart.js CDN with fallback
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js',
            
            # Local fallback and compatibility
            'oe_sale_dashboard_17/static/src/js/chart.fallback.js',
            'oe_sale_dashboard_17/static/src/js/simple-chart.js',
            'oe_sale_dashboard_17/static/src/js/field_mapping.js',
            'oe_sale_dashboard_17/static/src/js/compatibility.js',
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            
            # Templates
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
            
            # Styles
            'oe_sale_dashboard_17/static/src/scss/dashboard.scss',
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
}
