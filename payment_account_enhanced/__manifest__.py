{
    'name': 'Payment Voucher Enhanced',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Enhanced Payment Voucher with Beautiful Receipt Generation',
    'description': """
        This module extends the account.payment model to:
        - Generate beautiful payment vouchers/receipts
        - Make destination account visible and editable
        - Add custom fields for better voucher information
        - Provide professional receipt templates
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_account_views.xml',
        'reports/payment_voucher_report.xml',
        'reports/payment_voucher_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}