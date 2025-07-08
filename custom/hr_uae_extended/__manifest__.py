# -*- coding: utf-8 -*-
{
    'name': 'UAE HR Extended',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Extended HR features for UAE labor law compliance and agent commission management',
    'description': """
        This module extends the HR functionality with:
        * UAE Labor Law compliance features
        * Annual leave and ticket benefits management
        * Annual leave pay calculations
        * Default commission settings for agents
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'hr',
        'hr_holidays',
        'hr_payroll_community',
        'sale',
        'commission_ax',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_agent_commission_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
