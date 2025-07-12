{
    'name': 'Property Monitor',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Property Inventory and Status Monitoring System',
    'description': """
        Property Monitoring System for tracking property status, inventory and 
        specifications with easy-to-use dashboard for summary visualization.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'depends': ['base'],
    'data': [
        'security/property_security.xml',
        'views/property_menus.xml',
        'views/property_views.xml',
        'views/property_dashboard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'property_monitor/static/src/scss/property_dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
}