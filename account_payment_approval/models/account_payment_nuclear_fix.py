# -*- coding: utf-8 -*-
#############################################################################
#
#    Nuclear Fix - Payment Model WITHOUT State Extension
#    This version completely avoids state field conflicts
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
    """Payment with separate voucher workflow - NO STATE EXTENSION"""
    _inherit = "account.payment"
    
    # DO NOT EXTEND STATE FIELD - Use separate field to avoid conflicts
    # state = fields.Selection(...)  # REMOVED - causes conflicts
    
    # Use separate voucher_state field for workflow
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
    
    @api.depends('voucher_state', 'voucher_type')
    def _compute_workflow_progress(self):
        """Calculate workflow progress percentage"""
        for record in self:
            if record.voucher_state == 'draft':
                record.workflow_progress = 0.0
            elif record.voucher_state == 'submitted':
                record.workflow_progress = 16.67
            elif record.voucher_state == 'under_review':
                record.workflow_progress = 33.33
            elif record.voucher_state == 'approved':
                if record.voucher_type == 'payment':
                    record.workflow_progress = 50.0  # Still needs authorization
                else:
                    record.workflow_progress = 66.67  # Skip approval for receipts
            elif record.voucher_state == 'authorized':
                record.workflow_progress = 83.33
            elif record.voucher_state == 'posted':
                record.workflow_progress = 100.0
            elif record.voucher_state == 'rejected':
                record.workflow_progress = 0.0
            else:
                record.workflow_progress = 0.0
    
    # Workflow Methods using voucher_state
    def action_submit_for_approval(self):
        """Submit payment for approval"""
        for record in self:
            if record.voucher_state != 'draft':
                raise UserError(_("Only draft vouchers can be submitted for approval."))
            
            # Update voucher state
            record.write({
                'voucher_state': 'submitted',
                'submitted_date': fields.Datetime.now(),
            })
            
            # Create creator signature if not exists
            if not record.creator_signature_date:
                record._create_signature('creator')
            
            # Send notification
            record._send_notification('submitted')
            
            record.message_post(
                body=_("Payment voucher submitted for approval by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_review(self):
        """Review payment"""
        for record in self:
            if record.voucher_state != 'submitted':
                raise UserError(_("Only submitted vouchers can be reviewed."))
            
            record.write({
                'voucher_state': 'under_review',
                'reviewed_date': fields.Datetime.now(),
                'reviewer_id': self.env.user.id,
            })
            
            # Create reviewer signature
            record._create_signature('reviewer')
            
            record.message_post(
                body=_("Payment voucher reviewed by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_approve(self):
        """Approve payment (only for payment vouchers)"""
        for record in self:
            if record.voucher_type != 'payment':
                raise UserError(_("Only payment vouchers require approval step."))
            
            if record.voucher_state != 'under_review':
                raise UserError(_("Only vouchers under review can be approved."))
            
            record.write({
                'voucher_state': 'approved',
                'approved_date': fields.Datetime.now(),
                'approver_id': self.env.user.id,
            })
            
            # Create approver signature
            record._create_signature('approver')
            
            record.message_post(
                body=_("Payment voucher approved by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_authorize(self):
        """Authorize payment"""
        for record in self:
            expected_state = 'approved' if record.voucher_type == 'payment' else 'under_review'
            if record.voucher_state != expected_state:
                raise UserError(_("Voucher is not in the correct state for authorization."))
            
            record.write({
                'voucher_state': 'authorized',
                'authorized_date': fields.Datetime.now(),
                'authorizer_id': self.env.user.id,
            })
            
            # Create authorizer signature
            record._create_signature('authorizer')
            
            record.message_post(
                body=_("Payment voucher authorized by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_post(self):
        """Post payment"""
        for record in self:
            # Call the original post method
            super(AccountPaymentUnified, record).action_post()
            
            # Update voucher state
            if record.voucher_state != 'posted':
                record.voucher_state = 'posted'
    
    def action_reject(self):
        """Reject payment"""
        for record in self:
            record.write({
                'voucher_state': 'rejected',
            })
            
            record.message_post(
                body=_("Payment voucher rejected by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_reset_to_draft(self):
        """Reset to draft state"""
        for record in self:
            record.write({
                'voucher_state': 'draft',
            })
    
    def action_qr_verification_view(self):
        """Open QR verification view in new window"""
        self.ensure_one()
        if not self.verification_token:
            raise UserError(_("No verification token found for this payment."))
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        verification_url = f"{base_url}/payment/verify/{self.verification_token}"
        
        return {
            'type': 'ir.actions.act_url',
            'name': _('QR Verification'),
            'url': verification_url,
            'target': 'new',
        }
    
    # Helper Methods
    def _create_signature(self, signature_type):
        """Create digital signature placeholder"""
        # This would contain actual signature logic
        field_map = {
            'creator': 'creator_signature_date',
            'reviewer': 'reviewer_signature_date',
            'approver': 'approver_signature_date',
            'authorizer': 'authorizer_signature_date',
        }
        
        if signature_type in field_map:
            self.write({field_map[signature_type]: fields.Datetime.now()})
    
    def _send_notification(self, action):
        """Send notification for workflow action"""
        # Placeholder for notification logic
        pass
    
    @api.depends('voucher_state')
    def _compute_next_action_users(self):
        """Compute users who can perform next action"""
        for record in self:
            users = self.env['res.users']
            # Add logic to determine next action users
            record.next_action_user_ids = users
    
    @api.depends('creator_signature_date', 'reviewer_signature_date', 'approver_signature_date', 'authorizer_signature_date')
    def _compute_signature_count(self):
        """Count signatures"""
        for record in self:
            count = 0
            if record.creator_signature_date:
                count += 1
            if record.reviewer_signature_date:
                count += 1
            if record.approver_signature_date:
                count += 1
            if record.authorizer_signature_date:
                count += 1
            record.signature_count = count
    
    def _compute_verification_count(self):
        """Count verifications"""
        for record in self:
            record.verification_count = 1 if record.verification_token else 0
    
    @api.depends('amount', 'currency_id')
    def _compute_amount_in_words(self):
        """Convert amount to words"""
        for record in self:
            if record.amount:
                try:
                    words = num2words(record.amount, lang='en')
                    record.amount_in_words = words.title()
                except:
                    record.amount_in_words = str(record.amount)
            else:
                record.amount_in_words = ''
    
    def _compute_payment_method_display(self):
        """Display payment method"""
        for record in self:
            if record.payment_method_line_id:
                record.payment_method_display = record.payment_method_line_id.name
            else:
                record.payment_method_display = ''
    
    def _compute_is_approve_person(self):
        """Check if user can approve"""
        for record in self:
            record.is_approve_person = self.env.user.has_group('account_payment_approval.group_payment_voucher_approver')
    
    def _compute_authorized_approvers_display(self):
        """Display authorized approvers"""
        for record in self:
            record.authorized_approvers_display = "Authorized Approvers List"
    
    @api.depends('verification_token')
    def _compute_qr_code(self):
        """Generate QR code"""
        for record in self:
            if record.verification_token:
                # QR code generation logic
                record.qr_code = b'placeholder_qr_code'
            else:
                record.qr_code = False
    
    @api.depends('verification_token')
    def _compute_verification_url(self):
        """Generate verification URL"""
        for record in self:
            if record.verification_token:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                record.verification_url = f"{base_url}/payment/verify/{record.verification_token}"
            else:
                record.verification_url = False
    
    @api.model
    def create(self, vals):
        """Override create to generate voucher number and token"""
        if not vals.get('voucher_number'):
            vals['voucher_number'] = self.env['ir.sequence'].next_by_code('payment.voucher') or 'PV00001'
        
        if not vals.get('verification_token'):
            vals['verification_token'] = str(uuid.uuid4())
        
        return super().create(vals)
