# -*- coding: utf-8 -*-
{
    'name': 'Scholarix Global - Recruitment Extension',
    'version': '17.0.1.0.3',
    'category': 'Human Resources',
    'summary': 'UAE-compliant offer letters and recruitment extensions for Scholarix Global',
    'description': """
        Scholarix Global Recruitment Extension
        ========================================
        
        Features:
        ---------
        * Extended applicant fields for UAE compliance
        * Professional offer letter with Deep Ocean branding
        * Automated salary calculations (basic + allowances)
        * Email templates for offer letters
        * UAE Labour Law compliant templates
        * Comprehensive benefits tracking
        * Digital signature support
        * Offer validity tracking
        
        UAE Compliance:
        ---------------
        * Emirates ID and passport tracking
        * Visa sponsorship management
        * UAE standard probation period (180 days)
        * Annual leave entitlement (30 days minimum)
        * Health insurance requirements
        * Working hours and notice periods
        
        Brand Identity: Deep Ocean Palette
        -----------------------------------
        * Deep Navy (#0c1e34) - Authority & Trust
        * Ocean Blue (#1e3a8a) - Professionalism
        * Sky Blue (#4fc3f7) - Innovation
        * Ice White (#e8f4fd) - Clarity
        
        Technical Details:
        ------------------
        * Compatible with Odoo 17 Community & Enterprise
        * Extends standard hr_recruitment module
        * PDF report generation with QWeb
        * Responsive email templates
        * Multi-currency support
        
        Usage:
        ------
        1. Go to Recruitment > Applications
        2. Open any applicant record
        3. Fill Personal Information, Employment Details, Compensation tabs
        4. Navigate to Offer Letter tab
        5. Click "Generate Offer Letter" to preview
        6. Click "Send Offer Letter" to email candidate
        
        Author: Scholarix Global
        Tagline: Navigate. Innovate. Transform.
    """,
    'author': 'Scholarix Global',
    'website': 'https://www.scholarixglobal.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/hr_applicant_views.xml',
        
        # Reports
        'reports/offer_letter_template.xml',
        
        # Data
        'data/email_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'scholarix_recruitment/static/src/scss/report_styles.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.00,
    'currency': 'USD',
}
