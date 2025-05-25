{
    'name': 'Real Estate Management V2',
    'version': '17.0.1.0.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties, offers, and sales',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'account'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/ir_sequence_data.xml',
        
        # Views
        'views/menu_views.xml',
        'views/property_views.xml',
        'views/property_offer_views.xml',
        'views/property_sale_views.xml',
        'views/property_sale_line_views.xml',
        'views/broker_commission_views.xml',
        'views/internal_commission_views.xml',
        'views/res_config_views.xml',
        'views/property_action_views.xml',
        
        # Wizards
        'wizards/property_report_wizard_views.xml',
    ],
    'demo': [
        'demo/property_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'real_estate_management_v2/static/src/scss/property.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}