# -*- coding: utf-8 -*-
#############################################################################
#
#    Enhanced Payment Voucher System - OSUS
#    Copyright (C) 2024 OSUS Properties
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
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


class AccountPayment(models.Model):
    """Enhanced Payment with Digital Signatures, QR Codes, and Multi-stage Approval"""
    _inherit = "account.payment"
    _inherits = {'account.move': 'move_id'}
    
    # Enhanced Workflow States
    voucher_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Voucher Status', default='draft', tracking=True, copy=False,
       help="Enhanced workflow status for payment vouchers")
    
    # Voucher Information
    voucher_number = fields.Char(
        string='Voucher Number', 
        readonly=True, 
        copy=False,
        help="Auto-generated voucher number"
    )
    
    voucher_type = fields.Selection([
        ('payment', 'Payment Voucher'),
        ('receipt', 'Receipt Voucher')
    ], string='Voucher Type', compute='_compute_voucher_type', store=True)
    
    # Digital Signature Fields
    creator_signature = fields.Binary(string='Creator Signature', attachment=True)
    creator_signature_date = fields.Datetime(string='Creator Signature Date')
    creator_name = fields.Char(string='Creator Name', compute='_compute_creator_name', store=True)
    
    reviewer_signature = fields.Binary(string='Reviewer Signature', attachment=True)
    reviewer_signature_date = fields.Datetime(string='Reviewer Signature Date')
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    reviewer_name = fields.Char(string='Reviewer Name', related='reviewer_id.name', store=True)
    
    approver_signature = fields.Binary(string='Approver Signature', attachment=True)
    approver_signature_date = fields.Datetime(string='Approver Signature Date')
    approver_id = fields.Many2one('res.users', string='Approver')
    approver_name = fields.Char(string='Approver Name', related='approver_id.name', store=True)
    
    authorizer_signature = fields.Binary(string='Authorizer Signature', attachment=True)
    authorizer_signature_date = fields.Datetime(string='Authorizer Signature Date')
    authorizer_id = fields.Many2one('res.users', string='Authorizer')
    authorizer_name = fields.Char(string='Authorizer Name', related='authorizer_id.name', store=True)
    
    receiver_signature = fields.Binary(string='Receiver Signature', attachment=True)
    receiver_signature_date = fields.Datetime(string='Receiver Signature Date')
    
    # QR Code and Verification
    qr_code = fields.Binary(string='QR Code', attachment=True, compute='_compute_qr_code', store=True)
    verification_token = fields.Char(string='Verification Token', copy=False)
    verification_url = fields.Char(string='Verification URL', compute='_compute_verification_url')
    
    # Amount in Words
    amount_in_words = fields.Text(string='Amount in Words', compute='_compute_amount_in_words')
    
    # Related Document Information
    related_document_type = fields.Char(string='Related Document Type')
    related_document_number = fields.Char(string='Related Document Number')
    related_document_date = fields.Date(string='Related Document Date')
    
    # Workflow Tracking
    submitted_date = fields.Datetime(string='Submitted Date')
    reviewed_date = fields.Datetime(string='Reviewed Date')
    approved_date = fields.Datetime(string='Approved Date')
    authorized_date = fields.Datetime(string='Authorized Date')
    rejected_date = fields.Datetime(string='Rejected Date')
    rejection_reason = fields.Text(string='Rejection Reason')
    
    # Progress Tracking
    workflow_progress = fields.Float(string='Workflow Progress', compute='_compute_workflow_progress')
    next_action_user_ids = fields.Many2many('res.users', string='Next Action Users', compute='_compute_next_action_users')
    
    # Legacy Fields (for backward compatibility)
    is_approve_person = fields.Boolean(string='Is Approve Person', compute='_compute_is_approve_person')
    
    @api.depends('payment_type')
    def _compute_voucher_type(self):
        """Determine voucher type based on payment type"""
        for record in self:
            if record.payment_type == 'outbound':
                record.voucher_type = 'payment'
            else:
                record.voucher_type = 'receipt'
    
    @api.depends('create_uid')
    def _compute_creator_name(self):
        """Compute creator name from create_uid"""
        for record in self:
            record.creator_name = record.create_uid.name if record.create_uid else ''
    
    @api.depends('amount', 'currency_id')
    def _compute_amount_in_words(self):
        """Convert amount to words"""
        for record in self:
            if record.amount and record.currency_id:
                try:
                    # Get currency name
                    currency_name = record.currency_id.name or 'USD'
                    
                    # Convert amount to words
                    amount_words = num2words(record.amount, to='currency', currency=currency_name)
                    record.amount_in_words = amount_words.title()
                except Exception as e:
                    _logger.warning(f"Error converting amount to words: {e}")
                    record.amount_in_words = f"{record.currency_id.symbol} {record.amount:,.2f}"
            else:
                record.amount_in_words = ''
    
    @api.depends('verification_token')
    def _compute_verification_url(self):
        """Generate QR verification URL"""
        for record in self:
            if record.verification_token:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
                record.verification_url = f"{base_url}/payment/verify/{record.verification_token}"
            else:
                record.verification_url = ''
    
    @api.depends('verification_url')
    def _compute_qr_code(self):
        """Generate QR code for payment verification"""
        for record in self:
            if record.verification_url:
                try:
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(record.verification_url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    qr_code_data = base64.b64encode(buffer.getvalue())
                    record.qr_code = qr_code_data
                except Exception as e:
                    _logger.warning(f"Error generating QR code: {e}")
                    record.qr_code = False
            else:
                record.qr_code = False
    
    @api.depends('voucher_state', 'voucher_type')
    def _compute_workflow_progress(self):
        """Calculate workflow progress percentage"""
        for record in self:
            if record.voucher_type == 'payment':
                # Payment Voucher: 7 stages (Draft, Submitted, Review, Approved, Authorized, Posted)
                progress_map = {
                    'draft': 0,
                    'submitted': 16.67,
                    'under_review': 33.33,
                    'approved': 50.0,
                    'authorized': 66.67,
                    'posted': 100.0,
                    'rejected': 0,
                    'cancelled': 0
                }
            else:
                # Receipt Voucher: 4 stages (Draft, Submitted, Review, Posted)
                progress_map = {
                    'draft': 0,
                    'submitted': 25.0,
                    'under_review': 50.0,
                    'posted': 100.0,
                    'rejected': 0,
                    'cancelled': 0
                }
            record.workflow_progress = progress_map.get(record.voucher_state, 0)
    
    @api.depends('voucher_state', 'voucher_type')
    def _compute_next_action_users(self):
        """Determine who should take the next action"""
        for record in self:
            users = self.env['res.users']
            
            if record.voucher_state == 'submitted':
                # Need reviewer
                users = self.env.ref('account_payment_approval.group_payment_voucher_reviewer').users
            elif record.voucher_state == 'under_review' and record.voucher_type == 'payment':
                # Need approver for payment vouchers
                users = self.env.ref('account_payment_approval.group_payment_voucher_approver').users
            elif record.voucher_state == 'approved' and record.voucher_type == 'payment':
                # Need authorizer for payment vouchers
                users = self.env.ref('account_payment_approval.group_payment_voucher_authorizer').users
            elif record.voucher_state in ['under_review', 'authorized']:
                # Ready for posting
                users = self.env.ref('account_payment_approval.group_payment_voucher_manager').users
            
            record.next_action_user_ids = users
    
    def _compute_is_approve_person(self):
        """Legacy method for backward compatibility"""
        for record in self:
            # Check if user has any approval permissions
            user = self.env.user
            approval_groups = [
                'account_payment_approval.group_payment_voucher_reviewer',
                'account_payment_approval.group_payment_voucher_approver',
                'account_payment_approval.group_payment_voucher_authorizer',
                'account_payment_approval.group_payment_voucher_manager'
            ]
            
            record.is_approve_person = any(user.has_group(group) for group in approval_groups)
    
    @api.model
    def create(self, vals):
        """Override create to generate voucher number and verification token"""
        payment = super().create(vals)
        
        # Generate voucher number
        if not payment.voucher_number:
            if payment.voucher_type == 'payment':
                sequence = self.env.ref('account_payment_approval.sequence_payment_voucher')
            else:
                sequence = self.env.ref('account_payment_approval.sequence_receipt_voucher')
            payment.voucher_number = sequence.next_by_id()
        
        # Generate verification token
        if not payment.verification_token:
            payment.verification_token = str(uuid.uuid4())
        
        # Create QR verification record
        self.env['payment.voucher.qr.verification'].create({
            'payment_id': payment.id,
            'token': payment.verification_token,
            'is_active': True
        })
        
        return payment
    
    # Workflow Action Methods
    def action_submit_for_approval(self):
        """Submit payment for approval workflow"""
        self.ensure_one()
        
        if self.voucher_state != 'draft':
            raise UserError(_("Only draft vouchers can be submitted for approval."))
        
        # Validate required fields
        self._validate_submission()
        
        # Update state and dates
        self.write({
            'voucher_state': 'submitted',
            'submitted_date': fields.Datetime.now(),
        })
        
        # Create creator signature if not exists
        if not self.creator_signature_date:
            self._create_signature('creator')
        
        # Send notification
        self._send_notification('submitted')
        
        # Create activity for reviewers
        self._create_activity_for_next_users()
        
        self.message_post(
            body=_("Payment voucher submitted for approval by %s") % self.env.user.name,
            message_type='notification'
        )
    
    def action_review(self):
        """Review the payment voucher"""
        self.ensure_one()
        self._check_workflow_permission('review')
        
        if self.voucher_state != 'submitted':
            raise UserError(_("Only submitted vouchers can be reviewed."))
        
        self.write({
            'voucher_state': 'under_review',
            'reviewed_date': fields.Datetime.now(),
            'reviewer_id': self.env.user.id,
        })
        
        # Create reviewer signature
        self._create_signature('reviewer')
        
        # Send notification
        self._send_notification('reviewed')
        
        # Create next activity
        self._create_activity_for_next_users()
        
        self.message_post(
            body=_("Payment voucher reviewed by %s") % self.env.user.name,
            message_type='notification'
        )
    
    def action_approve(self):
        """Approve the payment voucher (only for payment vouchers)"""
        self.ensure_one()
        self._check_workflow_permission('approve')
        
        if self.voucher_type != 'payment':
            raise UserError(_("Only payment vouchers require approval step."))
        
        if self.voucher_state != 'under_review':
            raise UserError(_("Only vouchers under review can be approved."))
        
        self.write({
            'voucher_state': 'approved',
            'approved_date': fields.Datetime.now(),
            'approver_id': self.env.user.id,
        })
        
        # Create approver signature
        self._create_signature('approver')
        
        # Send notification
        self._send_notification('approved')
        
        # Create next activity
        self._create_activity_for_next_users()
        
        self.message_post(
            body=_("Payment voucher approved by %s") % self.env.user.name,
            message_type='notification'
        )
    
    def action_authorize(self):
        """Authorize the payment voucher (only for payment vouchers)"""
        self.ensure_one()
        self._check_workflow_permission('authorize')
        
        if self.voucher_type != 'payment':
            raise UserError(_("Only payment vouchers require authorization step."))
        
        if self.voucher_state != 'approved':
            raise UserError(_("Only approved vouchers can be authorized."))
        
        self.write({
            'voucher_state': 'authorized',
            'authorized_date': fields.Datetime.now(),
            'authorizer_id': self.env.user.id,
        })
        
        # Create authorizer signature
        self._create_signature('authorizer')
        
        # Send notification
        self._send_notification('authorized')
        
        # Create next activity
        self._create_activity_for_next_users()
        
        self.message_post(
            body=_("Payment voucher authorized by %s") % self.env.user.name,
            message_type='notification'
        )
    
    def action_post_payment(self):
        """Post the payment (final step)"""
        self.ensure_one()
        self._check_workflow_permission('post')
        
        # Check state requirements
        if self.voucher_type == 'payment' and self.voucher_state != 'authorized':
            raise UserError(_("Payment vouchers must be authorized before posting."))
        elif self.voucher_type == 'receipt' and self.voucher_state != 'under_review':
            raise UserError(_("Receipt vouchers must be reviewed before posting."))
        
        # Post the payment using standard Odoo method
        self.action_post()
        
        # Update voucher state
        self.write({
            'voucher_state': 'posted',
        })
        
        # Send final notification
        self._send_notification('posted')
        
        self.message_post(
            body=_("Payment voucher posted by %s") % self.env.user.name,
            message_type='notification'
        )
    
    def action_reject(self):
        """Reject the payment voucher"""
        self.ensure_one()
        self._check_workflow_permission('reject')
        
        # Get rejection reason
        ctx = self.env.context
        rejection_reason = ctx.get('rejection_reason', '')
        
        if not rejection_reason:
            raise UserError(_("Please provide a reason for rejection."))
        
        self.write({
            'voucher_state': 'rejected',
            'rejected_date': fields.Datetime.now(),
            'rejection_reason': rejection_reason,
        })
        
        # Send notification
        self._send_notification('rejected')
        
        self.message_post(
            body=_("Payment voucher rejected by %s. Reason: %s") % (self.env.user.name, rejection_reason),
            message_type='notification'
        )
    
    def action_reset_to_draft(self):
        """Reset voucher to draft state"""
        self.ensure_one()
        
        if not self.env.user.has_group('account_payment_approval.group_payment_voucher_manager'):
            raise AccessError(_("Only managers can reset vouchers to draft."))
        
        self.write({
            'voucher_state': 'draft',
            'submitted_date': False,
            'reviewed_date': False,
            'approved_date': False,
            'authorized_date': False,
            'rejected_date': False,
            'rejection_reason': False,
            'reviewer_id': False,
            'approver_id': False,
            'authorizer_id': False,
        })
        
        self.message_post(
            body=_("Payment voucher reset to draft by %s") % self.env.user.name,
            message_type='notification'
        )
    
    # Helper Methods
    def _validate_submission(self):
        """Validate required fields before submission"""
        self.ensure_one()
        
        if not self.partner_id:
            raise ValidationError(_("Partner is required for submission."))
        
        if not self.amount or self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))
        
        if not self.currency_id:
            raise ValidationError(_("Currency is required for submission."))
        
        if not self.payment_method_id:
            raise ValidationError(_("Payment method is required for submission."))
    
    def _check_workflow_permission(self, action):
        """Check if current user has permission for the workflow action"""
        self.ensure_one()
        user = self.env.user
        
        permission_map = {
            'review': 'account_payment_approval.group_payment_voucher_reviewer',
            'approve': 'account_payment_approval.group_payment_voucher_approver',
            'authorize': 'account_payment_approval.group_payment_voucher_authorizer',
            'post': 'account_payment_approval.group_payment_voucher_manager',
            'reject': 'account_payment_approval.group_payment_voucher_reviewer',  # Reviewers can reject
        }
        
        required_group = permission_map.get(action)
        if required_group and not user.has_group(required_group):
            raise AccessError(_("You don't have permission to %s this voucher.") % action)
    
    def _create_signature(self, signature_type):
        """Create a digital signature for the current user"""
        self.ensure_one()
        
        # Create signature record
        signature_vals = {
            'payment_id': self.id,
            'user_id': self.env.user.id,
            'signature_type': signature_type,
            'signature_date': fields.Datetime.now(),
            'ip_address': self.env.context.get('client_ip', ''),
            'user_agent': self.env.context.get('user_agent', ''),
        }
        
        self.env['payment.voucher.signature'].create(signature_vals)
        
        # Update payment fields
        field_map = {
            'creator': ('creator_signature_date',),
            'reviewer': ('reviewer_signature_date',),
            'approver': ('approver_signature_date',),
            'authorizer': ('authorizer_signature_date',),
            'receiver': ('receiver_signature_date',),
        }
        
        if signature_type in field_map:
            update_vals = {field_map[signature_type][0]: fields.Datetime.now()}
            self.write(update_vals)
    
    def _send_notification(self, action):
        """Send email notification for workflow action"""
        self.ensure_one()
        
        template_map = {
            'submitted': 'account_payment_approval.email_template_payment_submitted',
            'reviewed': 'account_payment_approval.email_template_payment_reviewed',
            'approved': 'account_payment_approval.email_template_payment_approved',
            'authorized': 'account_payment_approval.email_template_payment_authorized',
            'posted': 'account_payment_approval.email_template_payment_posted',
            'rejected': 'account_payment_approval.email_template_payment_rejected',
        }
        
        template_ref = template_map.get(action)
        if template_ref:
            try:
                template = self.env.ref(template_ref)
                template.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.warning(f"Failed to send email notification: {e}")
    
    def _create_activity_for_next_users(self):
        """Create activities for users who need to take the next action"""
        self.ensure_one()
        
        if not self.next_action_user_ids:
            return
        
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        
        action_messages = {
            'submitted': 'Review payment voucher',
            'under_review': 'Approve payment voucher' if self.voucher_type == 'payment' else 'Post receipt voucher',
            'approved': 'Authorize payment voucher',
            'authorized': 'Post payment voucher',
        }
        
        summary = action_messages.get(self.voucher_state, 'Process payment voucher')
        
        for user in self.next_action_user_ids:
            self.activity_schedule(
                activity_type_id=activity_type.id,
                summary=summary,
                note=f"Voucher {self.voucher_number} requires your attention.",
                user_id=user.id,
                date_deadline=fields.Date.today() + timedelta(days=3)
            )
    
    def get_voucher_verification_data(self):
        """Get voucher data for QR verification portal"""
        self.ensure_one()
        
        return {
            'voucher_number': self.voucher_number,
            'voucher_type': self.voucher_type,
            'partner_name': self.partner_id.name,
            'amount': self.amount,
            'currency': self.currency_id.name,
            'date': self.date.strftime('%B %d, %Y') if self.date else '',
            'state': self.voucher_state,
            'company': self.company_id.name,
            'is_posted': self.state == 'posted',
        }


