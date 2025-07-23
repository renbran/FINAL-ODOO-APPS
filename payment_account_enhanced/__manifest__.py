<<<<<<< HEAD
# -*- coding: utf-8 -*-
{
    'name': 'Payment Account Enhanced',
=======
{
    'name': 'Payment Voucher Enhanced',
>>>>>>> df3776f23c70d8392ffc74b64a8b82cb92048c30
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Enhanced Payment Voucher with Beautiful Receipt Generation',
    'description': """
<<<<<<< HEAD
        Enhanced Payment Account Module
        ===============================
        
        This module extends the account.payment model to provide:
        * Generate beautiful payment vouchers/receipts
        * Professional receipt templates with half A4 format
        * Enhanced payment voucher reporting
        * Custom paperformat for compact voucher printing
        
        Features:
        ---------
        * Payment voucher report with custom half A4 format
        * Professional receipt generation
        * Optimized margins and layout for voucher printing
=======
        This module extends the account.payment model to:
        - Generate beautiful payment vouchers/receipts
        - Make destination account visible and editable
        - Add custom fields for better voucher information
        - Provide professional receipt templates
>>>>>>> df3776f23c70d8392ffc74b64a8b82cb92048c30
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
<<<<<<< HEAD
    'demo': [],
=======
>>>>>>> df3776f23c70d8392ffc74b64a8b82cb92048c30
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
<<<<<<< HEAD
}
=======
}
>>>>>>> df3776f23c70d8392ffc74b64a8b82cb92048c30
