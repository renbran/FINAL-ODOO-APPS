# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Payment Voucher Settings
    auto_post_approved_payments = fields.Boolean(
        related='company_id.auto_post_approved_payments',
        readonly=False,
        string='Auto-Post Approved Payments'
    )
    
    max_approval_amount = fields.Monetary(
        related='company_id.max_approval_amount',
        readonly=False,
        string='Maximum Approval Amount'
    )
    
    send_approval_notifications = fields.Boolean(
        related='company_id.send_approval_notifications',
        readonly=False,
        string='Send Email Notifications'
    )
    
    use_osus_branding = fields.Boolean(
        related='company_id.use_osus_branding',
        readonly=False,
        string='Use OSUS Branding'
    )
    
    voucher_footer_message = fields.Text(
        related='company_id.voucher_footer_message',
        readonly=False,
        string='Voucher Footer Message'
    )
    
    # Invoice Approval Settings
    auto_post_approved_invoices = fields.Boolean(
        related='company_id.auto_post_approved_invoices',
        readonly=False,
        string='Auto-Post Approved Invoices'
    )
    
    invoice_approval_threshold = fields.Monetary(
        related='company_id.invoice_approval_threshold',
        readonly=False,
        string='Invoice Approval Threshold'
    )


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Payment Voucher Settings
    auto_post_approved_payments = fields.Boolean(
        string='Auto-Post Approved Payments',
        default=False,
        help="Automatically post payments when approved"
    )
    
    max_approval_amount = fields.Monetary(
        string='Maximum Approval Amount',
        currency_field='currency_id',
        default=10000.0,
        help="Maximum amount that can be approved without additional authorization"
    )
    
    send_approval_notifications = fields.Boolean(
        string='Send Email Notifications',
        default=True,
        help="Send email notifications for approval workflow"
    )
    
    use_osus_branding = fields.Boolean(
        string='Use OSUS Branding',
        default=True,
        help="Apply OSUS brand styling to reports"