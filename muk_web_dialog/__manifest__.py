{
    'name': 'OSUS Properties Dialog', 
    'summary': 'OSUS Branded Dialog Components with Enhanced Options',
    'description': '''
        OSUS Properties custom dialog module featuring:
        - Full screen expansion capability
        - User preference customization
        - OSUS brand styling and colors
    ''',
    'version': '17.0.1.0.0', 
    'category': 'Tools/UI',
    'license': 'LGPL-3', 
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'live_test_url': '',
    'contributors': [
        'OSUS Properties Development Team',
    ],
    'depends': [
        'web',
    ],
    'data': [
        'views/res_users.xml',
    ],
    'assets': {
        'web.assets_backend': [
            (
                'after',
                'web/static/src/core/dialog/dialog.js',
                '/muk_web_dialog/static/src/core/dialog/dialog.js',
            ),
            (
                'after',
                'web/static/src/core/dialog/dialog.scss',
                '/muk_web_dialog/static/src/core/dialog/dialog.scss',
            ),
            (
                'after',
                'web/static/src/core/dialog/dialog.xml',
                '/muk_web_dialog/static/src/core/dialog/dialog.xml',
            ),
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
