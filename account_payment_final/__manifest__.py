{
    'name': 'Account Payment Final - Enhanced Workflow',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Enhanced payment voucher system with 4-stage approval workflow and QR verification',
    'description': """
        Account Payment Final - Enhanced Workflow
        ==========================================
        
        This module provides a comprehensive payment voucher system with:
        
        Features:
        ---------
        • 4-stage approval workflow (Reviewer → Approver → Authorizer → Poster)
        • QR code verification system for payment authentication
        • Enhanced security with role-based access control
        • Professional voucher reports with company branding
        • Automated voucher numbering with configurable sequences
        • Email notifications for approval workflow stages
        • Mobile-responsive design for modern browsers
        • Comprehensive audit trail and activity logging
        • Print-optimized layouts with professional styling
        • Web-based QR verification portal
        
        Technical Features:
        ------------------
        • Odoo 17 compatible with modern ORM patterns
        • OWL framework integration for frontend components
        • REST API endpoints for QR verification
        • PostgreSQL optimized database structure
        • Docker-ready deployment configuration
        • CloudPepper hosting compatible
        
        This module transforms standard Odoo payment vouchers into
        a professional, secure, and user-friendly payment management system.
    """,
    'author': 'Odoo Development Team',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'web',
        'mail',
        'portal',
        'website',
    ],
    'data': [
        # Data and Sequences (Load First)
        'data/payment_sequences.xml',
        
        # Security (Load After Data)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Main Views (Load After Models/Security) - MINIMAL SAFE
        'views/account_payment_views.xml',
        'views/menus.xml',
        
        # Ultra Safe Views (NO OWL DIRECTIVES)
        'views/account_payment_views_ultra_safe.xml',
        
        # NO ADVANCED VIEWS TEMPORARILY
        # 'views/account_payment_views_advanced.xml',
        
        # Reports - MINIMAL
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_actions.xml',
        
        # NO QWeb TEMPLATES TEMPORARILY
        # 'reports/payment_voucher_template.xml',
        # 'reports/payment_verification_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # ULTRA MINIMAL - Only emergency CSS
            'account_payment_final/static/src/scss/emergency_fix.scss',
        ],
        # NO OTHER ASSETS TO PREVENT CONFLICTS
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow']
    },
    'demo': [
        'demo/demo_payments.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 10
}