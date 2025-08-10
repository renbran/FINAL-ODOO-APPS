{
    'name': 'Enhanced Payment Voucher System - OSUS',
    'version': '17.0.2.0.0',
    'category': 'Accounting',
    'summary': """Advanced Payment and Receipt Voucher System with Digital Signatures, 
                  QR Verification, Multi-stage Approval Workflows, and OSUS Branding""",
    'description': """
    Enhanced Payment Voucher System for OSUS Real Estate
    
    Key Features:
    • 4-stage Payment Voucher workflow (Submit → Review → Approve → Authorize → Post)
    • 3-stage Receipt Voucher workflow (Submit → Review → Post) 
    • Digital signature capture for all workflow stages
    • QR code generation with secure verification portal
    • OSUS branded reports with professional styling
    • Enhanced and compact report templates
    • Report generation wizards (single and bulk)
    • Email notifications and activity tracking
    • Multi-company support with role-based permissions
    • Mobile-responsive design and verification interface
    • Integration with invoices/bills workflow
    • Comprehensive audit trails and security
    """,
    'author': 'OSUS Properties - Enhanced by AI Assistant',
    'company': 'OSUS Properties',
    'maintainer': 'OSUS Properties',
    'website': "https://www.osusproperties.com",
    'depends': [
        'account', 
        'mail', 
        'web',
        'portal',
        'website',
        'contacts'
    ],
    'external_dependencies': {
        'python': ['qrcode', 'num2words', 'PIL']
    },
    'data': [
        # Security
        'security/payment_voucher_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/email_templates.xml',
        'data/voucher_sequence.xml',
        'data/qr_verification_data.xml',
        
        # Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/payment_report_wizard_views.xml',
        'views/menu_items.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/receipt_voucher_report.xml',
        'reports/qr_verification_report.xml',
        'reports/enhanced_payment_report.xml',
        'reports/report_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_payment_approval/static/src/js/digital_signature_widget.js',
            'account_payment_approval/static/src/js/payment_approval_dashboard.js',
            'account_payment_approval/static/src/js/qr_code_widget.js',
            'account_payment_approval/static/src/scss/payment_approval.scss',
            'account_payment_approval/static/src/xml/payment_approval_templates.xml',
        ],
        'web.assets_frontend': [
            'account_payment_approval/static/src/scss/payment_approval.scss',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}