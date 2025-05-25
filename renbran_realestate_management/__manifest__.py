# __manifest__.py
{
    'name': 'Property Management',
    'version': '17.1',
    'summary': 'Comprehensive property management system with offers, sales, and commissions',
    'description': '''
        Advanced Property Management System
        ==================================
        
        This module provides a complete solution for property management, sales and commission tracking:
        
        Features:
        - Detailed property information management
        - Property offer system with document verification
        - Flexible payment scheduling and installment tracking
        - Integrated broker commission calculation and tracking
        - Internal commission management for sales team
        - Complete integration with accounting for invoicing and payment tracking
        - Comprehensive reporting on properties, sales, and commissions
    ''',
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'category': 'Real Estate',
    'depends': [
        'base',
        'mail',
        'account',
        'web',
    ],
    'data': [
        # Security
        'security/property_management_security.xml',
        'security/ir.model.access.csv',
        
        # Data files
        'data/property_sequence.xml',
        'data/commission_data.xml',
        
        # Views
        'views/property_views.xml',
        'views/property_offer_views.xml',
        'views/property_sale_views.xml',
        'views/broker_commission_views.xml',
        'views/internal_commission_views.xml',
        'views/commission_rule_views.xml',
        'views/menu_views.xml',
        
        # Reports
        'reports/property_management.xml',
        'reports/property_sale_report_template.xml',
    ],
    'demo': [
        'demo/property_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'property_management/static/src/css/property_dashboard.css',
            'property_management/static/src/js/property_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 1,
}
