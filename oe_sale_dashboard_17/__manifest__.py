# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard - Odoo 17',
    'version': '17.0.1.6.0',
    'category': 'Sales',
    'summary': 'Enhanced Sales Dashboard with Clean Model Architecture (#800020 Maroon Theme)',
    'description': """
Sales Dashboard for Odoo 17 - Fixed Model Architecture Edition
==============================================================

This module provides a comprehensive sales dashboard with FIXED model architecture:
* NO INHERITANCE of sale.order model structure - only adds dashboard methods
* Visual analytics with #800020 maroon primary color theme
* Interactive Chart.js visualizations with brand color palette  
* Monthly fluctuation data with white fonts and light gold accents
* Sales performance metrics with professional styling
* Deal analysis and forecasting with accessibility compliance
* Mobile-responsive design optimized for brand presentation
* Real-time data updates with validated field mappings
* CLEAN SEPARATION between dashboard and core sale order functionality

Architecture Fixes:
-------------------
* Removed problematic _inherit that modified sale.order model
* Created isolated dashboard methods that don't affect sales forms
* Ensured sales order forms remain unchanged and functional
* Clean client-side action system for dashboard display
* Proper model separation to prevent conflicts

Features:
---------
* Interactive charts with custom brand colors
* Sales pipeline visualization in maroon/gold theme
* Performance KPIs with white text contrast
* Monthly/quarterly reports with professional styling
* Export capabilities with brand consistency
* Multi-currency support with enhanced formatting

Custom Branding:
----------------
* Primary: #800020 (Deep Maroon/Burgundy)
* Accent: #FFD700 (Light Gold)  
* Text: White fonts for optimal readability
* Charts: Brand-specific color schemes
* Accessibility: WCAG compliant contrast ratios
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
            ('include', 'web._assets_helpers'),
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js',
            'oe_sale_dashboard_17/static/src/css/dashboard.css',
            'oe_sale_dashboard_17/static/src/xml/sales_dashboard_main.xml',
            'oe_sale_dashboard_17/static/src/js/sales_dashboard.js',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.svg'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
