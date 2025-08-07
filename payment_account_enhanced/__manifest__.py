{
    'name': 'OSUS Payment Voucher Enhanced',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Enhanced Payment Vouchers with OSUS Brand Identity and Approval Workflow',
    'description': '''
        Enhanced Payment Voucher System for OSUS Properties
        ==================================================
        
        Features:
        ✓ OSUS branded payment voucher reports with premium design
        ✓ Professional approval workflow with state management
        ✓ QR code verification system for payment authentication
        ✓ Automatic voucher numbering with customizable sequences
        ✓ Enhanced security validations and user permissions
        ✓ Mobile-responsive design for modern browsers
        ✓ Print-optimized layouts with company branding
        ✓ Comprehensive audit trail and logging
        
        Design Standards:
        ✓ Follows Odoo 17 development best practices
        ✓ Modern UI/UX with responsive design
        ✓ Professional color scheme (Burgundy & Gold)
        ✓ Accessibility compliant interfaces
        ✓ Production-ready code structure
        
        This module transforms standard Odoo payment vouchers into 
        premium, branded documents that reflect OSUS Properties' 
        luxury real estate excellence while maintaining full 
        compatibility with Odoo 17 standards.
    ''',
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'web',
        'mail',
    ],
    'data': [
        # Security
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequences.xml',
        'data/email_templates.xml',
        
        # Views
        'views/account_payment_views.xml',
        'views/res_company_views.xml',
        
        # Reports
        'reports/payment_voucher_actions.xml',
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_template.xml',
        
        # Website (for QR verification)
        'views/payment_verification_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'payment_account_enhanced/static/src/css/payment_voucher.css',
            'payment_account_enhanced/static/src/js/payment_voucher.js',
        ],
        'web.assets_frontend': [
            'payment_account_enhanced/static/src/css/payment_verification.css',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow'],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 10,
    'post_init_hook': '_post_init_hook',
}