class PaymentVoucherSignature(models.Model):
    """Digital Signature Model for Payment Vouchers"""
    _name = 'payment.voucher.signature'
    _description = 'Payment Voucher Digital Signature'
    _order = 'signature_date desc'
    
    payment_id = fields.Many2one('account.payment', string='Payment', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    signature_type = fields.Selection([
        ('creator', 'Creator'),
        ('reviewer', 'Reviewer'),
        ('approver', 'Approver'),
        ('authorizer', 'Authorizer'),
        ('receiver', 'Receiver')
    ], string='Signature Type', required=True)
    signature_date = fields.Datetime(string='Signature Date', required=True)
    signature_data = fields.Binary(string='Signature Image', attachment=True)
    ip_address = fields.Char(string='IP Address')
    user_agent = fields.Text(string='User Agent')
    company_id = fields.Many2one('res.company', string='Company', related='payment_id.company_id', store=True)


class PaymentVoucherQRVerification(models.Model):
    """QR Code Verification Model"""
    _name = 'payment.voucher.qr.verification'
    _description = 'Payment Voucher QR Verification'
    _rec_name = 'token'
    
    payment_id = fields.Many2one('account.payment', string='Payment', required=True, ondelete='cascade')
    token = fields.Char(string='Verification Token', required=True, index=True)
    is_active = fields.Boolean(string='Is Active', default=True)
    verification_count = fields.Integer(string='Verification Count', default=0)
    last_verified_date = fields.Datetime(string='Last Verified')
    last_verified_ip = fields.Char(string='Last Verified IP')
    
    @api.model
    def verify_token(self, token):
        """Verify a QR token and return payment data"""
        verification = self.search([('token', '=', token), ('is_active', '=', True)], limit=1)
        
        if not verification:
            return {'error': 'Invalid or expired verification token'}
        
        # Update verification stats
        verification.write({
            'verification_count': verification.verification_count + 1,
            'last_verified_date': fields.Datetime.now(),
            'last_verified_ip': self.env.context.get('client_ip', ''),
        })
        
        # Return payment data
        return {
            'success': True,
            'payment_data': verification.payment_id.get_voucher_verification_data()
        }

    def _compute_is_approve_person(self):
        """This function checks if the current user is authorized to approve payments.
        It supports both single approver and multiple approvers configuration.
        Multiple approvers take precedence over single approver if both are configured."""
        for record in self:
            approval = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval')
            
            if not approval:
                record.is_approve_person = False
                continue
                
            # Check for multiple approvers first (takes precedence)
            multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_user_ids', '')
            
            if multiple_approvers_param:
                try:
                    # Parse the comma-separated string of user IDs
                    approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                    if approver_ids:  # Only use if we actually have IDs
                        record.is_approve_person = self.env.user.id in approver_ids
                        continue
                except (ValueError, AttributeError):
                    # If parsing fails, fall back to single approver
                    pass
            
            # Fall back to single approver configuration
            single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_user_id', '')
            if single_approver_param:
                try:
                    approver_id = int(single_approver_param)
                    record.is_approve_person = self.env.user.id == approver_id
                except (ValueError, TypeError):
                    record.is_approve_person = False
            else:
                record.is_approve_person = False

    def _is_user_authorized_approver(self, user_id=None):
        """Helper method to check if a user is authorized to approve payments.
        Supports both single and multiple approver configurations.
        
        Args:
            user_id (int): User ID to check. If None, uses current user.
            
        Returns:
            bool: True if user is authorized to approve payments
        """
        if user_id is None:
            user_id = self.env.user.id
            
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        
        if not approval:
            return False
            
        # Check for multiple approvers first (takes precedence)
        multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids', '')
        
        if multiple_approvers_param:
            try:
                # Parse the comma-separated string of user IDs
                approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                if approver_ids:  # Only use if we actually have IDs
                    return user_id in approver_ids
            except (ValueError, AttributeError):
                # If parsing fails, fall back to single approver
                pass
        
        # Fall back to single approver configuration
        single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id', '')
        if single_approver_param:
            try:
                approver_id = int(single_approver_param)
                return user_id == approver_id
            except (ValueError, TypeError):
                return False
        
        return False

    def get_authorized_approvers(self):
        """Get list of authorized approvers for this payment"""
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        
        if not approval:
            return self.env['res.users']
            
        # Check for multiple approvers first
        multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids', '')
        
        if multiple_approvers_param:
            try:
                approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                if approver_ids:  # Only use if we actually have IDs
                    return self.env['res.users'].browse(approver_ids).exists()
            except (ValueError, AttributeError):
                pass
        
        # Fall back to single approver
        single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id', '')
        if single_approver_param:
            try:
                approver_id = int(single_approver_param)
                return self.env['res.users'].browse(approver_id).exists()
            except (ValueError, TypeError):
                pass
        
        return self.env['res.users']

    is_approve_person = fields.Boolean(string='Approving Person',
                                       compute=_compute_is_approve_person,
                                       readonly=True,
                                       help="Enable/disable if approving"
                                            " person")

    authorized_approvers_display = fields.Char(
        string='Authorized Approvers',
        compute='_compute_authorized_approvers_display',
        readonly=True,
        help="List of users authorized to approve this payment"
    )

    def _compute_authorized_approvers_display(self):
        """Compute display string for authorized approvers"""
        for record in self:
            approvers = record.get_authorized_approvers()
            if approvers:
                approver_names = approvers.mapped('name')
                record.authorized_approvers_display = ', '.join(approver_names)
            else:
                record.authorized_approvers_display = 'No approvers configured'

    is_locked = fields.Boolean(string='Locked', compute='_compute_is_locked', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    @api.depends('state')
    def _compute_is_locked(self):
        for rec in self:
            # Allow editing only in draft and rejected states
            # Approved payments should be locked for editing but allow posting
            rec.is_locked = rec.state not in ['draft', 'rejected']

    def write(self, vals):
        """Override write to add workflow validation"""
        if 'state' in vals:
            for record in self:
                # Validate state transitions
                if record.state == 'posted' and vals['state'] != 'cancel':
                    raise UserError(_("Posted payments can only be cancelled."))
                if record.state == 'waiting_approval' and vals['state'] not in ['approved', 'rejected', 'cancel']:
                    raise UserError(_("Payments waiting for approval can only be approved, rejected, or cancelled."))
                if record.state == 'approved' and vals['state'] not in ['posted', 'cancel']:
                    raise UserError(_("Approved payments can only be posted or cancelled."))
        return super(AccountPayment, self).write(vals)

    def action_post(self):
        """Overwrites the action_post() to validate the payment in the 'approved'
         stage too.
        currently Odoo allows payment posting only in draft stage."""
        
        # Handle multiple records by processing each one individually
        for payment in self:
            # Skip approval check if called from approve_transfer or if already approved
            if not self.env.context.get('skip_approval_check') and payment.state == 'draft':
                validation = payment._check_payment_approval()
                if not validation:
                    return False
                    
            # Allow posting from both draft and approved states
            if payment.state in ('posted', 'cancel', 'waiting_approval', 'rejected'):
                raise UserError(
                    _("Only a draft or approved payment can be posted."))
            if any(inv.state != 'posted' for inv in
                   payment.reconciled_invoice_ids):
                raise ValidationError(_("The payment cannot be processed "
                                        "because the invoice is not open!"))
        
        # Call the parent's action_post method to ensure proper sequence generation
        # and all standard Odoo posting logic
        return super(AccountPayment, self).action_post()

    def _check_payment_approval(self):
        """This function checks the payment approval if payment_amount grater
         than amount,then state changed to waiting_approval """
        self.ensure_one()
        if self.state == "draft":
            first_approval = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval')
            if first_approval:
                amount = float(self.env['ir.config_parameter'].sudo().get_param(
                    'account_payment_approval.approval_amount'))
                payment_currency_id = int(
                    self.env['ir.config_parameter'].sudo().get_param(
                        'account_payment_approval.approval_currency_id'))
                payment_amount = self.amount
                if payment_currency_id:
                    if (self.currency_id and
                            self.currency_id.id != payment_currency_id):
                        currency_id = self.env['res.currency'].browse(
                            payment_currency_id)
                        payment_amount = (self.currency_id._convert(
                            self.amount, currency_id, self.company_id,
                            self.date or fields.Date.today(), round=True))
                if payment_amount > amount:
                    self.write({
                        'state': 'waiting_approval'
                    })
                    return False
        return True

    def action_submit_review(self):
        """Submit the payment for review"""
        for record in self:
            if record.state == 'draft':
                record.state = 'waiting_approval'

    def approve_transfer(self):
        """This function changes state to approved state if approving person
         approves payment and automatically posts the payment"""
        for record in self:
            if record.state == 'waiting_approval' and record._is_user_authorized_approver():
                # First, set state to approved
                record.write({
                    'state': 'approved'
                })
                # Ensure the record is refreshed before posting
                record.invalidate_recordset()
                # Automatically post the payment after approval
                try:
                    # Post the payment directly from approved state
                    result = record.with_context(skip_approval_check=True).action_post()
                    return result
                except Exception as e:
                    # If posting fails, keep approved state and log the error
                    _logger.error(f"Failed to auto-post payment after approval: {str(e)}")
                    # Raise a user-friendly error but keep the approved state
                    raise UserError(f"Payment approved successfully but failed to post automatically: {str(e)}. You can manually post it from the approved state.")

    def reject_transfer(self):
        """Reject the payment transfer"""
        for record in self:
            if record.state == 'waiting_approval' and record._is_user_authorized_approver():
                record.state = 'rejected'
                # Allow draft and cancel actions after rejection
                record.is_locked = False

    def bulk_approve_payments(self):
        """Bulk approve multiple payments that are waiting for approval.
        This method overrides singleton constraint and allows bulk processing."""
        # Check if current user is an authorized approver
        if not self._is_user_authorized_approver():
            raise UserError(_("You are not authorized to approve payments."))
        
        # Filter payments that can be approved
        approvable_payments = self.filtered(lambda p: p.state == 'waiting_approval')
        
        if not approvable_payments:
            raise UserError(_("No payments found that are waiting for approval."))
        
        approved_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in approvable_payments:
            try:
                # Set state to approved first
                payment.write({'state': 'approved'})
                # Ensure the record is refreshed before posting
                payment.invalidate_recordset()
                # Automatically post the payment after approval
                payment.with_context(skip_approval_check=True).action_post()
                approved_count += 1
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                # Keep the payment in approved state even if posting fails
                _logger.error(f"Failed to post payment {payment.name} after bulk approval: {str(e)}")
        
        # Prepare result message
        if approved_count > 0:
            message = _("%d payment(s) have been approved and posted successfully.") % approved_count
            if failed_payments:
                message += _(" %d payment(s) were approved but failed to post automatically and can be posted manually.") % len(failed_payments)
            
            # Show notification to user
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Approval Complete'),
                    'message': message,
                    'type': 'success' if not failed_payments else 'warning',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be approved."))

    def bulk_reject_payments(self):
        """Bulk reject multiple payments that are waiting for approval.
        This method overrides singleton constraint and allows bulk processing."""
        # Check if current user is an authorized approver
        if not self._is_user_authorized_approver():
            raise UserError(_("You are not authorized to reject payments."))
        
        # Filter payments that can be rejected
        rejectable_payments = self.filtered(lambda p: p.state == 'waiting_approval')
        
        if not rejectable_payments:
            raise UserError(_("No payments found that are waiting for approval."))
        
        rejected_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in rejectable_payments:
            try:
                # Set state to rejected and unlock
                payment.write({
                    'state': 'rejected',
                    'is_locked': False
                })
                rejected_count += 1
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                _logger.error(f"Failed to reject payment {payment.name}: {str(e)}")
        
        # Prepare result message
        if rejected_count > 0:
            message = _("%d payment(s) have been rejected successfully.") % rejected_count
            if failed_payments:
                message += _(" %d payment(s) failed to be rejected.") % len(failed_payments)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Rejection Complete'),
                    'message': message,
                    'type': 'success' if not failed_payments else 'warning',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be rejected."))

    def bulk_draft_payments(self):
        """Bulk set multiple payments back to draft state.
        This method allows resetting rejected or cancelled payments to draft."""
        # Filter payments that can be set to draft
        draftable_payments = self.filtered(lambda p: p.state in ['rejected', 'cancel'])
        
        if not draftable_payments:
            raise UserError(_("No payments found that can be set to draft state. Only rejected or cancelled payments can be reset to draft."))
        
        drafted_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in draftable_payments:
            try:
                # Set state to draft and unlock
                payment.write({
                    'state': 'draft',
                    'is_locked': False
                })
                drafted_count += 1
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                _logger.error(f"Failed to set payment {payment.name} to draft: {str(e)}")
        
        # Prepare result message
        if drafted_count > 0:
            message = _("%d payment(s) have been set to draft successfully.") % drafted_count
            if failed_payments:
                message += _(" %d payment(s) failed to be set to draft.") % len(failed_payments)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Draft Complete'),
                    'message': message,
                    'type': 'success' if not failed_payments else 'warning',
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be set to draft."))

    def bulk_submit_for_approval(self):
        """Bulk submit multiple payments for approval.
        This method submits draft payments that exceed the approval amount threshold."""
        
        # Filter payments that can be submitted for approval (draft state)
        submittable_payments = self.filtered(lambda p: p.state == 'draft')
        
        if not submittable_payments:
            raise UserError(_("No draft payments found that can be submitted for approval."))
        
        submitted_count = 0
        skipped_count = 0
        failed_payments = []
        
        # Process each payment individually to handle any errors gracefully
        for payment in submittable_payments:
            try:
                # Check if this payment needs approval based on amount threshold
                # _check_payment_approval returns False when approval is needed and sets state to waiting_approval
                approval_result = payment._check_payment_approval()
                
                if not approval_result:
                    # Payment was automatically set to waiting_approval by _check_payment_approval
                    submitted_count += 1
                else:
                    # Payment doesn't need approval (amount below threshold)
                    skipped_count += 1
                    
            except Exception as e:
                failed_payments.append({
                    'payment': payment,
                    'error': str(e)
                })
                _logger.error(f"Failed to submit payment {payment.name} for approval: {str(e)}")
        
        # Prepare result message
        message_parts = []
        notification_type = 'success'
        
        if submitted_count > 0:
            message_parts.append(_("%d payment(s) have been submitted for approval successfully.") % submitted_count)
        
        if skipped_count > 0:
            message_parts.append(_("%d payment(s) were skipped as they don't require approval (amount below threshold).") % skipped_count)
            notification_type = 'info'
        
        if failed_payments:
            message_parts.append(_("%d payment(s) failed to be submitted for approval.") % len(failed_payments))
            notification_type = 'warning'
        
        if submitted_count > 0 or skipped_count > 0:
            message = ' '.join(message_parts)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Bulk Submit Complete'),
                    'message': message,
                    'type': notification_type,
                    'sticky': False,
                }
            }
        else:
            raise UserError(_("No payments could be submitted for approval."))

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountPayment, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and self:
            # Ensure we have a single record for state access
            self.ensure_one()
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                # Allow editing only in draft and rejected states
                node.set('edit', "0" if self.state not in ['draft', 'rejected'] else "1")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
