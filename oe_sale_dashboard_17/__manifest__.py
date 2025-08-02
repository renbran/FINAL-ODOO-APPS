# -*- coding: utf-8 -*-
{
    'name': 'Enhanced Sales Dashboard 17',
    'version': '1.0.0',
    'category': 'Sales',
    'sequence': 10,
    'summary': 'Production-ready comprehensive sales dashboard with advanced analytics',
    'description': """
Enhanced Sales Dashboard for Odoo 17
====================================

This module provides a comprehensive, production-ready sales dashboard with advanced analytics and reporting capabilities.

Key Features:
* Real-time sales performance tracking
* Advanced KPI calculations (conversion rates, pipeline velocity, revenue growth)
* Interactive charts and visualizations
* Top performers ranking (agents and agencies)
* Sales type categorization and filtering
* Enhanced error handling and data validation
* Export functionality
* Auto-refresh capabilities
* Mobile-responsive design
* Sample data fallback for demonstration

Technical Features:
* Optimized database queries with batching
* Field existence validation for cross-module compatibility
* Multiple sales type model support (le.sale.type, sale.order.type)
* Comprehensive error handling and logging
* Performance monitoring and health checks
* Data integrity validation
* Cache management
* Production-ready architecture

Compatibility:
* Odoo 17.0+
* Works with standard sale module
* Compatible with custom sales type modules
* Supports commission tracking modules
* Handles booking date fields from custom modules

Installation:
1. Copy module to your addons directory
2. Update apps list
3. Install the module
4. Navigate to Sales > Dashboard to access

Requirements:
* sale module (auto-installed)
* Chart.js (loaded from CDN)
* FontAwesome icons (recommended)

Support:
For support and customization, please contact your Odoo implementation specialist.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'account',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_menu.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/css/dashboard.scss',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml'
        ]
    },
    'external_dependencies': {
        'javascript': [
            'Chart.js'  # Loaded from CDN
        ]
    },
    'images': [
        'static/description/icon.png',
        'static/description/dashboard_screenshot.png'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 0.00,
    'currency': 'EUR',
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'bootstrap': True,
    'cloc_exclude': [
        'static/lib/**/*'
    ]
}