{
    'name': 'White Label Branding',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Remove Odoo branding and replace with company branding',
    'description': """
        This module removes all Odoo marketing content and branding,
        replacing it with your company's branding dynamically.
        
        Features:
        - Replace "Powered by Odoo" with company name
        - Override digest notifications
        - Remove Odoo marketing content
        - Dynamic company name replacement
        - Clean interface without Odoo references
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'base',
        'web',
        'mail',
        'digest',
        'portal',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/digest_data.xml',
        'data/mail_template_data.xml',
        'views/res_config_settings_views.xml',
        'views/web_client_templates.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'white_label_branding/static/src/js/web_client.js',
            'white_label_branding/static/src/css/branding.css',
            'white_label_branding/static/src/css/common.css',
        ],
        'web.assets_frontend': [
            'white_label_branding/static/src/js/frontend.js',
            'white_label_branding/static/src/css/frontend.css',
            'white_label_branding/static/src/css/common.css',
        ],
        'web.assets_common': [
            'white_label_branding/static/src/css/common.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
