{
    'name': 'OSUS Properties Backend Theme', 
    'summary': 'OSUS Properties Custom Backend Theme with Maroon & Gold Branding',
    'description': '''
        Custom backend theme for OSUS Properties featuring:
        - OSUS brand colors (Maroon #800020 & Gold #FFD700)
        - Mobile-responsive design
        - Enhanced user experience
        - Professional property management interface
    ''',
    'version': '17.0.1.2.1',
    'category': 'Themes/Backend', 
    'license': 'LGPL-3', 
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'live_test_url': '',
    'contributors': [
        'OSUS Properties Development Team',
    ],
    'depends': [
        'muk_web_chatter',
        'muk_web_dialog',
        'muk_web_appsbar',
        'muk_web_colors',
    ],
    'excludes': [
        'web_enterprise',
    ],
    'data': [
        'templates/web_layout.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            (
                'after', 
                'web/static/src/scss/primary_variables.scss', 
                'muk_web_theme/static/src/scss/colors.scss'
            ),
            (
                'after', 
                'web/static/src/scss/primary_variables.scss', 
                'muk_web_theme/static/src/scss/variables.scss'
            ),
        ],
        'web.assets_backend': [
            'muk_web_theme/static/src/webclient/**/*.xml',
            'muk_web_theme/static/src/webclient/**/*.scss',
            'muk_web_theme/static/src/webclient/**/*.js',
            'muk_web_theme/static/src/views/**/*.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/theme_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': '_setup_module',
    'uninstall_hook': '_uninstall_cleanup',
}
