{
    'name': 'Account Vacuum Fix',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Fix autovacuum errors for account tax reports',
    'description': """
        Account Vacuum Fix
        ==================
        
        This module fixes the autovacuum error that occurs with account.tax.report model:
        "You can't delete a report that has variants."
        
        Features:
        - Cleans up orphaned report variants
        - Fixes problematic tax report relationships
        - Provides manual fix actions
        - Temporarily disables/re-enables autovacuum during fixes
        
        This is a maintenance module that should be installed temporarily to fix
        the vacuum issue and can be uninstalled after the fix is applied.
    """,
    'author': 'OSUS Development Team',
    'website': 'https://www.osus.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_vacuum_fix_views.xml',
        'data/fix_actions.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
