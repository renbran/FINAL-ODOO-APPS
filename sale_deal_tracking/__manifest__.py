{
    "name": "Sale Deal Tracking",
    "version": "2.0.0",
    "summary": "Enhanced deal tracking for Sales and CRM with unified stages and UTM integration",
    "description": """
        Sale Deal Tracking Module
        =========================

        Features:
        ---------
        * Links Sales Orders to CRM Opportunities/Leads
        * Unified deal stage tracking across CRM and Sales
        * Leverages standard Odoo UTM tracking (source, campaign, medium)
        * Automatic stage synchronization between CRM and Sales
        * Compatible with existing rental_management and UTM integrations

        Deal Stages:
        -----------
        - New: Initial contact
        - Attempt: Outreach in progress
        - Contacted: Successfully reached
        - Option Sent: Proposal/quote provided
        - Hot: High interest, likely to close
        - Idle: Low activity, needs follow-up
        - Junk: Not qualified, completely lost
        - Unsuccessful: Lost but follow up after 60 days
        - Customer (Won): Deal closed successfully
    """,
    "author": "OSUSAPPS",
    "category": "Sales/CRM",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "crm",
        "utm",  # Standard Odoo UTM tracking
        "le_sale_type",  # For sale_order_type_id field
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/crm_lead_views.xml",
        "data/deal_stage_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
