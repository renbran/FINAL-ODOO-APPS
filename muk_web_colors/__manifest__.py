{
    'name': 'OSUS Properties Colors', 
    'summary': 'OSUS Properties Brand Color System',
    'description': '''
        OSUS Properties color customization module featuring:
        - Brand maroon (#800020) and gold (#FFD700) colors
        - Light and dark mode support
        - Consistent brand identity across all interfaces
    ''',
    'version': '17.0.1.0.5',
    'category': 'Tools/UI',
    'license': 'LGPL-3', 
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'live_test_url': '',
    'contributors': [
        'OSUS Properties Development Team',
    ],
    'depends': [
        'base_setup',
        'web_editor',
    ],
    'data': [
        'templates/webclient.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'muk_web_colors/static/src/scss/colors.scss'),
            (
                'before', 
                'muk_web_colors/static/src/scss/colors.scss', 
                'muk_web_colors/static/src/scss/colors_light.scss'
            ),
        ],
        'web.assets_web_dark': [
            (
                'after', 
                'muk_web_colors/static/src/scss/colors.scss', 
                'muk_web_colors/static/src/scss/colors_dark.scss'
            ),
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': '_uninstall_cleanup',
}
