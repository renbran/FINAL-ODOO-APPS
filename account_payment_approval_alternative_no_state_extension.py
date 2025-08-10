# -*- coding: utf-8 -*-
#############################################################################
#
#    Alternative Payment Model - No State Extension
#    Uses separate voucher_state field instead of extending state
#
#############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, timedelta
import logging
import uuid
import qrcode
import io
import base64
from num2words import num2words

_logger = logging.getLogger(__name__)


class AccountPaymentUnified(models.Model):
    """Unified Payment with separate voucher workflow status"""
    _inherit = "account.payment"
    
    # Use a separate voucher_state field instead of extending state
    # This avoids any potential conflicts with the base state field
    voucher_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected'),
    ], string='Voucher Status', default='draft', tracking=True,
       help="Status of the payment voucher in the approval workflow")
    
    # Enhanced Voucher Information
    voucher_number = fields.Char(
        string='Voucher Number', 
        readonly=True, 
        copy=False,
        help="Auto-generated voucher number"
    )
    
    voucher_type = fields.Selection([
        ('payment', 'Payment Voucher'),
        ('receipt', 'Receipt Voucher')
    ], string='Voucher Type', compute='_compute_voucher_type', store=True,
       help="Type of voucher based on payment direction")
    
    requires_approval = fields.Boolean(
        string='Requires Approval', 
        compute='_compute_requires_approval',
        store=True,
        help="Whether this payment requires approval workflow"
    )
    
    # Workflow Dates
    submitted_date = fields.Datetime(string='Submitted Date', readonly=True)
    reviewed_date = fields.Datetime(string='Reviewed Date', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    authorized_date = fields.Datetime(string='Authorized Date', readonly=True)
    
    # Workflow Users
    reviewer_id = fields.Many2one('res.users', string='Reviewer', readonly=True)
    approver_id = fields.Many2one('res.users', string='Approver', readonly=True)
    authorizer_id = fields.Many2one('res.users', string='Authorizer', readonly=True)
    
    # Digital Signatures
    creator_signature = fields.Binary(string='Creator Signature', attachment=True)
    creator_signature_date = fields.Datetime(string='Creator Signature Date', readonly=True)
    
    reviewer_signature = fields.Binary(string='Reviewer Signature', attachment=True)
    reviewer_signature_date = fields.Datetime(string='Reviewer Signature Date', readonly=True)
    
    approver_signature = fields.Binary(string='Approver Signature', attachment=True)
    approver_signature_date = fields.Datetime(string='Approver Signature Date', readonly=True)
    
    authorizer_signature = fields.Binary(string='Authorizer Signature', attachment=True)
    authorizer_signature_date = fields.Datetime(string='Authorizer Signature Date', readonly=True)
    
    # QR Code and Verification
    verification_token = fields.Char(string='Verification Token', readonly=True, copy=False)
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code', attachment=True)
    verification_url = fields.Char(string='Verification URL', compute='_compute_verification_url')
    
    # Progress Tracking
    workflow_progress = fields.Float(string='Workflow Progress', compute='_compute_workflow_progress')
    next_action_user_ids = fields.Many2many('res.users', string='Next Action Users', compute='_compute_next_action_users')
    
    # Smart button fields
    signature_count = fields.Integer(string='Signature Count', compute='_compute_signature_count')
    verification_count = fields.Integer(string='Verification Count', compute='_compute_verification_count')
    
    # Permission fields
    is_approve_person = fields.Boolean(string='Can Approve', compute='_compute_is_approve_person')
    authorized_approvers_display = fields.Text(string='Authorized Approvers', compute='_compute_authorized_approvers_display')
    
    # Display Fields
    amount_in_words = fields.Char(string='Amount in Words', compute='_compute_amount_in_words')
    payment_method_display = fields.Char(string='Payment Method', compute='_compute_payment_method_display')
    company_currency = fields.Many2one('res.currency', related='company_id.currency_id', string='Company Currency')
    
    @api.depends('payment_type')
    def _compute_voucher_type(self):
        """Determine voucher type based on payment direction"""
        for record in self:
            if record.payment_type == 'outbound':
                record.voucher_type = 'payment'
            elif record.payment_type == 'inbound':
                record.voucher_type = 'receipt'
            else:
                record.voucher_type = 'payment'  # Default
    
    @api.depends('amount', 'voucher_type', 'partner_type')
    def _compute_requires_approval(self):
        """Determine if payment requires approval based on amount and type"""
        for record in self:
            # Get approval thresholds from system parameters
            payment_threshold = float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval_threshold', '1000.0'))
            receipt_threshold = float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.receipt_approval_threshold', '5000.0'))
            
            if record.voucher_type == 'payment':
                record.requires_approval = record.amount >= payment_threshold
            else:
                record.requires_approval = record.amount >= receipt_threshold
    
    # Override the workflow methods to use voucher_state instead of state
    def action_submit_for_approval(self):
        """Submit payment for approval"""
        for record in self:
            if record.voucher_state != 'draft':
                raise UserError(_("Only draft vouchers can be submitted for approval."))
            
            # Update voucher state instead of state
            record.write({
                'voucher_state': 'submitted',
                'submitted_date': fields.Datetime.now(),
            })
            
            # Create creator signature if not exists
            if not record.creator_signature_date:
                record._create_signature('creator')
            
            # Send notification
            record._send_notification('submitted')
            
            # Create activity for reviewers
            record._create_activity_for_next_users()
            
            record.message_post(
                body=_("Payment voucher submitted for approval by %s") % self.env.user.name,
                message_type='notification'
            )
    
    # Add all other methods here but using voucher_state instead of state
    # ... (rest of the methods would be similar but using voucher_state)
    
    # Keep all the existing computed field methods
    # ... (all the _compute methods remain the same)
