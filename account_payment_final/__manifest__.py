{
    'name': 'Enhanced Payment Voucher System',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Advanced Payment Voucher with Multi-level Approval and Digital Signatures',
    'description': """
        Enhanced Payment Voucher System for OSUS Real Estate with:
        - 4-stage approval workflow for payments (Create → Review → Approve → Authorize → Post)
        - 3-stage approval workflow for receipts (Create → Review → Post)
        - Digital signature capture and management
        - QR code verification system with secure URLs
        - OSUS branded professional report templates
        - Email notifications and Odoo activity tracking
        - Role-based access control with granular permissions
        - Integration with invoices and bills workflow
        - Real-time workflow tracking and audit trails
        - Amount in words conversion
        - Multi-signatory support (4 for payments, 2 for receipts)
    """,
    'author': 'OSUS Real Estate Development Team',
    'website': 'https://www.osus.ae',
    'depends': [
        'base',
        'account',
        'mail',
        'web',
        'portal',
    ],
    'data': [
        # Security - Load first
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data and Configuration
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        'data/system_parameters.xml',
        
        # Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/payment_voucher_actions.xml',
        'reports/payment_voucher_template.xml',
        'reports/payment_verification_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_payment_final/static/src/scss/variables.scss',
            'account_payment_final/static/src/scss/professional_payment_ui.scss',
            'account_payment_final/static/src/scss/components/payment_widget_enhanced.scss',
            'account_payment_final/static/src/js/payment_workflow.js',
            'account_payment_final/static/src/js/components/payment_approval_widget_enhanced.js',
            'account_payment_final/static/src/js/fields/qr_code_field.js',
            'account_payment_final/static/src/js/error_handler.js',
            'account_payment_final/static/src/js/performance_optimizer.js',
        ],
        'web.assets_frontend': [
            'account_payment_final/static/src/scss/frontend/verification_portal.scss',
            'account_payment_final/static/src/js/frontend/qr_verification.js',
        ],
        'web.report_assets_common': [
            'account_payment_final/static/src/scss/payment_voucher_report.scss',
            'account_payment_final/static/src/scss/responsive_report_styles.scss',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow', 'num2words']
    },
    'demo': [
        'demo/demo_payments.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}