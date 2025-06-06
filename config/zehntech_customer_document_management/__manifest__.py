{
    "name": "Customer Document Management",
    "description": """ Centralize and streamline your customer document management directly within Odoo. Customer Document Management Odoo module empowers you to efficiently handle a high volume of customer-related documents through features like: Bulk document upload, automated expiry management this Odoo app track document expiration dates and configure automated email alerts to relevant users before, on, and after expiry, ensuring timely renewals and compliance. With real-time Analytics Dashboards feature gain clear visibility into the status of your customer documents with intuitive dashboards, allowing you to monitor progress and identify potential bottlenecks. Role-Based access control feature defines granular access permissions based on user roles, ensuring that sensitive customer documents are only accessible to authorized personnel. Customers can be restricted to viewing only their own documents, maintaining data privacy. With Organized Tagging and Categorization feature gives you a flexible system for tagging and categorizing documents, making it quick and easy to search, filter, and retrieve specific information when needed. Customer Document Management Odoo app enhances efficiency, reduces administrative overhead, improves compliance, and provides a secure and organized repository for all your critical customer documentation within your Odoo environment.""",
    "summary": """Customer Document Management Odoo App helps you to effortlessly manage customer documents within Odoo. Enable bulk uploads, automated expiry tracking with timely email notifications, insightful analytics dashboards, role-based access control, and streamlined organization through tagging and categorization.""",
    "version": "17.0.1.0.0",
    "category": "Document Management",
    "author": "Zehntech Technologies Inc.",
    "company": "Zehntech Technologies Inc.",
    "maintainer": "Zehntech Technologies Inc.",
    "contributor": "Zehntech Technologies Inc.",
    "website": "https://www.zehntech.com/",
    "support": "odoo-support@zehntech.com",
    "images": ["static/description/banner.png"],
    "depends": ['base', 'contacts','web'],
    "data": [
        "security/ir.model.access.csv",
        "security/res_partner_document_rules.xml",
        "data/email_templates.xml",
        "data/cron_jobs.xml",
        "views/res_config_settings_view.xml",
        "views/customer_document_dashboard.xml",
        "views/dashboard_menu.xml",
        "views/res_partner_document_views.xml",
        "views/document_dashboard_piechart.xml",
        "views/res_partner_document_search.xml",
        "views/customer_document_views.xml",
        "views/res_partner_views.xml",
       
    ],
    'assets': {
        'web.assets_backend': [
            'zehntech_customer_document_management/static/src/css/status.css'
            
        ],
    },
    'i18n': [
            'i18n/es.po',
            'i18n/fr.po',
            'i18n/de.po',
            'i18n/ja.po',
    ],
 
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 00.00,
    "currency": "USD"
}
