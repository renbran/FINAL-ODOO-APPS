# -*- coding: utf-8 -*-
{
    'name': 'Payment Approval Workflow',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Multi-level payment approval workflow with QR verification and digital signatures',
    'description': """
        Payment Approval Workflow
        =========================
        
        This module enhances the account payment functionality with:
        
        * Multi-level approval workflows for vendor payments and customer receipts
        * QR code verification portal for public payment verification
        * Digital signatures on printed vouchers
        * Automated email notifications with professional styling
        * Role-based security groups for reviewers, approvers, and authorizers
        * Rejection workflow with reason tracking
        
        Key Features:
        - Sequential approval process: Draft -> Submitted -> Reviewed -> Approved -> Authorized -> Posted
        - Different workflows for vendor payments (5 levels) and customer receipts (4 levels)
        - Public QR verification portal for payment validation
        - Digital signature capture for each approval level
        - Professional email notifications with company branding
        - Smart buttons for journal entries and QR verification
        - Comprehensive audit trail with user and date tracking
    """,
    'author': 'Odoo Expert Developer',
    'website': 'https://www.odoo.com',
    'depends': [
        'account',
        'mail',
        'web',
        'portal',
        'website',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'uuid'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        'data/security_groups.xml',
        
        # Data
        'data/mail_templates.xml',
        
        # Views
        'views/account_payment_views.xml',
        'wizards/payment_signature_wizard_views.xml',
        'wizards/payment_rejection_wizard_views.xml',
        
        # Reports
        'reports/payment_report.xml',
        
        # Templates
        'templates/payment_verification_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    'sequence': 1,
}
