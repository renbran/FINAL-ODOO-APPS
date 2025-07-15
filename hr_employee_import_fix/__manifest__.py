# -*- coding: utf-8 -*-
{
    'name': 'Employee Import Fix',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Fix employee import issues with resource constraints',
    'description': """
        This module fixes common issues when importing employees:
        - Handles missing resource_resource records
        - Auto-creates required resource records during employee creation
        - Provides safe import methods for bulk employee uploads
        
        Features:
        - Automatic resource record creation
        - Safe employee import with constraint handling
        - Bulk import utilities
        - Error prevention for foreign key violations
    """,
    'author': 'Custom Development',
    'depends': ['hr', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
