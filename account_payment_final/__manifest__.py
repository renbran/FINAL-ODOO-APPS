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
        'payment',
        'website',
    ],
    'data': [
        # Security - Load first
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        
        # Data and Configuration
        'data/sequences.xml',
        'data/email_templates.xml',
        'data/workflow_stages.xml',
        
        # Views
        'views/assets.xml',
        'views/payment_signatory_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/report_actions.xml',
        'reports/payment_voucher_template.xml',
        'reports/receipt_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'payment_voucher_enhanced/static/src/scss/variables.scss',
            'payment_voucher_enhanced/static/src/scss/payment_styles.scss',
            'payment_voucher_enhanced/static/src/js/payment_workflow.js',
            'payment_voucher_enhanced/static/src/js/qr_code_field.js',
            'payment_voucher_enhanced/static/src/js/signature_capture.js',
        ],
        'web.assets_frontend': [
            'payment_voucher_enhanced/static/src/scss/frontend_styles.scss',
        ],
        'web.report_assets_common': [
            'payment_voucher_enhanced/static/src/scss/report_styles.scss',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow', 'num2words']
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}