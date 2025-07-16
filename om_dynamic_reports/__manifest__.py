# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Mates, Walnut Software Solutions
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'Enhanced Dynamic Financial Reports - Enterprise Edition',
    'version': '17.0.2.0.0',
    'category': 'Accounting',
    'summary': 'Complete Enterprise-Style Financial Reporting Suite for Odoo 17',
    'description': """
        Enhanced Dynamic Financial Reports - Enterprise Edition
        
        🚀 Complete Financial Reporting Suite:
        =====================================
        
        📊 Core Reports:
        • General Ledger with advanced filtering and drill-down
        • Trial Balance with comparative analysis
        • Balance Sheet with enterprise-style formatting
        • Profit & Loss Statement with trend analysis
        • Cash Flow Statement with detailed categorization
        • Partner Ledger with aging analysis
        
        ✨ Enterprise Features:
        • Modern, responsive UI design
        • Interactive charts and graphs
        • Advanced filtering and sorting
        • Drill-down capabilities
        • Multi-format export (PDF, Excel, CSV)
        • Real-time data updates
        • Mobile-friendly interface
        
        🎨 Design:
        • Enterprise-grade styling
        • Professional layouts
        • Accessibility compliant
        • Print-optimized
        
        🔧 Technical:
        • Optimized performance
        • Multi-company support
        • Extensible architecture
        • Clean, maintainable code
    """,
    'sequence': '1',
    'website': 'https://github.com/renbran/odoo17_final',
    'author': 'Enhanced by GitHub Copilot - Based on Odoo Mates & Cybrosys',
    'maintainer': 'Enterprise Financial Reports Team',
    'license': 'LGPL-3',
    'support': 'enterprise.reports@example.com',
    'depends': [
        'account',
        'base_accounting_kit',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/report_views.xml',
        'report/trial_balance.xml',
        'report/general_ledger_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'om_dynamic_reports/static/src/css/enterprise_reports.css',
            'om_dynamic_reports/static/src/css/report_styles.css',
            'om_dynamic_reports/static/src/xml/general_ledger.xml',
            'om_dynamic_reports/static/src/xml/trial_balance.xml',
            'om_dynamic_reports/static/src/xml/balance_sheet.xml',
            'om_dynamic_reports/static/src/xml/profit_loss.xml',
            'om_dynamic_reports/static/src/xml/partner_ledger.xml',
            'om_dynamic_reports/static/src/xml/cash_flow.xml',
            'om_dynamic_reports/static/src/js/general_ledger.js',
            'om_dynamic_reports/static/src/js/trial_balance.js',
            'om_dynamic_reports/static/src/js/balance_sheet.js',
            'om_dynamic_reports/static/src/js/profit_and_loss.js',
            'om_dynamic_reports/static/src/js/partner_ledger.js',
            'om_dynamic_reports/static/src/js/cash_flow.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
