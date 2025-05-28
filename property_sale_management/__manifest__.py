{
    'name': 'Property Sale Management',
    'version': '17.0.1.0.0',
    'summary': 'Comprehensive Property Sales Management System',
    'description': '''
        Advanced property management solution with features including:
        - Full lifecycle management of property listings
        - Integrated sales and commission tracking
        - Automated financial reporting
        - Interactive dashboards and reporting
        - Multi-currency support
        - Team-based commission structures
    ''',
    'category': 'Real Estate/Sales',
    'author': 'Renbran',
    'website': 'https://www.renbran.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'account',
        'contacts',
        'purchase',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/property_property_views.xml',
        'views/property_sale_offer_views.xml',
        'views/property_sale_views.xml',
        'views/internal_commission_views.xml',
        'views/broker_commission_views.xml',
        'views/internal_commission_purchase_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/property_offer_views.xml',  # Add this line
        'reports/property_sale_report.xml',
        'reports/property_offer_report.xml',
        'reports/property_report.xml',
        'reports/property_sale_management.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'property_sale_management/static/src/scss/property_sale_management.scss',
            'property_sale_management/static/src/js/payment_progress.js',
        ],
        'web.assets_qweb': [
            'property_sale_management/static/src/xml/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'post_init_hook': '_post_install_initialize',
}