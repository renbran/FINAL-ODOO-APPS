# -*- coding: utf-8 -*-
{
    'name': 'SCHOLARIX Assessment System',
    'version': '17.0.2.0.1',
    'category': 'Human Resources/Recruitment',
    'summary': 'AI-Powered Candidate Assessment and Evaluation System',
    'description': """
        SCHOLARIX Assessment System
        ============================
        
        Comprehensive candidate assessment platform with:
        - Public assessment portal for candidates
        - AI-powered NLP scoring engine
        - Human review and ranking system
        - Advanced analytics dashboard
        - Multi-tier security and audit trails
        - Email notifications and PDF reports
        - Mobile-responsive interface
        
        Features:
        ---------
        * Candidate submission portal
        * 10-question assessment framework
        * AI scoring across 5 categories (Technical, Sales, Communication, Learning, Cultural Fit)
        * Human review workflow
        * Candidate rankings and leaderboard
        * Advanced search and filtering
        * Analytics and reporting
        * Export to CSV/Excel
        * GDPR compliant
    """,
    'author': 'SCHOLARIX',
    'website': 'https://scholarix.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'portal',
        'mail',
        'hr_recruitment',
    ],
    'data': [
        # Security
        'security/assessment_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/assessment_questions_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',

        # Reports (must be loaded before views that reference them)
        'reports/assessment_report.xml',
        'reports/assessment_templates.xml',

        # Views
        'views/assessment_candidate_views.xml',
        'views/assessment_response_views.xml',
        'views/assessment_ai_score_views.xml',
        'views/assessment_human_review_views.xml',
        'views/assessment_ranking_views.xml',
        'views/assessment_question_views.xml',
        'views/assessment_audit_log_views.xml',
        'views/dashboard_views.xml',
        'views/assessment_menu.xml',  # Must be last - references actions from other views

        # Portal
        'views/portal_templates.xml',
        'views/portal_assessment_templates.xml',
        'views/portal_assessment_landing.xml',

        # Wizards
        'wizards/assessment_export_wizard_views.xml',
        'wizards/assessment_bulk_action_wizard_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'scholarix_assessment/static/src/css/portal_assessment.css',
            'scholarix_assessment/static/src/css/assessment_landing.css',
            'scholarix_assessment/static/src/js/portal_assessment.js',
        ],
        'web.assets_backend': [
            'scholarix_assessment/static/src/css/dashboard.css',
            'scholarix_assessment/static/src/js/dashboard.js',
            'scholarix_assessment/static/src/xml/dashboard_templates.xml',
        ],
    },
    'external_dependencies': {
        'python': ['openai', 'anthropic', 'tiktoken', 'numpy', 'pandas'],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
