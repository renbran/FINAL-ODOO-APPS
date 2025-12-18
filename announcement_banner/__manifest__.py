# -*- coding: utf-8 -*-
{
    'name': 'Announcement Banner - OSUSAPPS',
    'version': '17.0.1.2.2',
    'category': 'Productivity/Communications',
    'summary': 'Professional Announcement Banners with Rich Content Support',
    'description': """
        OSUSAPPS Announcement Banner Module
        ====================================

        Professional popup announcement system for Odoo 17 Enterprise

        Key Features:
        ============
        * 📢 Elegant popup announcements on user login
        * 🎨 Rich HTML content with images, formatting, and styling
        * 📅 Schedule announcements with start/end dates
        * 👥 Target specific users or entire organization
        * 🔔 Show once or recurring notification options
        * ⚡ Priority-based display ordering
        * 📊 Track announcement views and engagement
        * 📱 Fully responsive mobile-friendly design
        * 🎯 Multi-announcement navigation

        Production Features:
        ===================
        * ✅ Production-ready with OSUSAPPS branding
        * ✅ Proper text and image rendering (no HTML code visible)
        * ✅ Optimized CSS for professional appearance
        * ✅ Enhanced security and access controls
        * ✅ WYSIWYG editor for easy content creation
        * ✅ Mobile responsive with elegant animations

        Version 1.1.0 Updates:
        =====================
        * PRODUCTION READY: Professional branding and polish
        * FIXED: Text rendering with proper word-break behavior
        * ENHANCED: Image display with responsive styling
        * IMPROVED: Footer branding with OSUSAPPS attribution
        * OPTIMIZED: CSS for better readability and appearance

        Perfect for:
        ===========
        * System maintenance notifications
        * New feature announcements
        * Policy updates and compliance notices
        * Holiday schedules and company events
        * Emergency alerts and critical communications
        * Training reminders and onboarding messages
    """,
    'author': 'OSUSAPPS - Enterprise Odoo Solutions',
    'website': 'https://www.osusapps.com',
    'maintainer': 'OSUSAPPS',
    'support': 'support@osusapps.com',
    'depends': ['web', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/announcement_banner_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'announcement_banner/static/src/js/announcement_banner.js',
            'announcement_banner/static/src/xml/announcement_banner.xml',
            'announcement_banner/static/src/css/announcement_banner.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
