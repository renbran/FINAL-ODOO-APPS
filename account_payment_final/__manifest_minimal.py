{
    'name': 'Account Payment Final - Minimal Safe',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Enhanced payment voucher system - Safe Installation Version',
    'description': """
        Account Payment Final - Minimal Safe Installation
        ================================================
        
        This is a minimal version for safe installation testing.
        Contains only core functionality without advanced features.
    """,
    'author': 'Odoo Development Team',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
    ],
    'data': [
        # Security (Essential)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Basic Views (Safe)
        'views/account_payment_views.xml',
        'views/menus.xml',
        
        # Minimal Advanced Views (Safe)
        'views/account_payment_views_advanced.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Minimal CSS for basic functionality
            'account_payment_final/static/src/scss/emergency_fix.scss',
            'account_payment_final/static/src/scss/osus_branding.scss',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow']
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 10
}
