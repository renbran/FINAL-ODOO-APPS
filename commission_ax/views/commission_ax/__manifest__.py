{
    'name': 'CUSTOME Commission Management',
    'version': '17.0.1.0.0',
    'summary': 'Commission Management for Sale Orders',
    'description': """
        Manage commissions for different parties involved in sales.
        Calculate commissions based on sales value or untaxed amounts.
        Generate purchase orders for commission payments.
    """,
    'category': 'Sales',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'purchase', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}