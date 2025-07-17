{
    'name': 'Automated Employee Announcements',
<<<<<<< HEAD
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Automated mails for employee birthdays and work anniversaries',
    'description': """
Automatically send announcement emails to all employees for birthdays and work anniversaries. Inherits and extends Odoo's automated mail rules.
=======
    'version': '17.0.1.1.0',
    'category': 'Human Resources',
    'summary': 'Automated mails for employee birthdays, work anniversaries, and sale order events',
    'description': """
Automatically send announcement emails to all employees for birthdays and work anniversaries. Also notifies agents for sale order events (invoiced, payment, deal status reminder). Inherits and extends Odoo's automated mail rules.
>>>>>>> staging
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'license': 'LGPL-3',
<<<<<<< HEAD
    'depends': ['base', 'hr', 'mail', 'web', 'hr_holidays'],
=======
    'depends': ['base', 'hr', 'mail', 'web', 'hr_holidays', 'sale_management'],
>>>>>>> staging
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/automated_mail_rule_data.xml',
        'data/mail_template_saleorder_invoiced.xml',
<<<<<<< HEAD
        'views/menu.xml',
        'views/automated_mail_rule_views.xml',
        'data/mail_template_saleorder_payment_initiated.xml',
        'data/mail_template_saleorder_deal_status_reminder.xml',
        'data/ir_cron_deal_status_reminder.xml',
=======
        'data/mail_template_saleorder_payment_initiated.xml',
        'data/mail_template_saleorder_deal_status_reminder.xml',
        'data/ir_cron_deal_status_reminder.xml',
        'views/menu.xml',
        'views/automated_mail_rule_views.xml',
>>>>>>> staging
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'automated_employee_announce/static/src/css/*.css',
            'automated_employee_announce/static/src/js/*.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
}
