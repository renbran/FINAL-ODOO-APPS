{
    'name': 'Custom Fields Cleanup',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Fix orphaned references causing _unknown object errors',
    'description': '''
        This module provides a server action to clean up orphaned references 
        in custom fields that cause '_unknown' object errors.
        
        Install this module and run the "Clean Custom Fields" server action 
        from Settings > Technical > Server Actions.
    ''',
    'depends': ['base'],
    'data': [
        'data/server_actions.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
