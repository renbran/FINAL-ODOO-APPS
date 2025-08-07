from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Company-related fields (delegated)
    use_osus_branding = fields.Boolean(
        related='company_id.use_osus_branding',
        readonly=False,
        string='Use OSUS Branding',
        help="Apply OSUS brand guidelines to payment vouchers"
    )
    
    auto_post_approved_payments = fields.Boolean(
        related='company_id.auto_post_approved_payments',
        readonly=False,
        string='Auto-Post Approved Payments',
        help="Automatically post payments when approved"
    )
    
    max_approval_amount = fields.Monetary(
        related='company_id.max_approval_amount',
        readonly=False,
        string='Maximum Approval Amount',
        help="Maximum amount that regular users can approve"
    )
    
    send_approval_notifications = fields.Boolean(
        related='company_id.send_approval_notifications',
        readonly=False,
        string='Send Approval Notifications',
        help="Send email notifications for approval requests"
    )
    
    require_remarks_for_large_payments = fields.Boolean(
        related='company_id.require_remarks_for_large_payments',
        readonly=False,
        string='Require Remarks for Large Payments',
        help="Require remarks for payments above the maximum approval amount"
    )