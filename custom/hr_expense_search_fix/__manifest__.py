{
    'name': 'HR Expense Search Fix',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Expenses',
    'summary': 'Fix undefined field errors in HR Expense search views',
    'description': """
        This module fixes common undefined field errors in HR Expense search views.

        Common Issues Fixed:
        - Missing project_id field references
        - Missing task_id field references
        - Missing analytic_account_id field references
        - Other undefined field references from uninstalled modules
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr_expense'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
