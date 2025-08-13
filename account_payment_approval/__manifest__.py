# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Approval',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Advanced Payment Approval Workflow with Digital Signatures and QR Verification',
    'description': """
        Advanced Payment Approval Workflow System
        ==========================================
        
        This module provides a comprehensive payment approval workflow system with:
        
        * Multi-tier approval process (6 security groups)
        * Digital signature integration
        * QR code verification system
        * Bulk approval operations
        * Payment voucher generation
        * Comprehensive audit trail
        * Email notifications
        * Advanced reporting
        
        Features:
        ---------
        * Voucher State Management: Draft → Submitted → Under Review → Approved → Authorized → Posted
        * Role-based Security: Creator, Reviewer, Approver, Authorizer, Finance Manager, Administrator
        * Digital Signatures: Required signatures for critical approval steps
        * QR Verification: Secure QR codes for payment verification
        * Bulk Operations: Approve multiple payments at once
        * Enhanced Reporting: Payment voucher reports and summaries
        * Account Move Integration: Enhanced journal entry views with payment tracking
        * Reconciliation Navigator: Advanced reconciliation tracking and navigation
        
        Security Groups:
        ----------------
        * Payment Approval - Creator: Can create and submit payments
        * Payment Approval - Reviewer: Can review submitted payments
        * Payment Approval - Approver: Can approve reviewed payments
        * Payment Approval - Authorizer: Can authorize approved payments
        * Payment Approval - Finance Manager: Can post authorized payments
        * Payment Approval - Administrator: Full access to all operations
        
        Technical Features:
        -------------------
        * Modern Odoo 17 syntax (no deprecated attrs/states)
        * Stored computed fields for fast searching
        * Robust field compatibility checking
        * Safe XPath expressions using reliable field targets
        * Comprehensive error handling and validation
    """,
    'author': 'OSUS Properties',
    'website': 'https://www.osus.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
        'web',
        'portal',
        'payment',
        'account_payment',
    ],
    'external_dependencies': {
        'python': [
            'qrcode',
            'PIL',
            'reportlab',
            'xlsxwriter',
        ],
    },
    'data': [
        # Security
        'security/payment_approval_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        
        # Data
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        'data/system_parameters.xml',
        'data/cron_jobs.xml',
        
        # Views
        'views/menu_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_enhanced_views.xml',
        'views/wizard_views.xml',
        'views/qr_verification_templates.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_summary_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_payment_approval/static/src/scss/payment_approval.scss',
            'account_payment_approval/static/src/scss/digital_signature.scss',
            'account_payment_approval/static/src/scss/qr_verification.scss',
            'account_payment_approval/static/src/scss/dashboard.scss',
            'account_payment_approval/static/src/js/payment_approval_widget.js',
            'account_payment_approval/static/src/js/digital_signature_widget.js',
            'account_payment_approval/static/src/js/qr_verification_widget.js',
            'account_payment_approval/static/src/js/bulk_approval_widget.js',
            'account_payment_approval/static/src/js/payment_dashboard.js',
        ],
        'web.assets_frontend': [
            'account_payment_approval/static/src/scss/portal.scss',
            'account_payment_approval/static/src/js/portal.js',
        ],
        'web.qunit_suite_tests': [
            'account_payment_approval/static/tests/**/*.js',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': None,
}
