# -*- coding: utf-8 -*-
{
    'name': 'SGC Tech AI Theme',
    'version': '17.0.1.0.3',
    'category': 'Theme/Backend',
    'summary': 'Modern AI-powered backend theme for Odoo 17 - Scholarix Global Consultants',
    'description': '''
        SGC Tech AI Theme
        =================
        * Modern deep ocean color palette
        * AI-focused design with electric accents
        * CloudPepper deployment ready
        * Odoo 17 compliant SCSS (no CSS variables)
        * Proper asset loading with correct paths
        * Full ownership and permissions configured
    ''',
    'author': 'Scholarix Global Consultants',
    'website': 'https://scholarixglobal.com',
    'license': 'LGPL-3',
    'depends': ['web', 'base'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            # Core color variables - MUST load first
            'sgc_tech_ai_theme/static/src/scss/sgc_colors.scss',
            # Typography
            'sgc_tech_ai_theme/static/src/scss/typography.scss',
            # Layout & visibility
            'sgc_tech_ai_theme/static/src/scss/content_visibility.scss',
            # Component themes
            'sgc_tech_ai_theme/static/src/scss/header_theme.scss',
            'sgc_tech_ai_theme/static/src/scss/theme_overrides.scss',
            # Dashboard styling
            'sgc_tech_ai_theme/static/src/scss/dashboard_theme.scss',
            # CRM specific
            'sgc_tech_ai_theme/static/src/scss/crm_theme.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
