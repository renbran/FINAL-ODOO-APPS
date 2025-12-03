# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    "name": "Advanced Property Sale & Rental Management | Real Estate | Property Sales | Property Rental | Property Management",
    "description": """
        Property Sale & Rental Management System
        
        Key Features:
        - Property Sale & Rental Management
        - Lease Contract Management
        - Landlord & Customer Management
        - Property Maintenance
        - Customer Recurring Invoice
        - Flexible Payment Plans with Templates
        - Professional SPA Reports
        - Bank Account Integration
        
        Version 3.4.1 Updates:
        - Two-stage payment workflow (Draft → Booked → Sold)
        - Booking requirements validation before installments
        - Payment progress tracking and status monitoring
        - Enhanced payment invoice categorization
        - Backward compatibility for existing contracts
        - Improved user experience with detailed error messages
        
        Version 3.4.2 Updates:
        - Configurable booking percentage at project and property levels
        - Automatic inheritance: Project → Property → Sale Contract
        - Property-level override for custom booking requirements
        - Support for different booking percentages per project (5%, 10%, 15%, 20%, etc.)
        - Enhanced UI with booking configuration sections
        
        Version 3.5.0 Updates (Invoice Tracking Enhancement):
        - 6 Smart Buttons for instant invoice tracking (Booking, Installments, All, Created, Paid, Maintenance)
        - Visual Payment Progress Dashboard with real-time statistics
        - Booking Requirements Monitoring with completion indicators
        - Guided Workflow for booking to installment creation
        - Payment Progress Charts showing percentage completion
        - Automated Validation preventing workflow errors
        - One-Click Invoice Creation for booking fees, DLD, and admin fees
        - Color-coded invoice tree view (Green=Paid, Orange=Partial, Gray=Not Created)
        - Enhanced header buttons organized by workflow phase
        - Getting Started guide for new users
        - Comprehensive documentation (3 detailed guides)
        - 100% backward compatible with v3.4.x
    """,
    "summary": """
        Property Sale & Rental Management with Enhanced Invoice Tracking, Visual Payment Dashboard, Smart Buttons, and Professional SPA Reports
    """,
    "version": "17.0.3.5.0",
    "author": "TechKhedut Inc.",
    "company": "TechKhedut Inc.",
    "maintainer": "TechKhedut Inc.",
    "website": "https://www.techkhedut.com",
    "category": "Services",
    "depends": [
        "mail",
        "contacts",
        "account",
        "hr",
        "maintenance",
        "crm",
        "crm_ai_field_compatibility",  # Required for ai_enrichment_report field
        "website",
        "base",
        "web",
    ],
    "data": [
        # security
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        # Report ACTIONS must load first (before any views reference them)
        "data/report_actions.xml",
        # Data
        "data/ir_cron.xml",
        "data/sequence.xml",
        "data/property_product_data.xml",
        "data/update_ir_cron.xml",
        "data/payment_schedule_data.xml",
        "data/cleanup_orphaned_fields.xml",
        # Report TEMPLATES load after actions are created
        "report/tenancy_details_report_template.xml",
        "report/property_details_report_v2.xml",
        "report/property_sold_report.xml",
        "report/sales_offer_template.xml",  # Client proposal/quotation for property.vendor
        "report/sales_offer_property_template.xml",  # Client proposal for property.details
        "report/sales_purchase_agreement.xml",  # Formal legal contract
        "report/invoice_report_inherit.xml",
        # wizard views
        "wizard/contract_wizard_view.xml",
        "wizard/property_payment_wizard_view.xml",
        "wizard/extend_contract_wizard_view.xml",
        "wizard/property_vendor_wizard_view.xml",
        "wizard/property_maintenance_wizard_view.xml",
        "wizard/booking_wizard_view.xml",
        "wizard/property_sale_tenancy_xls_report_view.xml",
        "wizard/landlord_tenancy_sold_xls_view.xml",
        "wizard/booking_inquiry_view.xml",
        "wizard/active_contract_view.xml",
        "wizard/subproject_creation_view.xml",
        "wizard/unit_creation_view.xml",
        "wizard/agreement_preview_view.xml",
        # Views
        "views/assets.xml",
        "views/payment_schedule_views.xml",
        "views/property_details_view.xml",
        "views/property_document_view.xml",
        "views/user_type_view.xml",
        "views/tenancy_details_view.xml",
        "views/contract_duration_view.xml",
        "views/rent_invoice_view.xml",
        "views/property_amenities_view.xml",
        "views/property_specification_view.xml",
        "views/property_vendor_view.xml",
        "views/certificate_type_view.xml",
        "views/parent_property_view.xml",
        "views/property_tag_view.xml",
        "views/product_product_inherit_view.xml",
        "views/property_invoice_inherit.xml",
        "views/res_config_setting_view.xml",
        "views/property_res_city.xml",
        "views/nearby_connectivity_view.xml",
        "views/agreement_template_view.xml",
        "views/configuration_views.xml",
        "views/property_region_views.xml",
        "views/property_project_view.xml",
        "views/property_sub_project_views.xml",
        "views/rent_bill_view.xml",
        "views/templates/property_web_template.xml",
        # Inherit Views
        "views/maintenance_product_inherit.xml",
        "views/property_maintenance_view.xml",
        "views/property_crm_lead_inherit_view.xml",
        # Mail Template
        "data/active_contract_mail_template.xml",
        "data/tenancy_reminder_mail_template.xml",
        "data/property_book_mail_template.xml",
        "data/property_sold_mail_template.xml",
        "data/sale_invoice_mail_template.xml",
        # menus
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # CRITICAL: Load DOM protection FIRST to prevent querySelector errors
            ('prepend', "rental_management/static/src/js/global_dom_protection.js"),
            ('prepend', "rental_management/static/src/js/list_renderer_fix.js"),
            ('prepend', "rental_management/static/src/js/property_dashboard_action.js"),
            
            # Then load regular assets
            "rental_management/static/src/css/style.css",
            "rental_management/static/src/css/lib/image-uploader.min.css",
            "rental_management/static/src/js/lib/image-uploader.min.js",
            "rental_management/static/src/xml/template.xml",
            "rental_management/static/src/scss/style.scss",
            "rental_management/static/src/js/lib/index.js",
            "rental_management/static/src/js/lib/map.js",
            "rental_management/static/src/js/lib/xy.js",
            "rental_management/static/src/js/lib/worldLow.js",
            "rental_management/static/src/js/lib/Animated.js",
            "rental_management/static/src/js/lib/apexcharts.js",
            "rental_management/static/src/js/rental.js",
            'rental_management/static/src/components/**/*',
            'rental_management/static/src/views/**/*',
        ],
        "web.assets_frontend": [
            "rental_management/static/src/css/extra.css",
        ],
    },
    "images": [
        "static/description/property-rental.gif",
    ],
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 250,
    "currency": "USD",
}
