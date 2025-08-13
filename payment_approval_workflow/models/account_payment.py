import base64
import uuid
import qrcode
from io import BytesIO
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Payment with Approval Workflow'

    # Approval State Field
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected'),
    ], string='Approval Status', default='draft', tracking=True, copy=False,
       help="Current approval status of the payment")

    # Rejection Management
    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True,
        help="Reason for rejection if payment was rejected"
    )

    # QR Code Verification
    verification_token = fields.Char(
        string='Verification Token',
        copy=False,
        readonly=True,
        help="Unique token for QR code verification"
    )
    
    qr_code_image = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code_image',
        store=False,
        help="QR code for payment verification"
    )

    # Digital Signatures
    review_signature = fields.Binary(
        string='Reviewer Signature',
        attachment=True,
        help="Digital signature of the reviewer"
    )
    approval_signature = fields.Binary(
        string='Approver Signature',
        attachment=True,
        help="Digital signature of the approver"
    )
    authorization_signature = fields.Binary(
        string='Authorizer Signature',
        attachment=True,
        help="Digital signature of the authorizer"
    )

    # Approval Tracking Fields
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        readonly=True,
        tracking=True,
        help="User who reviewed this payment"
    )
    review_date = fields.Datetime(
        string='Review Date',
        readonly=True,
        tracking=True,
        help="Date and time when payment was reviewed"
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True,
        help="User who approved this payment"
    )
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        tracking=True,
        help="Date and time when payment was approved"
    )
    
    authorizer_id = fields.Many2one(
        'res.users',
        string='Authorized By',
        readonly=True,
        tracking=True,
        help="User who authorized this payment"
    )
    authorization_date = fields.Datetime(
        string='Authorization Date',
        readonly=True,
        tracking=True,
        help="Date and time when payment was authorized"
    )
    
    submitted_by_id = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True,
        tracking=True,
        help="User who submitted this payment for review"
    )
    submission_date = fields.Datetime(
        string='Submission Date',
        readonly=True,
        tracking=True,
        help="Date and time when payment was submitted"
    )

    # Computed Fields
    can_submit = fields.Boolean(
        compute='_compute_action_permissions',
        help="Whether current user can submit this payment"
    )
    can_review = fields.Boolean(
        compute='_compute_action_permissions',
        help="Whether current user can review this payment"
    )
    can_approve = fields.Boolean(
        compute='_compute_action_permissions',
        help="Whether current user can approve this payment"
    )
    can_authorize = fields.Boolean(
        compute='_compute_action_permissions',
        help="Whether current user can authorize this payment"
    )
    can_reject = fields.Boolean(
        compute='_compute_action_permissions',
        help="Whether current user can reject this payment"
    )

    verification_url = fields.Char(
        compute='_compute_verification_url',
        help="Public URL for payment verification"
    )

    @api.depends('verification_token')
    def _compute_verification_url(self):
        """Compute the public verification URL"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for payment in self:
            if payment.verification_token:
                payment.verification_url = f"{base_url}/payment/verify/{payment.verification_token}"
            else:
                payment.verification_url = False

    @api.depends('verification_token')
    def _compute_qr_code_image(self):
        """Generate QR code for payment verification"""
        for payment in self:
            if payment.verification_token:
                payment.qr_code_image = payment._generate_qr_code()
            else:
                payment.qr_code_image = False

    @api.depends('approval_state')
    def _compute_action_permissions(self):
        """Compute what actions current user can perform"""
        for payment in self:
            user = self.env.user
            
            # Initialize all permissions to False
            payment.can_submit = False
            payment.can_review = False
            payment.can_approve = False
            payment.can_authorize = False
            payment.can_reject = False
            
            if payment.approval_state == 'draft':
                # Anyone who can write can submit
                payment.can_submit = payment._check_write_access()
                
            elif payment.approval_state == 'submitted':
                # Only reviewers can review or reject
                payment.can_review = user.has_group('payment_approval_workflow.group_payment_reviewer')
                payment.can_reject = user.has_group('payment_approval_workflow.group_payment_reviewer')
                
            elif payment.approval_state == 'reviewed':
                # Only approvers can approve or reject
                payment.can_approve = user.has_group('payment_approval_workflow.group_payment_approver')
                payment.can_reject = user.has_group('payment_approval_workflow.group_payment_approver')
                
            elif payment.approval_state == 'approved':
                # For outbound payments, need authorization
                if payment.payment_type == 'outbound':
                    payment.can_authorize = user.has_group('payment_approval_workflow.group_payment_authorizer')
                    payment.can_reject = user.has_group('payment_approval_workflow.group_payment_authorizer')

    def _check_write_access(self):
        """Check if current user has write access"""
        try:
            self.check_access_rights('write')
            self.check_access_rule('write')
            return True
        except AccessError:
            return False

    def _generate_qr_code(self):
        """Generate QR code image for payment verification"""
        if not self.verification_token:
            return False
            
        try:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            verification_url = f"{base_url}/payment/verify/{self.verification_token}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(verification_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue())
            
            return qr_code_data
            
        except Exception as e:
            _logger.error("Error generating QR code: %s", str(e))
            return False

    def _generate_verification_token(self):
        """Generate unique verification token"""
        return str(uuid.uuid4())

    # Workflow Actions
    def action_submit_for_review(self):
        """Submit payment for review"""
        for payment in self:
            if payment.approval_state != 'draft':
                raise UserError(_("Only draft payments can be submitted for review."))
            
            if not payment.verification_token:
                payment.verification_token = payment._generate_verification_token()
            
            payment.write({
                'approval_state': 'submitted',
                'submitted_by_id': self.env.user.id,
                'submission_date': fields.Datetime.now(),
            })
            
            # Send notification to reviewers
            payment._send_notification_email('submitted')
            
            # Log activity
            payment.message_post(
                body=_("Payment submitted for review by %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note'
            )

    def action_review(self):
        """Open signature wizard for review"""
        self.ensure_one()
        if self.approval_state != 'submitted':
            raise UserError(_("Only submitted payments can be reviewed."))
        
        if not self.env.user.has_group('payment_approval_workflow.group_payment_reviewer'):
            raise AccessError(_("You don't have permission to review payments."))
        
        return {
            'name': _('Review Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'payment.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
                'default_action_type': 'review',
            }
        }

    def action_approve(self):
        """Open signature wizard for approval"""
        self.ensure_one()
        if self.approval_state != 'reviewed':
            raise UserError(_("Only reviewed payments can be approved."))
        
        if not self.env.user.has_group('payment_approval_workflow.group_payment_approver'):
            raise AccessError(_("You don't have permission to approve payments."))
        
        return {
            'name': _('Approve Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'payment.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
                'default_action_type': 'approve',
            }
        }

    def action_authorize(self):
        """Open signature wizard for authorization"""
        self.ensure_one()
        if self.approval_state != 'approved':
            raise UserError(_("Only approved payments can be authorized."))
        
        if self.payment_type != 'outbound':
            raise UserError(_("Only vendor payments require authorization."))
        
        if not self.env.user.has_group('payment_approval_workflow.group_payment_authorizer'):
            raise AccessError(_("You don't have permission to authorize payments."))
        
        return {
            'name': _('Authorize Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'payment.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
                'default_action_type': 'authorize',
            }
        }

    def action_reject(self):
        """Open rejection wizard"""
        self.ensure_one()
        if self.approval_state not in ['submitted', 'reviewed', 'approved']:
            raise UserError(_("Payment cannot be rejected in current state."))
        
        # Check permissions based on current state
        if self.approval_state == 'submitted' and not self.env.user.has_group('payment_approval_workflow.group_payment_reviewer'):
            raise AccessError(_("You don't have permission to reject payments at this stage."))
        elif self.approval_state == 'reviewed' and not self.env.user.has_group('payment_approval_workflow.group_payment_approver'):
            raise AccessError(_("You don't have permission to reject payments at this stage."))
        elif self.approval_state == 'approved' and not self.env.user.has_group('payment_approval_workflow.group_payment_authorizer'):
            raise AccessError(_("You don't have permission to reject payments at this stage."))
        
        return {
            'name': _('Reject Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'payment.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
            }
        }

    def action_post(self):
        """Override post action to handle approval workflow"""
        for payment in self:
            # Check if payment is in correct state for posting
            if payment.payment_type == 'outbound' and payment.approval_state != 'authorized':
                raise UserError(_("Vendor payments must be authorized before posting."))
            elif payment.payment_type == 'inbound' and payment.approval_state != 'approved':
                raise UserError(_("Customer payments must be approved before posting."))
        
        # Call parent method
        result = super().action_post()
        
        # Update approval state to posted
        for payment in self:
            payment.approval_state = 'posted'
            
            # Send final notification
            payment._send_notification_email('posted')
            
            # Log activity
            payment.message_post(
                body=_("Payment posted and processed successfully"),
                subtype_xmlid='mail.mt_note'
            )
        
        return result

    def confirm_review(self, signature_data):
        """Confirm review with signature"""
        self.ensure_one()
        self.write({
            'approval_state': 'reviewed',
            'reviewer_id': self.env.user.id,
            'review_date': fields.Datetime.now(),
            'review_signature': signature_data,
        })
        
        # Send notification to approvers
        self._send_notification_email('reviewed')
        
        # Log activity
        self.message_post(
            body=_("Payment reviewed and signed by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def confirm_approve(self, signature_data):
        """Confirm approval with signature"""
        self.ensure_one()
        self.write({
            'approval_state': 'approved',
            'approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now(),
            'approval_signature': signature_data,
        })
        
        # Send notification based on payment type
        if self.payment_type == 'outbound':
            # Vendor payment - send to authorizers
            self._send_notification_email('approved')
        else:
            # Customer payment - ready for posting
            self._send_notification_email('final_approved')
        
        # Log activity
        self.message_post(
            body=_("Payment approved and signed by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def confirm_authorize(self, signature_data):
        """Confirm authorization with signature"""
        self.ensure_one()
        self.write({
            'approval_state': 'authorized',
            'authorizer_id': self.env.user.id,
            'authorization_date': fields.Datetime.now(),
            'authorization_signature': signature_data,
        })
        
        # Send final notification
        self._send_notification_email('authorized')
        
        # Log activity
        self.message_post(
            body=_("Payment authorized and signed by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note'
        )

    def confirm_reject(self, rejection_reason):
        """Confirm rejection with reason"""
        self.ensure_one()
        self.write({
            'approval_state': 'rejected',
            'rejection_reason': rejection_reason,
        })
        
        # Send rejection notification
        self._send_notification_email('rejected')
        
        # Log activity
        self.message_post(
            body=_("Payment rejected by %s. Reason: %s") % (self.env.user.name, rejection_reason),
            subtype_xmlid='mail.mt_note'
        )

    def _send_notification_email(self, trigger):
        """Send automated email notifications"""
        self.ensure_one()
        
        template_mapping = {
            'submitted': 'payment_approval_workflow.email_template_payment_submitted',
            'reviewed': 'payment_approval_workflow.email_template_payment_reviewed',
            'approved': 'payment_approval_workflow.email_template_payment_approved',
            'authorized': 'payment_approval_workflow.email_template_payment_authorized',
            'final_approved': 'payment_approval_workflow.email_template_payment_final_approved',
            'posted': 'payment_approval_workflow.email_template_payment_posted',
            'rejected': 'payment_approval_workflow.email_template_payment_rejected',
        }
        
        template_id = template_mapping.get(trigger)
        if not template_id:
            return
        
        try:
            template = self.env.ref(template_id)
            if template:
                template.send_mail(self.id, force_send=True)
        except Exception as e:
            _logger.warning("Failed to send email notification for %s: %s", trigger, str(e))

    def action_reset_to_draft(self):
        """Reset payment to draft state (for testing/admin purposes)"""
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only system administrators can reset payments to draft."))
        
        for payment in self:
            payment.write({
                'approval_state': 'draft',
                'rejection_reason': False,
                'reviewer_id': False,
                'review_date': False,
                'review_signature': False,
                'approver_id': False,
                'approval_date': False,
                'approval_signature': False,
                'authorizer_id': False,
                'authorization_date': False,
                'authorization_signature': False,
                'submitted_by_id': False,
                'submission_date': False,
            })

    def action_view_journal_entry(self):
        """Smart button action to view journal entry"""
        self.ensure_one()
        if not self.move_id:
            raise UserError(_("No journal entry found for this payment."))
        
        return {
            'name': _('Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_qr_verification(self):
        """Smart button action to open QR verification URL"""
        self.ensure_one()
        if not self.verification_token:
            raise UserError(_("No verification token found for this payment."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.verification_url,
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        """Override create to set initial state"""
        vals['approval_state'] = 'draft'
        return super().create(vals)

    def write(self, vals):
        """Override write to handle state changes"""
        result = super().write(vals)
        
        # Auto-generate verification token when needed
        for payment in self:
            if payment.approval_state in ['submitted', 'reviewed', 'approved', 'authorized'] and not payment.verification_token:
                payment.verification_token = payment._generate_verification_token()
        
        return result

    @api.constrains('approval_state', 'payment_type')
    def _check_approval_state_consistency(self):
        """Validate approval state consistency"""
        for payment in self:
            if payment.payment_type == 'inbound' and payment.approval_state == 'authorized':
                raise ValidationError(_("Customer payments cannot be in 'Authorized' state. They go directly from 'Approved' to 'Posted'."))

    def unlink(self):
        """Prevent deletion of payments in approval process"""
        for payment in self:
            if payment.approval_state not in ['draft', 'rejected']:
                raise UserError(_("Cannot delete payments that are in the approval process."))
        return super().unlink()
