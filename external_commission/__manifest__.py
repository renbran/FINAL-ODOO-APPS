{
    'name': 'External Commission',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage external commissions for brokers, referrers, cashback recipients, and others',
    'description': 'Module to manage external party commissions such as brokers, referrers, cashback recipients, and other external agents.',
    'author': 'Your Company',
    'depends': ['sale', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
