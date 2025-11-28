# -*- coding: utf-8 -*-
{
    'name': 'HR Employment Certificate',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Generate Employment Certificates for Employees',
    'description': """
HR Employment Certificate
=========================
This module adds the ability to generate and print professional 
Employment Certificates for employees with OSUS Properties branding.

Features:
---------
* Professional Employment Certificate template
* OSUS Properties branded design (maroon and gold theme)
* Configurable certificate content
* Print-ready PDF output
* Reference number tracking
    """,
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/certificate_sequence.xml',
        'wizard/employment_certificate_wizard_views.xml',
        'report/employment_certificate_report.xml',
        'report/employment_certificate_template.xml',
        'views/hr_employee_views.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
