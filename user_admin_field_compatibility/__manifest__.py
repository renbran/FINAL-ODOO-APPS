# -*- coding: utf-8 -*-
{
    'name': 'User Admin Field Compatibility',
    'version': '17.0.1.0.0',
    'category': 'Hidden/Tools',
    'summary': 'Adds missing is_admin field to res.users for compatibility',
    'description': """
        User Admin Field Compatibility
        ===============================
        
        This module adds the is_admin computed field to res.users model
        to fix compatibility issues with modules that reference this field.
        
        **Purpose**: Fix "res.users.is_admin field is undefined" errors
        
        **What it does**:
        - Adds is_admin computed field that checks if user is in base.group_system
        - Prevents crashes when views or modules reference this field
        - Fully backward compatible with all existing functionality
    """,
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
