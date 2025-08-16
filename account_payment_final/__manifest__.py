# -*- coding: utf-8 -*-
{
    'name': 'OSUS Payment Approval System',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'OSUS Properties - Professional Payment Voucher System with Multi-Stage Approval Workflow',
    'description': """
        OSUS Properties Payment Approval System
        ======================================
        
        Professional payment voucher management system designed specifically for 
        OSUS Properties with comprehensive approval workflows and security features.
        
        Key Features:
        -------------
        * 4-Stage Approval Workflow: Reviewer -> Approver -> Authorizer -> Final Approval
        * QR Code Verification: Secure payment authentication system
        * OSUS Branding: Professional styling with OSUS Properties brand colors
        * Role-Based Security: Granular access control for different user roles
        * Digital Signatures: Electronic signature capture for each approval stage
        * Professional Reports: OSUS-branded voucher reports with QR verification
        * Automated Sequences: Smart voucher numbering system
        * Email Notifications: Workflow status updates for stakeholders
        * Mobile Responsive: Optimized for desktop, tablet, and mobile devices
        * Audit Trail: Complete payment history and approval tracking
        
        Technical Excellence:
        -------------------
        * Odoo 17 Native: Built with latest ORM patterns and OWL framework
        * CloudPepper Ready: Optimized for CloudPepper hosting environment
        * Security First: Implements Odoo security best practices
        * Performance Optimized: Efficient database queries and caching
        * API Integration: REST endpoints for external system integration
        * Test Coverage: Comprehensive automated testing suite
        
        Perfect for organizations requiring professional payment processing
        with strong approval controls and comprehensive audit capabilities.
    """,
    'author': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
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
        
        # IMMEDIATE Error Prevention Template (HTML Head Injection)
        'views/immediate_error_prevention_template.xml',
        
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
        'views/payment_voucher_template_enhanced.xml',
    ],
    'assets': {
        # Core Backend Assets - Optimized Loading Order
        'web.assets_backend': [
            # LEGACY-COMPATIBLE Fix (Must Load ABSOLUTELY FIRST - ES5 Only)
            ('prepend', 'account_payment_final/static/src/js/legacy_compatible_fix.js'),
            # ULTIMATE Module Fix (Must Load FIRST - Before Everything Else)
            ('prepend', 'account_payment_final/static/src/js/ultimate_module_fix.js'),
            # IMMEDIATE Error Prevention (Must Load First - Before Everything)
            ('prepend', 'account_payment_final/static/src/js/immediate_error_prevention.js'),
            # Critical Error Prevention (Secondary)
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_clean_fix.js'),
            
            # Core OSUS Branding (Priority)
            'account_payment_final/static/src/scss/osus_branding.scss',
            'account_payment_final/static/src/scss/professional_payment_ui.scss',
            
            # Component Styles (Modular Loading)
            'account_payment_final/static/src/scss/components/**/*.scss',
            'account_payment_final/static/src/scss/views/**/*.scss',
            'account_payment_final/static/src/scss/enhanced_form_styling.scss',
            'account_payment_final/static/src/scss/payment_voucher.scss',
            
            # Core JavaScript Components (ES6 Modules)
            'account_payment_final/static/src/js/components/**/*.js',
            'account_payment_final/static/src/js/fields/**/*.js',
            'account_payment_final/static/src/js/views/**/*.js',
            'account_payment_final/static/src/js/payment_voucher.js',
            
            # Non-Module Helpers (CloudPepper Compatible)
            'account_payment_final/static/src/js/payment_workflow_safe.js',
        ],
        
        # Frontend Assets (Public Portal)
        'web.assets_frontend': [
            # LEGACY-COMPATIBLE Fix for Public Pages
            ('prepend', 'account_payment_final/static/src/js/legacy_compatible_fix.js'),
            # ULTIMATE Module Fix for Public Pages
            ('prepend', 'account_payment_final/static/src/js/ultimate_module_fix.js'),
            # IMMEDIATE Error Prevention for Public Pages
            ('prepend', 'account_payment_final/static/src/js/immediate_error_prevention.js'),
            # Error Prevention for Public Pages
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_clean_fix.js'),
            
            # Frontend Styles
            'account_payment_final/static/src/scss/frontend/**/*.scss',
            'account_payment_final/static/src/scss/osus_branding.scss',
            
            # Frontend JavaScript (Vanilla JS for Compatibility)
            'account_payment_final/static/src/js/frontend/**/*.js',
        ],
        
        # QWeb Templates
        'web.assets_qweb': [
            'account_payment_final/static/src/xml/**/*.xml',
        ],
        
        # Dark Theme Support
        'web.assets_web_dark': [
            ('prepend', 'account_payment_final/static/src/js/ultimate_module_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/immediate_error_prevention.js'),
            ('prepend', 'account_payment_final/static/src/js/cloudpepper_clean_fix.js'),
            'account_payment_final/static/src/xml/**/*.xml',
        ],
        
        # Core Web Assets (Load Before Standard Web Assets)
        'web.assets_common': [
            ('prepend', 'account_payment_final/static/src/js/legacy_compatible_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/ultimate_module_fix.js'),
            ('prepend', 'account_payment_final/static/src/js/immediate_error_prevention.js'),
            'account_payment_final/static/src/scss/responsive_report_styles.scss',
        ],
        
        # Test Suite
        'web.qunit_suite_tests': [
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