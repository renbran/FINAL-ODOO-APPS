# -*- coding: utf-8 -*-
# Copyright 2025 OSUS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Enterprise Dynamic Accounting Reports',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Modern Enterprise-Level Dynamic Financial Reports with Professional UI/UX',
    'description': """
Enterprise Dynamic Accounting Reports
=====================================

A complete reimagining of dynamic financial reporting with enterprise-level features:

Key Features:
* Modern responsive dashboard interface
* Real-time financial analytics with interactive charts
* Advanced filtering and comparison tools
* Professional report layouts with export capabilities
* Mobile-responsive design
* Dark/Light theme support
* Role-based access controls
* Advanced drill-down capabilities
* Automated report scheduling
* Custom KPI widgets

Reports Included:
* Enhanced Balance Sheet with trend analysis
* Comprehensive Profit & Loss with variance analysis
* Advanced Trial Balance with drill-down
* Interactive General Ledger
* Partner Ledger with aging analysis
* Cash Flow Statement with projections
* Aged Receivables/Payables with action insights
* Tax Reports with compliance features
* Custom Financial Dashboards

Perfect for:
* Enterprise organizations requiring professional financial reporting
* Companies needing advanced financial analytics
* Organizations requiring mobile-friendly interfaces
* Businesses with complex reporting requirements
    """,
    'author': 'OSUS Enterprise Solutions',
    'company': 'OSUS',
    'maintainer': 'OSUS',
    'website': "https://osus.com",
    'depends': [
        'base',
        'account',
        'account_accountant',
        'web',
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # CSS/SCSS
            'enterprise_dynamic_reports/static/src/scss/enterprise_reports.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
