# -*- coding: utf-8 -*-
{
    'name': 'LLM Lead Scoring',
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'AI-Powered Lead Scoring with Multi-LLM Support',
    'description': """
LLM Lead Scoring Module
========================
This module enhances Odoo CRM with AI-powered lead scoring capabilities:

Features:
---------
* Multi-LLM Provider Support (OpenAI, Groq, HuggingFace, Anthropic, etc.)
* Automated customer research from publicly available sources
* AI-driven lead probability scoring based on:
  - Form completeness
  - Requirement clarity
  - Customer activity/intervention logs
* Enrichment data logging in internal notes
* Real-time and scheduled lead enrichment
* Configurable scoring algorithms
* Customizable LLM prompts and parameters

The module leverages LLM reasoning capabilities to help sales teams:
- Properly allocate efforts based on lead quality
- Get enhanced customer insights
- Improve conversion rates
- Automate lead qualification

    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/llm_provider_data.xml',
        'data/ir_cron_data.xml',
        'views/llm_provider_views.xml',
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
        'wizards/lead_enrichment_wizard_views.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
