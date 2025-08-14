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
        # Security (Load First)
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data and Sequences
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        'data/system_parameters.xml',
        
        # Main Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_actions.xml',
        'reports/payment_voucher_template.xml',
        
        # Website/Portal Views
        'views/payment_verification_templates.xml',
        'views/payment_voucher_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Variables must be loaded first for all other SCSS files
            'account_payment_final/static/src/scss/variables.scss',
            
            # Core SCSS files (in dependency order)
            'account_payment_final/static/src/scss/emergency_fix.scss',
            'account_payment_final/static/src/scss/enhanced_form_styling.scss',
            'account_payment_final/static/src/scss/cloudpepper_optimizations.scss',
            'account_payment_final/static/src/scss/professional_payment_ui.scss',
            'account_payment_final/static/src/scss/osus_branding.scss',
            
            # Component-specific styles
            'account_payment_final/static/src/scss/components/payment_widget.scss',
            'account_payment_final/static/src/scss/components/payment_widget_enhanced.scss',
            'account_payment_final/static/src/scss/components/table_enhancements.scss',
            'account_payment_final/static/src/scss/views/form_view.scss',
            
            # JavaScript files
            'account_payment_final/static/src/js/error_handler.js',
            'account_payment_final/static/src/js/cloudpepper_console_optimizer.js',
            'account_payment_final/static/src/js/unknown_action_handler.js',
            'account_payment_final/static/src/js/payment_workflow.js',
            'account_payment_final/static/src/js/components/payment_approval_widget_enhanced.js',
            'account_payment_final/static/src/js/components/payment_widget.js',
            'account_payment_final/static/src/js/fields/qr_code_field.js',
            'account_payment_final/static/src/js/views/payment_list_view.js',
            
            # XML templates
            'account_payment_final/static/src/xml/payment_templates.xml',
        ],
        'web.assets_common': [
            # Variables for reports (loaded first)
            'account_payment_final/static/src/scss/variables.scss',
            
            # Report-specific styles
            'account_payment_final/static/src/scss/responsive_report_styles.scss',
            'account_payment_final/static/src/scss/payment_voucher_report.scss',
        ],
        'web.assets_frontend': [
            # Variables for frontend (loaded first)
            'account_payment_final/static/src/scss/variables.scss',
            
            # Frontend verification portal
            'account_payment_final/static/src/scss/frontend/verification_portal.scss',
            'account_payment_final/static/src/js/frontend/qr_verification.js',
        ],
        'web.qunit_suite_tests': [
            # Test files
            'account_payment_final/static/tests/**/*.js',
        ],
    },
    'external_dependencies': {
        'python': ['qrcode', 'pillow'],
    },
    'demo': [
        'demo/demo_payments.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 10,
}