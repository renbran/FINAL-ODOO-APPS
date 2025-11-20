# -*- coding: utf-8 -*-
{
    'name': 'Order Status Override',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Override and manage custom order statuses for sale orders',
    'description': 'Allows overriding and customizing order status workflow for sale orders.',
    'author': 'CloudPepper/OSUS',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_status_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
