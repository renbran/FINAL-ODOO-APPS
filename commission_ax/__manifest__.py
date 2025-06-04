{
    'name': 'Commission Management',
    'version': '17.0.1.0.0',
    'summary': 'Manage internal and external commissions',
    'description': """
        Comprehensive commission management for sales teams
        and external partners.
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'sale',
        'purchase',
        'hr',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/external_commission_views.xml',
        'views/internal_commission_views.xml',
        'data/commission_sequence.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}