# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard - Odoo 17',
    'version': '17.0.1.6.2',
    'category': 'Sales',
    'summary': 'Enhanced Sales Dashboard - Agent & Broker Rankings with Booking Date Support (#800020 Maroon Theme)',
    'description': """
Enhanced Sales Dashboard for Odoo 17 - COMPLETELY ISOLATED EDITION  
==================================================================

⚠️  IMPORTANT: This module DOES NOT modify sale.order model or views ⚠️

This module provides a completely independent enhanced sales dashboard with:

🔹 ZERO INHERITANCE of sale.order model - completely separate
🔹 NO MODIFICATIONS to quotation/order forms or views
🔹 Independent TransientModel 'sale.dashboard' for data only
🔹 Visual analytics with #800020 maroon primary color theme
🔹 Interactive Chart.js visualizations with brand color palette  
🔹 Mobile-responsive design optimized for brand presentation
🔹 Real-time data updates through isolated data queries

NEW ENHANCED FEATURES:
---------------------
✅ Agent Rankings (agent1_partner_id) by deal count, price_unit and amount_total
✅ Broker Rankings (broker_partner_id) by deal count, price_unit and amount_total
✅ Booking Date Integration (booking_date field support from invoice_report_for_realestate)
✅ Sale Type Filtering (sale_order_type_id from le_sale_type module)
✅ Enhanced performance tables with detailed agent/broker analytics
✅ Multi-select sale type filters for targeted analysis
✅ Comprehensive agent and broker performance metrics

Complete Independence:
---------------------
* sale.order forms remain 100% unchanged
* No view inheritance affecting quotations
* No data modifications to sales workflow
* Pure read-only dashboard functionality
* Zero impact on sales module operations

Enhanced Architecture:
---------------------
* TransientModel 'sale.dashboard' - completely separate from sale.order
* Client-side only dashboard rendering with enhanced agent analytics
* Read-only queries to existing sale.order data with commission_ax integration
* No model extensions or inheritance
* No view modifications to sales module
* Intelligent field detection (booking_date fallback to date_order)

Enhanced Features:
-----------------
* Interactive charts with custom brand colors (#800020)
* Agent and broker ranking visualizations
* Sales pipeline visualization in maroon/gold theme
* Performance KPIs with white text contrast and agent metrics
* Monthly/quarterly reports with professional styling and booking date support
* Export capabilities with brand consistency
* Multi-currency support with enhanced formatting
* Sale type filtering for targeted analysis
* Responsive design for mobile and desktop

Module Dependencies:
-------------------
* le_sale_type (for sale_order_type_id filtering)
* commission_ax (for agent1_partner_id and broker_partner_id)
* invoice_report_for_realestate (for booking_date field)

This module is SAFE to install and will NOT affect your sales quotation workflow.
All enhancements are contained within the dashboard interface only.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'web',
        'le_sale_type',
        'commission_ax',
        'invoice_report_for_realestate',
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
