{
    'name': 'HR Expense Search Fix',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Fix undefined field error in HR Expense search view',
    'depends': ['hr_expense'],
    'data': [
        'views/hr_expense_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
