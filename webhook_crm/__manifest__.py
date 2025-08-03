# -*- coding: utf-8 -*-
{
    'name': 'Webhook CRM Lead Handler',
    'version': '1.0.0',
    'category': 'CRM',
    'summary': 'Handle external webhooks for CRM lead creation',
    'description': """
        This module provides a comprehensive webhook handler for creating CRM leads
        from external sources with advanced field mapping capabilities.
    """,
    'author': 'Your Company',
    'depends': ['base', 'crm', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/webhook_mapping_views.xml',
        'data/webhook_mapping_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
