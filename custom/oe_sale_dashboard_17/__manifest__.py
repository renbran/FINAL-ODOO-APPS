# -*- coding: utf-8 -*-
# This module is under copyright of 'OdooElevate'
{
    'name': 'OSUS Sales Dashboard',
    'version': '17.0.0.1.1',
    'category': 'Sales',
    'summary': 'Custom dashboard for yearly sales report.',
    'description': """
        Enhanced sales dashboard module with advanced filtering and field selection capabilities.
        
        Key Features:
        - Date range filtering (start date to end date) 
        - Booking date reference instead of order date
        - Amount field selection (Total Amount vs Sale Value)
        - Simplified company-based reporting
        - Real-time dashboard updates
        - Responsive design with modern UI
        
        Comprehensive dashboard for sales analysis using booking_date and sale_value fields
        from the osus_invoice_report module.
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
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
