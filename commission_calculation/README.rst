Commission Calculation
======================

This module now provides a full-featured, production-ready commission management system for Odoo 17, including:

Features:
---------
- Custom commission fields (amount, percentage, notes, etc.)
- Automatic commission calculation, confirmation, payment, and reset workflow
- Allocation status and commission percentage tracking
- Internal commission base (company share after external commission)
- Button actions for all commission workflow steps
- Odoo 17 best practices and improved security
- Simple tree and form views

Installation:
-------------
- Copy this module to your Odoo addons directory
- Update the app list and install via Odoo UI

Usage:
------
- Go to Sales > Commission Calculation
- Use the Commission tab to manage and track all commission details
- Use the provided buttons to calculate, confirm, pay, or reset commissions
- All commission data is visible and tracked for reporting and auditing

Best Practices:
---------------
- Always calculate and confirm commissions before confirming the sales order
- Do not modify commission fields after confirmation unless the commission is reset to draft
- Use the provided UI actions for all commission-related workflows
