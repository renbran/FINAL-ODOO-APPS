{
    'name': 'OSUS Properties Chatter', 
    'summary': 'OSUS Branded Chatter with Enhanced Design',
    'description': '''
        OSUS Properties custom chatter module featuring:
        - Enhanced chatter design with OSUS branding
        - Customizable chatter position preferences
        - Improved user experience and visual consistency
    ''',
    'version': '17.0.1.2.0',
    'category': 'Tools/UI',
    'license': 'LGPL-3', 
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'live_test_url': '',
    'contributors': [
        'OSUS Properties Development Team',
    ],
    'depends': [
        'mail',
    ],
    'data': [
        'views/res_users.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            (
                'after', 
                'web/static/src/scss/primary_variables.scss', 
                'muk_web_chatter/static/src/scss/variables.scss'
            ),
        ],
        'web.assets_backend': [
            'muk_web_chatter/static/src/core/**/*.js',
            'muk_web_chatter/static/src/core/**/*.xml',
            'muk_web_chatter/static/src/core/**/*.scss',
            (
                'after', 
                'mail/static/src/views/web/form/form_compiler.js', 
                'muk_web_chatter/static/src/views/form/form_compiler.js'
            ),
            'muk_web_chatter/static/src/views/form/form_renderer.js',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
