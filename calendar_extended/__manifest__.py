# -*- coding: utf-8 -*-
{
    'name': 'Calendar Extended - Meeting Announcements',
    'version': '17.0.1.0.0',
    'category': 'Productivity/Calendar',
    'summary': 'Calendar with approval workflow and scheduled announcements',
    'description': """
        Calendar Extended Module - Meeting Announcements
        
        Core Features:
        - Meeting announcements with approval workflow (Draft → Review → Approved)
        - Manual/scheduled invitation sending (no automatic sending)
        - Easy employee selection by department or "select all"
        - Controlled meeting invitation distribution
        
        Workflow:
        1. Create meeting announcement (Draft state)
        2. Review and approve (Review → Approved state)
        3. Send invitations manually or schedule them
        4. Department-wise employee selection for easy management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'calendar', 'mail', 'hr'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/calendar_security.xml',
        
        # Data
        'data/mail_templates.xml',
        'data/cron_jobs.xml',
        
        # Views
        'views/calendar_announcement_views.xml',
        'views/calendar_extended_menus.xml',
        
        # Wizards
        'wizard/calendar_send_invitation_wizard_views.xml',
        'wizard/calendar_department_select_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'calendar_extended/static/src/js/calendar_extended.js',
            'calendar_extended/static/src/css/calendar_extended.css',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
