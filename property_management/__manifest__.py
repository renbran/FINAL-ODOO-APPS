{
    'name': 'Property Sale Management',
    'version': '17.1',
    'summary': 'Manage property sales and property details',
    'description': '''
        This module allows you to manage property details and their sales.
        - Maintain property records with details like price, address, and status.
        - Link properties to sales and auto-fill relevant details.
        - Generate broker commission invoices based on property sales.
    ''',
    'author': 'Renbran',
    'website': 'https://yourcompany.com',
    'category': 'Real Estate',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/property_sale_views.xml',
        'views/property_property_views.xml',
        'views/property_sale_offer_views.xml',
        'views/account_move_views.xml',
        'views/broker_commission_views.xml',  # Add the new broker commission views
        'reports/property_sale_management.xml',
        'reports/report_property_sale.xml',
        'reports/report_property_sale_offer.xml',
        'reports/property_sale_report_template.xml',
        'reports/action_report.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'property_management/static/src/js/property_management.js',
        'property_management/static/src/scss/property_management.scss',
    ],
},
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}