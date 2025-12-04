# -*- coding: utf-8 -*-
{
    'name': 'SGC Tech AI Theme',
    'version': '17.0.1.0.4',
    'category': 'Theme/Backend',
    'summary': 'Modern AI-powered backend theme for Odoo 17 - Scholarix Global Consultants',
    'description': '''
        SGC Tech AI Theme
        =================
        * Modern deep ocean color palette with electric cyan accents
        * AI-focused design with gradient effects
        * Enterprise-style sidebar menu with toggle button
        * Persistent sidebar state (remembers visibility)
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
            
            # Initialization script
            'sgc_tech_ai_theme/static/src/webclient/sgc_init.js',
            
            # Enterprise-style navbar (toggle button and styling)
            'sgc_tech_ai_theme/static/src/webclient/navbar/sgc_navbar.js',
            'sgc_tech_ai_theme/static/src/webclient/navbar/sgc_navbar.xml',
            'sgc_tech_ai_theme/static/src/webclient/navbar/sgc_navbar.scss',
            
            # Appsbar integration (Enterprise-inspired sidebar)
            'sgc_tech_ai_theme/static/src/webclient/menus/app_menu_service.js',
            'sgc_tech_ai_theme/static/src/webclient/appsbar/sgc_appsbar.js',
            'sgc_tech_ai_theme/static/src/webclient/sgc_webclient.js',
            'sgc_tech_ai_theme/static/src/webclient/appsbar/sgc_appsbar.xml',
            'sgc_tech_ai_theme/static/src/webclient/sgc_webclient.xml',
            
            # Appsbar styling with enterprise look
            'sgc_tech_ai_theme/static/src/webclient/appsbar/sgc_appsbar_variables.scss',
            'sgc_tech_ai_theme/static/src/webclient/sgc_webclient.scss',
            'sgc_tech_ai_theme/static/src/webclient/appsbar/sgc_appsbar.scss',
            
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
