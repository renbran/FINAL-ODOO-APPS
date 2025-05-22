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
    'author': 'Renbran',
    'website': 'https://yourcompany.com',
    'category': 'Real Estate/Sales',
    'depends': [
        'base',
        'web',
        'mail',
        'account',
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/menu_items.xml',
        'views/property_property_views.xml',
        'views/property_sale_views.xml',
        'views/internal_commission_views.xml',
        'views/broker_commission_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'reports/property_sale_offer_report.xml',  # Add this line
        'reports/property_sale_report.xml',
        # Removed reference to non-existent rental_views.xml
    ],
    'assets': {
        'web.assets_backend': [
            # Libs (load first)
            'property_sale_management/static/src/scss/property_sale_management.scss',
            
            # Core Components
            'property_sale_management/static/src/js/payment_progress.js',
            
            # Controllers
            'property_sale_management/static/src/js/property_form_controller.js',
            'property_sale_management/static/src/js/property_kanban_controller.js',
            'property_sale_management/static/src/js/property_list_controller.js',
            
            # Templates
            'property_sale_management/static/src/xml/payment_progress.xml',
            
            # Entry point
            'property_sale_management/static/src/js/index.js',  # Fixed missing comma here
            'property_sale_management/static/src/js/monetary_field_patch.js',
        ],
        'web.assets_qweb': [
            'property_sale_management/static/src/xml/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    'post_init_hook': '_post_install_initialize',
}