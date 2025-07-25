{
    'name': 'OSUS Invoice Report - Enhanced with Bulk Printing & Smart Payment Vouchers',
    'version': '17.0.3.0.0',
    'summary': 'Professional UAE Tax Invoice Reports with Bulk Printing & Intelligent Payment Vouchers',
    'description': '''
        Professional Tax Invoice Reports with Advanced Features
        =====================================================
        - UAE VAT compliant invoice layout
        - Real estate commission specific fields
        - UK date format support
        - Amount in words conversion
        - Professional styling with Bootstrap 5
        - Multi-company support
        - Inheritance-safe implementation
        
        Bulk Printing Features
        =====================
        - Bulk print multiple customer invoices in single PDF
        - Bulk print multiple vendor bills in single PDF
        - Bulk print mixed documents (invoices, bills, credit notes)
        - Professional cover pages with document summaries
        - Enhanced list view actions for bulk operations
        - Dedicated bulk print menu structure
        - Document count and total amount summaries
        - Error handling and validation
        
        NEW: Smart Payment Voucher Enhancements
        =====================================
        - Intelligent document type detection (bills vs invoices)
        - Dynamic label generation ("Related bill" vs "Related invoice")
        - Multiple document support with detailed tables
        - Payment status indicators (full/partial payment)
        - Remaining balance calculations
        - Enhanced document reference formatting
        - Professional summary sections
        - Automatic reconciliation analysis
    ''',
    'category': 'Accounting/Accounting',
    'author': 'OSUS Real Estate',
    'website': 'https://www.osus.ae',
    'depends': ['account', 'base', 'sale', 'portal'],
    'external_dependencies': {
        'python': ['qrcode', 'num2words'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/report_paperformat.xml',
        'data/payment_sequences.xml',
        
        # Views
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/payment_fix_menu.xml',
        'views/sale_order_views.xml',
        'views/portal_templates.xml',
        'views/bulk_print_menus.xml',
        
        # Reports
        'report/report_action.xml',
        'report/bill_report_action.xml',
        'report/payment_voucher_report_action.xml',
        'report/invoice_report.xml',
        'report/bill_report.xml',
        'report/payment_voucher_report.xml',
        'report/bulk_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'osus_invoice_report/static/src/js/bulk_print_controller.js',
        ],
        'web.report_assets_pdf': [
            'osus_invoice_report/static/src/css/report_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'auto_install': False,
}