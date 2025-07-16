# -*- coding: utf-8 -*-
# This module is under copyright of 'OdooElevate'
{
    'name': 'OSUS Executive Sales Dashboard',
    'version': '17.0.0.1.1',
    'category': 'Sales',
    'summary': 'Custom dashboard for yearly sales report.',
    'description': """
        Enhanced Executive Sales Dashboard with modern visualizations and business intelligence.
        
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
        
        Transform your sales data into beautiful, actionable insights with this comprehensive
        executive dashboard using booking_date and sale_value fields from the osus_invoice_report module.
    """,
    'author': 'Sheikh Muhammad Saad, OdooElevate',
    'website': 'https://odooelevate.odoo.com/',
    'depends': ['web', 'sale_management', 'osus_invoice_report', 'le_sale_type'],
    'data': [
        'data/sale_order_data.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js',
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
