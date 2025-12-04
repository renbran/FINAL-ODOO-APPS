{
    "name": "Sale Deal Tracking",
    "version": "2.0.3",
    "summary": "Enhanced deal tracking for Sales and CRM with unified stages, UTM integration, and Commission Reporting",
    "description": """
        Sale Deal Tracking Module
        =========================

        Features:
        ---------
        * Links Sales Orders to CRM Opportunities/Leads
        * Unified deal stage tracking across CRM and Sales
        * Leverages standard Odoo UTM tracking (source, campaign, medium)
        * Automatic stage synchronization between CRM and Sales
        * Commission Report Button (visible only when commission lines exist)
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
        
        Commission Integration:
        ----------------------
        * Print Commission Report button in sale order header
        * Commission Lines smart button shows commission count
        * Only visible when commission lines exist
        * Opens detailed commission view and report printing
        * Integrates with commission_ax module for full workflow
    """,
    "author": "OSUSAPPS",
    "category": "Sales/CRM",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "crm",
        "utm",  # Standard Odoo UTM tracking
        "le_sale_type",  # For sale_order_type_id field
        "commission_ax",  # For commission report integration
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/crm_lead_views.xml",
        "views/sale_order_commission_button.xml",
        "data/deal_stage_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
