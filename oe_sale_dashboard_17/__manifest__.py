{
    'name': 'Executive Sales Dashboard',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Advanced Sales Dashboard with Real-time Analytics',
    'description': """
        Executive Sales Dashboard for Odoo 17
        =====================================
        
        Features:
        - Real-time sales performance metrics
        - Interactive charts and visualizations
        - Top performers tracking (agents & agencies)
        - Sales type analysis and filtering
        - Commission tracking integration
        - Mobile-responsive design
        
        Compatible with:
        - le_sale_type module (for sales type categorization)
        - commission_ax module (for agent/broker commission tracking)
        - osus_invoice_report module (for enhanced reporting fields)
    """,
    'author': 'OdooElevate',
    'website': 'https://www.odooelevate.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'account',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oe_sale_dashboard_17/static/src/js/dashboard.js',
            'oe_sale_dashboard_17/static/src/css/dashboard.scss',
            'oe_sale_dashboard_17/static/src/xml/dashboard_template.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
