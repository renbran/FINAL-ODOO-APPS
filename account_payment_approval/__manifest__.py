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
        'views/account_move_enhanced_views.xml',
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
            # Simplified SCSS - Single file with no complex imports
            'account_payment_approval/static/src/scss/payment_approval.scss',
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
