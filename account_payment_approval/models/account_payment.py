# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Payment Workflow - Single Status Bar
#    Consolidates standard Odoo payment workflow with enhanced voucher workflow
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
    """Unified Payment with single workflow status"""
    _inherit = "account.payment"
    
    # Extend the standard state field to include our enhanced states
    state = fields.Selection(
        selection_add=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('authorized', 'Authorized'),
            ('rejected', 'Rejected'),
        ],
        ondelete={
            'submitted': 'set default',
            'under_review': 'set default', 
            'approved': 'set default',
            'authorized': 'set default',
            'rejected': 'set default'
        },
        help="Status of the payment voucher in the approval workflow"
    )
    
    # Remove the separate voucher_state field since we're using the unified state
    # voucher_state = fields.Selection(...)  # Remove this
    
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
    ], string='Voucher Type', compute='_compute_voucher_type', store=True)
    
    # Approval Configuration
    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
        store=True,
        help="Whether this payment requires approval workflow"
    )
    
    approval_stage = fields.Selection([
        ('none', 'No Approval Required'),
        ('review', 'Needs Review'),
        ('approve', 'Needs Approval'),
        ('authorize', 'Needs Authorization'),
        ('complete', 'Approval Complete')
    ], string='Approval Stage', compute='_compute_approval_stage', store=True)
    
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
    
    # Smart button fields
    signature_count = fields.Integer(string='Signature Count', compute='_compute_signature_count')
    verification_count = fields.Integer(string='Verification Count', compute='_compute_verification_count')
    
    # Permission fields
    is_approve_person = fields.Boolean(string='Can Approve', compute='_compute_is_approve_person')
    authorized_approvers_display = fields.Text(string='Authorized Approvers', compute='_compute_authorized_approvers_display')
    
    @api.depends('payment_type')
    def _compute_voucher_type(self):
        """Determine voucher type based on payment type"""
        for record in self:
            if record.payment_type == 'outbound':
                record.voucher_type = 'payment'
            else:
                record.voucher_type = 'receipt'
    
    @api.depends('amount', 'currency_id')
    def _compute_requires_approval(self):
        """Determine if payment requires approval based on amount and configuration"""
        for record in self:
            # Check if approval is enabled
            approval_enabled = self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.payment_approval', False)
            
            if not approval_enabled:
                record.requires_approval = False
                continue
            
            # Get approval amount threshold
            approval_amount = float(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_amount', 0))
            
            # Get approval currency
            approval_currency_id = int(self.env['ir.config_parameter'].sudo().get_param(
                'account_payment_approval.approval_currency_id', 0))
            
            if not approval_amount:
                # If approval amount is 0, all payments require approval
                record.requires_approval = True
                continue
            
            # Convert payment amount to approval currency if needed
            payment_amount = record.amount
            if approval_currency_id and record.currency_id and record.currency_id.id != approval_currency_id:
                approval_currency = self.env['res.currency'].browse(approval_currency_id)
                payment_amount = record.currency_id._convert(
                    record.amount, approval_currency, record.company_id,
                    record.date or fields.Date.today())
            
            record.requires_approval = payment_amount > approval_amount
    
    @api.depends('state', 'voucher_type', 'requires_approval')
    def _compute_approval_stage(self):
        """Compute current approval stage"""
        for record in self:
            if not record.requires_approval:
                record.approval_stage = 'none'
            elif record.state == 'draft':
                record.approval_stage = 'review'
            elif record.state == 'submitted':
                record.approval_stage = 'review'
            elif record.state == 'under_review':
                if record.voucher_type == 'payment':
                    record.approval_stage = 'approve'
                else:
                    record.approval_stage = 'authorize'
            elif record.state == 'approved':
                record.approval_stage = 'authorize'
            elif record.state in ['authorized', 'posted', 'reconciled']:
                record.approval_stage = 'complete'
            else:
                record.approval_stage = 'none'
    
    @api.depends('state', 'voucher_type')
    def _compute_workflow_progress(self):
        """Calculate workflow progress percentage"""
        for record in self:
            if record.voucher_type == 'payment':
                # Payment Voucher: Draft → Submitted → Under Review → Approved → Authorized → Posted
                progress_map = {
                    'draft': 0,
                    'submitted': 16.67,
                    'under_review': 33.33,
                    'approved': 50.0,
                    'authorized': 83.33,
                    'posted': 100.0,
                    'reconciled': 100.0,
                    'rejected': 0,
                    'cancelled': 0
                }
            else:
                # Receipt Voucher: Draft → Submitted → Under Review → Posted
                progress_map = {
                    'draft': 0,
                    'submitted': 25.0,
                    'under_review': 50.0,
                    'posted': 100.0,
                    'reconciled': 100.0,
                    'rejected': 0,
                    'cancelled': 0
                }
            record.workflow_progress = progress_map.get(record.state, 0)
    
    @api.depends('state', 'voucher_type')
    def _compute_next_action_users(self):
        """Determine who should take the next action"""
        for record in self:
            users = self.env['res.users']
            
            if record.state == 'submitted':
                # Need reviewer
                try:
                    users = self.env.ref('account_payment_approval.group_payment_voucher_reviewer').users
                except:
                    users = self.env['res.users']
            elif record.state == 'under_review' and record.voucher_type == 'payment':
                # Need approver for payment vouchers
                try:
                    users = self.env.ref('account_payment_approval.group_payment_voucher_approver').users
                except:
                    users = self.env['res.users']
            elif record.state == 'approved' and record.voucher_type == 'payment':
                # Need authorizer for payment vouchers
                try:
                    users = self.env.ref('account_payment_approval.group_payment_voucher_authorizer').users
                except:
                    users = self.env['res.users']
            elif record.state in ['under_review', 'authorized']:
                # Ready for posting
                try:
                    users = self.env.ref('account_payment_approval.group_payment_voucher_manager').users
                except:
                    users = self.env['res.users']
            
            record.next_action_user_ids = users
    
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
                    currency_name = record.currency_id.name or 'USD'
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
    
    @api.depends('state')
    def _compute_signature_count(self):
        """Compute number of digital signatures"""
        for record in self:
            try:
                signatures = self.env['payment.voucher.signature'].search_count([
                    ('payment_id', '=', record.id)
                ])
                record.signature_count = signatures
            except:
                record.signature_count = 0
    
    @api.depends('verification_token')
    def _compute_verification_count(self):
        """Compute number of verifications performed"""
        for record in self:
            if record.verification_token:
                try:
                    verification = self.env['payment.voucher.qr.verification'].search([
                        ('payment_id', '=', record.id)
                    ], limit=1)
                    record.verification_count = verification.verification_count if verification else 0
                except:
                    record.verification_count = 0
            else:
                record.verification_count = 0
    
    @api.depends('state')
    def _compute_is_approve_person(self):
        """Compute if current user can approve this payment"""
        for record in self:
            user = self.env.user
            
            # Check if user has approver group
            is_approver = user.has_group('account_payment_approval.group_payment_voucher_approver')
            is_authorizer = user.has_group('account_payment_approval.group_payment_voucher_authorizer')
            is_manager = user.has_group('account_payment_approval.group_payment_voucher_manager')
            
            # Logic based on state and voucher type
            if record.state == 'under_review' and record.voucher_type == 'payment':
                record.is_approve_person = is_approver or is_manager
            elif record.state == 'under_review' and record.voucher_type == 'receipt':
                record.is_approve_person = is_authorizer or is_manager
            elif record.state == 'approved':
                record.is_approve_person = is_authorizer or is_manager
            else:
                record.is_approve_person = False
    
    @api.depends('state', 'voucher_type')
    def _compute_authorized_approvers_display(self):
        """Compute display text for authorized approvers"""
        for record in self:
            approvers = []
            
            # Get approver groups based on state and voucher type
            if record.state == 'under_review' and record.voucher_type == 'payment':
                # Payment vouchers need approval
                approver_group = self.env.ref('account_payment_approval.group_payment_voucher_approver', raise_if_not_found=False)
                if approver_group:
                    approvers.extend([user.name for user in approver_group.users])
                    
            elif record.state == 'under_review' and record.voucher_type == 'receipt':
                # Receipt vouchers skip to authorization
                authorizer_group = self.env.ref('account_payment_approval.group_payment_voucher_authorizer', raise_if_not_found=False)
                if authorizer_group:
                    approvers.extend([user.name for user in authorizer_group.users])
                    
            elif record.state == 'approved':
                # Need authorization
                authorizer_group = self.env.ref('account_payment_approval.group_payment_voucher_authorizer', raise_if_not_found=False)
                if authorizer_group:
                    approvers.extend([user.name for user in authorizer_group.users])
            
            # Always include managers
            manager_group = self.env.ref('account_payment_approval.group_payment_voucher_manager', raise_if_not_found=False)
            if manager_group:
                approvers.extend([user.name for user in manager_group.users])
            
            # Remove duplicates and format
            unique_approvers = list(set(approvers))
            if unique_approvers:
                record.authorized_approvers_display = ', '.join(unique_approvers)
            else:
                record.authorized_approvers_display = 'No authorized approvers found'
    
    @api.model
    def create(self, vals):
        """Override create to generate voucher number and verification token"""
        payment = super().create(vals)
        
        # Generate voucher number
        if not payment.voucher_number:
            if payment.voucher_type == 'payment':
                try:
                    sequence = self.env.ref('account_payment_approval.sequence_payment_voucher')
                    payment.voucher_number = sequence.next_by_id()
                except:
                    payment.voucher_number = self.env['ir.sequence'].next_by_code('payment.voucher') or '/'
            else:
                try:
                    sequence = self.env.ref('account_payment_approval.sequence_receipt_voucher')
                    payment.voucher_number = sequence.next_by_id()
                except:
                    payment.voucher_number = self.env['ir.sequence'].next_by_code('receipt.voucher') or '/'
        
        # Generate verification token
        if not payment.verification_token:
            payment.verification_token = str(uuid.uuid4())
        
        # Create QR verification record
        try:
            self.env['payment.voucher.qr.verification'].create({
                'payment_id': payment.id,
                'token': payment.verification_token,
                'is_active': True
            })
        except:
            _logger.warning("Could not create QR verification record")
        
        return payment
    
    # Workflow Action Methods
    def action_submit_for_approval(self):
        """Submit payment for approval workflow"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft vouchers can be submitted for approval."))
            
            # Check if approval is required
            if not record.requires_approval:
                # Skip approval workflow and go directly to posted
                record.action_post()
                return
            
            # Validate required fields
            record._validate_submission()
            
            # Update state
            record.write({
                'state': 'submitted',
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
    
    def action_review(self):
        """Review the payment voucher"""
        for record in self:
            record._check_workflow_permission('review')
            
            if record.state != 'submitted':
                raise UserError(_("Only submitted vouchers can be reviewed."))
            
            record.write({
                'state': 'under_review',
                'reviewed_date': fields.Datetime.now(),
                'reviewer_id': self.env.user.id,
            })
            
            # Create reviewer signature
            record._create_signature('reviewer')
            
            # Send notification
            record._send_notification('reviewed')
            
            # Create next activity
            record._create_activity_for_next_users()
            
            record.message_post(
                body=_("Payment voucher reviewed by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_approve(self):
        """Approve the payment voucher (only for payment vouchers)"""
        for record in self:
            record._check_workflow_permission('approve')
            
            if record.voucher_type != 'payment':
                raise UserError(_("Only payment vouchers require approval step."))
            
            if record.state != 'under_review':
                raise UserError(_("Only vouchers under review can be approved."))
            
            record.write({
                'state': 'approved',
                'approved_date': fields.Datetime.now(),
                'approver_id': self.env.user.id,
            })
            
            # Create approver signature
            record._create_signature('approver')
            
            # Send notification
            record._send_notification('approved')
            
            # Create next activity
            record._create_activity_for_next_users()
            
            record.message_post(
                body=_("Payment voucher approved by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_authorize(self):
        """Authorize the payment voucher"""
        for record in self:
            record._check_workflow_permission('authorize')
            
            expected_state = 'approved' if record.voucher_type == 'payment' else 'under_review'
            if record.state != expected_state:
                raise UserError(_("Voucher is not in the correct state for authorization."))
            
            record.write({
                'state': 'authorized',
                'authorized_date': fields.Datetime.now(),
                'authorizer_id': self.env.user.id,
            })
            
            # Create authorizer signature
            record._create_signature('authorizer')
            
            # Send notification
            record._send_notification('authorized')
            
            # Create next activity
            record._create_activity_for_next_users()
            
            record.message_post(
                body=_("Payment voucher authorized by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_post(self):
        """Override action_post to handle approval workflow"""
        for record in self:
            # Check if approval is required and completed
            if record.requires_approval:
                if record.voucher_type == 'payment' and record.state != 'authorized':
                    raise UserError(_("Payment vouchers must be authorized before posting."))
                elif record.voucher_type == 'receipt' and record.state not in ['authorized', 'under_review']:
                    raise UserError(_("Receipt vouchers must be authorized or reviewed before posting."))
            
            # Call parent method to post the payment
            super(AccountPaymentUnified, record).action_post()
            
            # Update state to posted (this might be redundant with parent call)
            if record.state != 'posted':
                record.state = 'posted'
            
            # Send final notification
            record._send_notification('posted')
            
            record.message_post(
                body=_("Payment voucher posted by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_reject(self):
        """Reject the payment voucher"""
        for record in self:
            record._check_workflow_permission('reject')
            
            # Get rejection reason from context
            rejection_reason = self.env.context.get('rejection_reason', '')
            
            if not rejection_reason:
                # Open wizard to get rejection reason
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Reject Payment',
                    'res_model': 'payment.rejection.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_payment_id': record.id}
                }
            
            record.write({
                'state': 'rejected',
                'rejected_date': fields.Datetime.now(),
                'rejection_reason': rejection_reason,
            })
            
            # Send notification
            record._send_notification('rejected')
            
            record.message_post(
                body=_("Payment voucher rejected by %s. Reason: %s") % (self.env.user.name, rejection_reason),
                message_type='notification'
            )
    
    def action_reset_to_draft(self):
        """Reset voucher to draft state"""
        for record in self:
            if not self.env.user.has_group('account_payment_approval.group_payment_voucher_manager'):
                raise AccessError(_("Only managers can reset vouchers to draft."))
            
            record.write({
                'state': 'draft',
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
            
            record.message_post(
                body=_("Payment voucher reset to draft by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_print_multiple_reports(self):
        """Print multiple reports for the payment voucher"""
        self.ensure_one()
        
        if self.state == 'draft':
            raise UserError(_("Cannot print reports for draft vouchers."))
        
        # Get the appropriate report based on voucher type
        if self.voucher_type == 'payment':
            report_action = self.env.ref('account_payment_approval.action_report_payment_voucher')
        else:
            report_action = self.env.ref('account_payment_approval.action_report_receipt_voucher')
        
        # Return the report action
        return report_action.report_action(self)
    
    def action_cancel(self):
        """Cancel the payment voucher"""
        for record in self:
            if record.state in ['posted', 'reconciled']:
                raise UserError(_("Cannot cancel posted or reconciled vouchers."))
            
            record.write({'state': 'cancelled'})
            record.message_post(
                body=_("Payment voucher cancelled by %s") % self.env.user.name,
                message_type='notification'
            )
    
    def action_draft(self):
        """Set voucher back to draft"""
        return self.action_reset_to_draft()
    
    def action_view_signatures(self):
        """View digital signatures"""
        self.ensure_one()
        signatures = []
        
        if self.submitter_signature:
            signatures.append({
                'role': 'Submitter',
                'user': self.create_uid.name,
                'date': self.submitted_date,
                'signature': self.submitter_signature
            })
        
        if self.reviewer_signature:
            signatures.append({
                'role': 'Reviewer',
                'user': self.reviewer_id.name,
                'date': self.reviewed_date,
                'signature': self.reviewer_signature
            })
            
        if self.approver_signature:
            signatures.append({
                'role': 'Approver', 
                'user': self.approver_id.name,
                'date': self.approved_date,
                'signature': self.approver_signature
            })
            
        if self.authorizer_signature:
            signatures.append({
                'role': 'Authorizer',
                'user': self.authorizer_id.name, 
                'date': self.authorized_date,
                'signature': self.authorizer_signature
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Digital Signatures'),
                'message': _('Signatures found: %s') % len(signatures),
                'type': 'info',
            }
        }
    
    def action_view_verifications(self):
        """View QR verifications"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/payment/verify/{self.verification_token}',
            'target': 'new',
        }
    
    def action_view_workflow_history(self):
        """View workflow history"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Workflow History'),
            'res_model': 'mail.message',
            'view_mode': 'tree,form',
            'domain': [('res_id', '=', self.id), ('model', '=', 'account.payment')],
            'context': {'default_res_id': self.id, 'default_model': 'account.payment'},
        }
    
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
    
    # Permission and validation methods
    def _check_workflow_permission(self, action):
        """Check if current user has permission for the workflow action"""
        user = self.env.user
        
        permission_map = {
            'review': 'account_payment_approval.group_payment_voucher_reviewer',
            'approve': 'account_payment_approval.group_payment_voucher_approver',
            'authorize': 'account_payment_approval.group_payment_voucher_authorizer',
            'post': 'account_payment_approval.group_payment_voucher_manager',
            'reject': 'account_payment_approval.group_payment_voucher_reviewer',
        }
        
        required_group = permission_map.get(action)
        if required_group:
            try:
                if not user.has_group(required_group):
                    raise AccessError(_("You don't have permission to %s this voucher.") % action)
            except:
                # If group doesn't exist, allow the action
                pass
    
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
    
    def _create_signature(self, signature_type):
        """Create a digital signature for the current user"""
        self.ensure_one()
        
        try:
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
                'creator': 'creator_signature_date',
                'reviewer': 'reviewer_signature_date',
                'approver': 'approver_signature_date',
                'authorizer': 'authorizer_signature_date',
                'receiver': 'receiver_signature_date',
            }
            
            if signature_type in field_map:
                self.write({field_map[signature_type]: fields.Datetime.now()})
        except Exception as e:
            _logger.warning(f"Failed to create signature: {e}")
    
    def _send_notification(self, action):
        """Send email notification for workflow action"""
        try:
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
                template = self.env.ref(template_ref)
                template.send_mail(self.id, force_send=True)
        except Exception as e:
            _logger.warning(f"Failed to send email notification: {e}")
    
    def _create_activity_for_next_users(self):
        """Create activities for users who need to take the next action"""
        self.ensure_one()
        
        if not self.next_action_user_ids:
            return
        
        try:
            activity_type = self.env.ref('mail.mail_activity_data_todo')
            
            action_messages = {
                'submitted': 'Review payment voucher',
                'under_review': 'Approve payment voucher' if self.voucher_type == 'payment' else 'Authorize payment voucher',
                'approved': 'Authorize payment voucher',
                'authorized': 'Post payment voucher',
            }
            
            summary = action_messages.get(self.state, 'Process payment voucher')
            
            for user in self.next_action_user_ids:
                self.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=summary,
                    note=f"Voucher {self.voucher_number or self.name} requires your attention.",
                    user_id=user.id,
                    date_deadline=fields.Date.today() + timedelta(days=3)
                )
        except Exception as e:
            _logger.warning(f"Failed to create activity: {e}")