# -*- coding: utf-8 -*-
{
    'name': 'Custom Invoice Layout',
    'version': '1.0',
    'summary': 'Customizable Invoice Layouts for Real Estate',
    'description': """
    This module adds customizable invoice layouts for real estate transactions.
    Features:
    - Customizable colors, positions, and fields
    - Integration with sales orders and deal tracking
    - QR code generation for invoices
    - Custom layouts for different property types
    """,
    'category': 'Accounting/Accounting',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'account',
        'sale',
        'web',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/doc_layout.xml',
        'views/customer_invoice.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}