# -*- coding: utf-8 -*-
{
    'name': 'OSUS Global PDF Template',
    'version': '17.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Apply OSUS branded template to all PDF reports globally',
    'description': '''
        OSUS Properties - Global PDF Report Template
        ============================================
        
        Applies the official OSUS Properties template design to ALL PDF reports:
        - Automatic watermark/background on every report
        - Professional OSUS branding
        - No per-report configuration needed
        - Clean, modern implementation
        - Compatible with all Odoo report types
        
        This module uses a clean approach without complex background logic,
        simply overlaying the OSUS template on every generated PDF report.
    ''',
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.report_assets_common': [
            'osus_global_pdf_template/static/src/css/report_template.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
