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
        'views/property_property_views.xml',
        'views/property_sale_views.xml',
        'views/property_sale_offer_views.xml',
        'views/broker_commission_views.xml',
        'reports/property_sale_management.xml',
        'reports/report_property_sale.xml',
        'reports/report_property_sale_offer.xml',
        'reports/action_report.xml',
        'views/action_menu.xml',
        'views/menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'property_management/static/src/js/property_status_widget.js',
            'property_management/static/src/scss/property_management.scss',
            'property_management/static/src/xml/property_status_widget.xml',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}