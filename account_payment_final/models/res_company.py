from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # OSUS Branding and Payment Settings
    use_osus_branding = fields.Boolean(
        string='Use OSUS Branding',
        default=True,
        help="Apply OSUS brand guidelines to payment vouchers"
    )
    
    auto_post_approved_payments = fields.Boolean(
        string='Auto-Post Approved Payments',
        default=False,
        help="Automatically post payments when approved"
    )
    
    max_approval_amount = fields.Monetary(
        string='Maximum Approval Amount',
        default=10000.0,
        help="Maximum amount that regular users can approve"
    )
    
    send_approval_notifications = fields.Boolean(
        string='Send Approval Notifications',
        default=True,
        help="Send email notifications for approval requests"
    )
    
    require_remarks_for_large_payments = fields.Boolean(
        string='Require Remarks for Large Payments',
        default=True,
        help="Require remarks for payments above the maximum approval amount"
    )
    
    voucher_footer_message = fields.Text(
        string='Voucher Footer Message',
        default='Thank you for your business with OSUS Properties',
        help="Custom footer message for payment vouchers"
    )
    
    voucher_terms = fields.Text(
        string='Voucher Terms',
        default='This is a computer-generated document. No physical signature required for system verification.',
        help="Terms and conditions text for payment vouchers"
    )
