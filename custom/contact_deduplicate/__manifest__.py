{
    'name': 'Contact Deduplicate',
    'version': '17.0.1.0.0',
    'summary': 'Advanced Contact Deduplication Tool',
    'description': """
Contact Deduplicate Module
=========================

This module provides advanced tools for identifying and merging duplicate contacts in Odoo.

Features:
---------
* Intelligent duplicate detection based on multiple criteria
* Fuzzy matching for names and addresses
* Bulk merge operations
* Detailed merge preview
* Configurable matching rules
* Merge history tracking
    """,
    'category': 'Tools',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/contact_merge_wizard_views.xml',
        'views/contact_duplicate_views.xml',
        'views/menu_views.xml',
        'data/duplicate_rules_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
