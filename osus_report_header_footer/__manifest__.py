# -*- coding: utf-8 -*-
{
    'name': 'OSUS Report Header Footer',
    'version': '17.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Custom header and footer with OSUS branding for all reports',
    'description': '''
        OSUS Report Header Footer
        =========================

        This module provides standardized headers and footers with OSUS branding
        for all PDF reports in the system.

        Key Features:
        ------------
        * Custom external layout with OSUS logo and branding
        * Professional header with company information
        * Footer with OSUS contact details and page numbers
        * Applies automatically to all reports
        * Customizable paper format with proper margins

        The module includes:
        -------------------
        * OSUS logo in header
        * Company information display
        * Consistent branding across all reports
        * Professional styling with CSS
    ''',
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'account',
    ],
    'data': [
        'data/report_paperformat.xml',
        'report/osus_external_layout.xml',
        'report/osus_branded_layout.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'osus_report_header_footer/static/src/css/report_style.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
