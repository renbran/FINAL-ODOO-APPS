{
    'name': 'OSUS Invoice Report',
    'version': '17.0.1.0.0',
    'summary': 'Custom transparent invoice report for OSUS PROPERTIES',
    'category': 'Accounting',
    'author': 'OSUS PROPERTIES',
    'website': 'https://osusproperties.com',
    'depends': ['account'],
    'data': [
        'report/invoice_report.xml',
        'report/report_action.xml',
        'report/bill_report.xml',
        'report/bill_report_action.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
