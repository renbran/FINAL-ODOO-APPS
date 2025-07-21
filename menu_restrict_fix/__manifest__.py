# -*- coding: utf-8 -*-
{
    'name': 'Menu Restrict Field Fix',
    'version': '17.0.1.0.0',
    'category': 'Base',
    'summary': 'Fix for restrict_user_ids field error in ir.ui.menu',
    'description': """
This module temporarily fixes the restrict_user_ids field error by:
1. Disabling the problematic security rule
2. Ensuring the field is properly created
    """,
    'author': 'System Fix',
    'depends': ['base'],
    'data': [
        'data/fix_security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
