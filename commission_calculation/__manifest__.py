{
    'name': 'Commission Calculation',
    'version': '17.0.1.0.0',
    'summary': 'Refactored commission calculation with custom fields only, no computation',
    'description': 'This module replaces the old commission field with custom fields and removes all computation logic.',
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'category': 'Sales',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/commission_calculation_views.xml',
        'views/commission_calculation_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
