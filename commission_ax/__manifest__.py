{
    'name': 'Custom Commission Management',
    'version': '1.1',
    'summary': 'Advanced Commission Calculation and Purchase Order Management',
    'description': '''
    Automatically calculates commissions and creates purchase orders for employees after a deal is closed.
    Features:
    - Automatic commission calculation
    - Purchase order generation for consultants, managers, and directors
    - Automated posting of purchase orders based on receipt and payment status
    - Manual commission processing options
    ''',
    'category': 'Sales',
    'author': 'RENBRAN',
    'depends': [
        'base',
        'sale', 
        'purchase', 
        'account'
    ],
    'data': [
        'views/sale_order.xml',
        'views/external_commission_views.xml',
        'views/internal_commission_views.xml',
        'views/purchase_order.xml',
        'data/purchase_order_cron.xml',  # Add the cron job XML
        'security/ir.model.access.csv',  # Recommended to add access rights
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}