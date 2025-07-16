# -*- coding: utf-8 -*-
# This module is under copyright of 'OdooElevate'
{
    'name': 'OSUS Executive Sales Dashboard (Safe Install)',
    'version': '17.0.0.1.2',
    'category': 'Sales',
    'summary': 'Custom dashboard for yearly sales report - Safe installation version.',
    'description': """
        Enhanced Executive Sales Dashboard with modern visualizations and business intelligence.
        
        This is a safe installation version that includes only essential dependencies
        to avoid foreign key constraint issues during installation.
        
        Key Features:
        - Interactive Chart.js powered visualizations
        - Executive-level KPI cards with gradient designs
        - Real-time sales funnel analysis
        - Enhanced date range filtering with booking_date reference
        - Beautiful modern UI with animated components
        - Responsive design optimized for all devices
        - Advanced revenue distribution charts
        - Sales performance trend analysis
        - Professional color-coded tables and cards
        - Top 10 performing agents and agencies dashboard
        
        Transform your sales data into beautiful, actionable insights with this comprehensive
        executive dashboard.
    """,
    'author': 'Sheikh Muhammad Saad, OdooElevate',
    'website': 'https://odooelevate.odoo.com/',
    'depends': ['web', 'sale'],  # Minimal dependencies
    'data': [
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oe_sale_dashboard_17/static/src/css/dashboard.scss',
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
}
