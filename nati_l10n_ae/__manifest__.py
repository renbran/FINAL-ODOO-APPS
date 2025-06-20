# -*- encoding: utf-8 -*-

{
    'name': 'Emirates Chart of Accounts standard',
    'version': '17.0.0.0',
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
     Arabic localization for most arabic countries.
    """,
    'depends': [
        'account',
        'base_iban',
        'base_vat',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_chart_template_data.xml',
        'data/account.group.csv',
        'data/account.account.template.csv',
        'data/l10n_ye_chart_data.xml',
        'data/account_chart_template_configure_data.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'post_init_hook': 'load_translations',
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {},
}
