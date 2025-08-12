# -*- coding: utf-8 -*-
{
    'name': 'Enterprise Payment Approval System - OSUS',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Enterprise-level Multi-tier Payment Approval System with Digital Signatures and QR Verification',
    'description': """
Enterprise Payment Approval System for OSUS Properties

Key Features:
============
• Multi-level approval workflow with configurable tiers
• Digital signature capture for all approval stages
• QR code generation with secure verification portal
• Role-based permission system (6-tier hierarchy)
• Real-time dashboard and analytics
• Email notifications and activity tracking
• Bulk approval and batch processing
• Mobile-responsive verification interface
• Comprehensive audit trails and reporting
• Integration with accounting workflows
• OSUS branded professional reports

Workflow Stages:
===============
1. Draft → Submit for Review
2. Under Review → Approve/Reject
3. Approved → Authorize (for payments above threshold)
4. Authorized → Post to Accounting
5. Posted → Complete

Security Groups:
===============
• Payment Creator: Create and submit payments
• Payment Reviewer: Review submitted payments
• Payment Approver: Approve reviewed payments
• Payment Authorizer: Final authorization for high-value payments
• Payment Manager: Full access to all payment operations
• Payment Admin: System configuration and security settings

Technical Features:
==================
• Modern Odoo 17 OWL framework
• Responsive CSS with OSUS branding
• REST API integration ready
• Automated email templates
• QR verification with mobile support
• Digital signature widgets
• Advanced reporting with Chart.js
• Bulk operations support
    """,
    'author': 'OSUS Properties',
    'company': 'OSUS Properties',
    'maintainer': 'OSUS Properties Development Team',
    'website': 'https://www.osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'mail',
        'web',
        'portal',
        'website',
        'contacts',
        'hr',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'num2words', 'Pillow', 'reportlab']
    },
    'data': [
        # Security
        'security/payment_approval_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        
        # Data and Sequences
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        'data/system_parameters.xml',
        'data/cron_jobs.xml',
        
        # Views
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/payment_approval_config_views.xml',
        'views/payment_approval_dashboard_views.xml',
        'views/menu_views.xml',
        'views/wizard_views.xml',
        
        # Wizards
        'wizards/payment_bulk_approval_wizard_views.xml',
        'wizards/payment_report_wizard_views.xml',
        
        # Reports
        'reports/payment_voucher_report.xml',
        'reports/payment_approval_report.xml',
        'reports/qr_verification_report.xml',
        'reports/report_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Main CSS (compiled from modular SCSS)
            'account_payment_approval/static/src/css/payment_approval.css',
            
            # SCSS Variables and Components (for development/customization)
            'account_payment_approval/static/src/scss/_variables.scss',
            'account_payment_approval/static/src/scss/main.scss',
            
            # JavaScript Components (organized structure)
            'account_payment_approval/static/src/js/components/payment_approval_dashboard.js',
            'account_payment_approval/static/src/js/widgets/digital_signature_widget.js',
            'account_payment_approval/static/src/js/widgets/qr_code_widget.js',
            'account_payment_approval/static/src/js/widgets/bulk_approval_widget.js',
            'account_payment_approval/static/src/js/views/payment_form_view.js',
            'account_payment_approval/static/src/js/fields/approval_state_field.js',
            
            # XML Templates
            'account_payment_approval/static/src/xml/payment_approval_templates.xml',
            'account_payment_approval/static/src/xml/dashboard_templates.xml',
            'account_payment_approval/static/src/xml/digital_signature_templates.xml',
            'account_payment_approval/static/src/xml/qr_verification_templates.xml',
        ],
        'web.assets_frontend': [
            # Frontend styles for QR verification portal
            'account_payment_approval/static/src/css/payment_approval.css',
            'account_payment_approval/static/src/js/qr_verification.js',
        ],
        'web.qunit_suite_tests': [
            'account_payment_approval/static/tests/**/*.js',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 15,
    'price': 299.00,
    'currency': 'USD',
    'support': 'support@osusproperties.com',
}
