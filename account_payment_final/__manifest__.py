# -*- coding: utf-8 -*-
{
    'name': 'OSUS Enhanced Payment Voucher System',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Advanced Payment Voucher with Multi-level Approval and Digital Signatures',
    'description': """
OSUS Enhanced Payment Voucher System
====================================

Professional payment voucher system with comprehensive workflow management:

Core Features:
--------------
* Multi-level approval workflow (3-step receipts, 5-step payments)
* Digital signature capture and QR code verification
* OSUS branded professional reports
* Real-time workflow tracking and notifications
* Role-based access control with 6 security groups

Workflow Stages:
---------------
* Receipts: Submit → Review → Post
* Payments: Submit → Review → Approve → Authorize → Post

Advanced Features:
-----------------
* QR code verification system with public access
* Email notifications at each workflow stage
* Amount in words conversion
* Multi-signatory support with digital signatures
* Integration with invoices and bills
* Audit trails and verification logging
* Mobile-responsive design

Technical:
----------
* Compatible with Odoo 17.0
* SCSS-based styling system
* JavaScript enhancements
* API endpoints for verification
* Automated maintenance tasks

Security:
---------
* Payment Voucher User: Create and submit
* Payment Voucher Reviewer: Review and forward
* Payment Voucher Approver: Approve payments
* Payment Voucher Authorizer: Final authorization
* Payment Voucher Poster: Post to ledger
* Payment Voucher Manager: Full access
    """,
    'author': 'OSUS Real Estate Development Team',
    'website': 'https://www.osus.ae',
    'depends': [
        'base',
        'account',
        'account_payment',
        'mail',
        'web',
        'website',
        'portal',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'pillow', 'num2words']
    },
    'data': [
        # Security
        'security/payment_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/payment_sequences.xml',
        'data/email_templates.xml',
        'data/cron_jobs.xml',
        
        # Views
        'views/payment_signatory_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/payment_verification_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        
        # Reports
        'reports/payment_voucher_actions.xml',
        'reports/payment_voucher_template.xml',
        'reports/payment_verification_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_payment_final/static/src/scss/payment_voucher.scss',
            'account_payment_final/static/src/css/payment_voucher.css',
            'account_payment_final/static/src/js/payment_voucher.js',
            'account_payment_final/static/src/xml/payment_voucher_templates.xml',
        ],
        'web.assets_frontend': [
            'account_payment_final/static/src/css/verification_portal.css',
            'account_payment_final/static/src/js/qr_verification.js',
        ],
        'web.report_assets_common': [
            'account_payment_final/static/src/css/report_payment_voucher.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}