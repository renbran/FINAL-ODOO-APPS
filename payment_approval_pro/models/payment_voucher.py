# -*- coding: utf-8 -*-
"""
Payment Voucher Model - Core payment approval system
Clean, focused, and maintainable implementation for Odoo 17
"""

import base64
import io
import qrcode
import secrets
from datetime import datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo.tools import float_compare, format_amount
import logging

_logger = logging.getLogger(__name__)


class PaymentVoucher(models.Model):
    """
    Payment Voucher with Multi-Stage Approval Workflow
    
    This model manages payment vouchers with a clean 4-stage approval process:
    Draft → Review → Approve → Authorize → Paid
    
    Features:
    - QR code generation for verification
    - Role-based approval workflow
    - Professional reporting
    - Audit trail with mail.thread
    - Integration with standard Odoo payments
    """
    _name = 'payment.voucher'
    _description = 'Payment Voucher with Approval Workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'voucher_number desc, payment_date desc'
    _rec_name = 'voucher_number'

    # ================================
    # CORE FIELDS
    # ================================
    
    voucher_number = fields.Char(
        string='Voucher Number',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        help="Unique voucher number generated automatically"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor/Payee',
        required=True,
        tracking=True,
        domain=[('supplier_rank', '>', 0)],
        help="The vendor or person to be paid"
    )
    
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help="Total payment amount"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
        help="Payment currency"
    )
    
    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help="Scheduled payment date"
    )
    
    reference = fields.Char(
        string='Payment Reference',
        help="External reference or invoice number"
    )
    
    memo = fields.Text(
        string='Memo',
        help="Internal notes and payment description"
    )
    
    # ================================
    # WORKFLOW FIELDS
    # ================================
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approve', 'Approved'),
        ('authorize', 'Authorized'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True,
        help="Current approval status of the payment voucher")
    
    # ================================
    # APPROVAL TRACKING
    # ================================
    
    creator_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
        help="User who created this voucher"
    )
    
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewer',
        readonly=True,
        help="User assigned to review this voucher"
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        readonly=True,
        help="User who approved this voucher"
    )
    
    authorizer_id = fields.Many2one(
        'res.users',
        string='Authorizer',
        readonly=True,
        help="User who authorized the payment"
    )
    
    # ================================
    # DATES TRACKING
    # ================================
    
    create_date = fields.Datetime(
        string='Creation Date',
        readonly=True,
        help="When the voucher was created"
    )
    
    review_date = fields.Datetime(
        string='Review Date',
        readonly=True,
        help="When the voucher was submitted for review"
    )
    
    approval_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        help="When the voucher was approved"
    )
    
    authorization_date = fields.Datetime(
        string='Authorization Date',
        readonly=True,
        help="When the payment was authorized"
    )
    
    payment_posted_date = fields.Datetime(
        string='Payment Posted Date',
        readonly=True,
        help="When the actual payment was posted"
    )
    
    # ================================
    # QR CODE & VERIFICATION
    # ================================
    
    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        store=True,
        help="QR code for voucher verification"
    )
    
    verification_token = fields.Char(
        string='Verification Token',
        readonly=True,
        help="Unique token for QR verification"
    )
    
    qr_verification_url = fields.Char(
        string='Verification URL',
        compute='_compute_qr_verification_url',
        help="Public URL for QR verification"
    )
    
    # ================================
    # INTEGRATION FIELDS
    # ================================
    
    payment_id = fields.Many2one(
        'account.payment',
        string='Related Payment',
        readonly=True,
        help="Standard Odoo payment created when authorized"
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        domain=[('type', 'in', ('bank', 'cash'))],
        help="Journal for payment posting"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    amount_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_words',
        help="Amount written in words for reports"
    )
    
    can_review = fields.Boolean(
        string='Can Review',
        compute='_compute_user_permissions',
        help="Current user can review this voucher"
    )
    
    can_approve = fields.Boolean(
        string='Can Approve',
        compute='_compute_user_permissions',
        help="Current user can approve this voucher"
    )
    
    can_authorize = fields.Boolean(
        string='Can Authorize',
        compute='_compute_user_permissions',
        help="Current user can authorize this voucher"
    )
    
    is_readonly = fields.Boolean(
        string='Is Readonly',
        compute='_compute_is_readonly',
        help="Determines if voucher is in readonly state"
    )

    # ================================
    # CONSTRAINT METHODS
    # ================================
    
    @api.constrains('amount')
    def _check_amount(self):
        """Validate payment amount is positive"""
        for record in self:
            if float_compare(record.amount, 0.0, precision_rounding=record.currency_id.rounding) <= 0:
                raise ValidationError(_("Payment amount must be greater than zero."))
    
    @api.constrains('payment_date')
    def _check_payment_date(self):
        """Validate payment date is not in the past"""
        for record in self:
            if record.payment_date and record.payment_date < date.today():
                if record.state in ('draft', 'review'):
                    raise ValidationError(_("Payment date cannot be in the past."))
    
    # ================================
    # COMPUTED METHODS
    # ================================
    
    @api.depends('voucher_number', 'partner_id', 'amount', 'currency_id')
    def _compute_display_name(self):
        """Generate display name for voucher"""
        for record in self:
            if record.voucher_number and record.voucher_number != _('New'):
                partner_name = record.partner_id.name or _('Unknown')
                amount_str = format_amount(record.env, record.amount, record.currency_id)
                record.display_name = f"{record.voucher_number} - {partner_name} - {amount_str}"
            else:
                record.display_name = _('New Payment Voucher')
    
    @api.depends('amount', 'currency_id')
    def _compute_amount_words(self):
        """Convert amount to words for reports"""
        for record in self:
            try:
                # Use Odoo's built-in amount to words conversion
                record.amount_words = record.currency_id.amount_to_text(record.amount)
            except Exception:
                record.amount_words = f"{record.amount} {record.currency_id.name}"
    
    @api.depends('voucher_number', 'verification_token')
    def _compute_qr_code(self):
        """Generate QR code for voucher verification"""
        for record in self:
            if record.voucher_number and record.voucher_number != _('New'):
                try:
                    # Generate QR code data
                    qr_data = record._get_qr_code_data()
                    
                    # Create QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    # Generate image
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    
                    record.qr_code = base64.b64encode(buffer.getvalue())
                except Exception as e:
                    _logger.warning(f"Failed to generate QR code for voucher {record.voucher_number}: {e}")
                    record.qr_code = False
            else:
                record.qr_code = False
    
    @api.depends('verification_token')
    def _compute_qr_verification_url(self):
        """Generate public verification URL"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.verification_token:
                record.qr_verification_url = f"{base_url}/payment/verify/{record.verification_token}"
            else:
                record.qr_verification_url = False
    
    @api.depends('state')
    def _compute_user_permissions(self):
        """Calculate user permissions for workflow actions"""
        for record in self:
            user = self.env.user
            
            record.can_review = (
                record.state == 'draft' and
                user.has_group('payment_approval_pro.group_payment_reviewer')
            )
            
            record.can_approve = (
                record.state == 'review' and
                user.has_group('payment_approval_pro.group_payment_approver')
            )
            
            record.can_authorize = (
                record.state == 'approve' and
                user.has_group('payment_approval_pro.group_payment_authorizer')
            )
    
    @api.depends('state')
    def _compute_is_readonly(self):
        """Determine if voucher should be readonly"""
        for record in self:
            record.is_readonly = record.state in ('authorize', 'paid', 'cancel')

    # ================================
    # CRUD METHODS
    # ================================
    
    @api.model
    def create(self, vals):
        """Create voucher with sequence number and verification token"""
        if vals.get('voucher_number', _('New')) == _('New'):
            vals['voucher_number'] = self.env['ir.sequence'].next_by_code('payment.voucher') or _('New')
        
        if not vals.get('verification_token'):
            vals['verification_token'] = self._generate_verification_token()
        
        voucher = super().create(vals)
        
        # Log creation
        voucher.message_post(
            body=_("Payment voucher created by %s") % self.env.user.name,
            message_type='notification'
        )
        
        return voucher
    
    def write(self, vals):
        """Override write to add state change logging"""
        for record in self:
            if 'state' in vals and vals['state'] != record.state:
                old_state = dict(self._fields['state'].selection).get(record.state)
                new_state = dict(self._fields['state'].selection).get(vals['state'])
                
                record.message_post(
                    body=_("Status changed from %s to %s by %s") % (old_state, new_state, self.env.user.name),
                    message_type='notification'
                )
        
        return super().write(vals)
    
    def unlink(self):
        """Prevent deletion of non-draft vouchers"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft vouchers can be deleted. Cancel the voucher instead."))
        return super().unlink()

    # ================================
    # WORKFLOW ACTION METHODS
    # ================================
    
    def action_submit_for_review(self):
        """Submit voucher for review"""
        self.ensure_one()
        self._validate_voucher_data()
        
        reviewer = self._get_next_reviewer()
        
        self.write({
            'state': 'review',
            'reviewer_id': reviewer.id,
            'review_date': fields.Datetime.now(),
        })
        
        self._create_review_activity(reviewer)
        self._send_notification('review', reviewer)
        
        return True
    
    def action_approve(self):
        """Approve voucher"""
        self.ensure_one()
        self._check_approval_rights('approve')
        
        self.write({
            'state': 'approve',
            'approval_date': fields.Datetime.now(),
            'approver_id': self.env.user.id,
        })
        
        # Find next authorizer
        authorizer = self._get_next_authorizer()
        if authorizer:
            self._create_authorization_activity(authorizer)
            self._send_notification('approve', authorizer)
        
        return True
    
    def action_authorize(self):
        """Authorize payment and create payment entry"""
        self.ensure_one()
        self._check_approval_rights('authorize')
        
        # Create the actual payment
        payment = self._create_payment_entry()
        
        self.write({
            'state': 'authorize',
            'authorization_date': fields.Datetime.now(),
            'authorizer_id': self.env.user.id,
            'payment_id': payment.id,
        })
        
        self._send_notification('authorize')
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Created'),
            'res_model': 'account.payment',
            'res_id': payment.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_mark_paid(self):
        """Mark voucher as paid (when payment is posted)"""
        self.ensure_one()
        
        if self.state != 'authorize':
            raise UserError(_("Only authorized vouchers can be marked as paid."))
        
        self.write({
            'state': 'paid',
            'payment_posted_date': fields.Datetime.now(),
        })
        
        self._send_notification('paid')
        return True
    
    def action_cancel(self):
        """Cancel voucher"""
        self.ensure_one()
        
        if self.state == 'paid':
            raise UserError(_("Cannot cancel a paid voucher."))
        
        self.write({'state': 'cancel'})
        
        # Cancel related activities
        self.activity_unlink(['payment_approval_pro.mail_activity_payment_review',
                             'payment_approval_pro.mail_activity_payment_authorize'])
        
        self._send_notification('cancel')
        return True
    
    def action_reset_to_draft(self):
        """Reset voucher to draft state"""
        self.ensure_one()
        
        if self.state == 'paid':
            raise UserError(_("Cannot reset a paid voucher to draft."))
        
        if self.payment_id:
            raise UserError(_("Cannot reset voucher with created payment. Cancel the payment first."))
        
        self.write({
            'state': 'draft',
            'reviewer_id': False,
            'approver_id': False,
            'authorizer_id': False,
            'review_date': False,
            'approval_date': False,
            'authorization_date': False,
        })
        
        return True

    # ================================
    # HELPER METHODS
    # ================================
    
    def _validate_voucher_data(self):
        """Validate voucher data before submission"""
        self.ensure_one()
        
        if not self.partner_id:
            raise ValidationError(_("Please select a vendor/payee."))
        
        if not self.amount or self.amount <= 0:
            raise ValidationError(_("Please enter a valid payment amount."))
        
        if not self.journal_id:
            raise ValidationError(_("Please select a payment journal."))
        
        if not self.payment_date:
            raise ValidationError(_("Please set a payment date."))
    
    def _check_approval_rights(self, action):
        """Check if current user has rights for the action"""
        user = self.env.user
        
        if action == 'approve' and not user.has_group('payment_approval_pro.group_payment_approver'):
            raise AccessError(_("You don't have permission to approve payments."))
        
        if action == 'authorize' and not user.has_group('payment_approval_pro.group_payment_authorizer'):
            raise AccessError(_("You don't have permission to authorize payments."))
    
    def _get_next_reviewer(self):
        """Get next available reviewer"""
        reviewers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('payment_approval_pro.group_payment_reviewer').id)
        ], limit=1)
        
        if not reviewers:
            raise UserError(_("No payment reviewers available."))
        
        return reviewers[0]
    
    def _get_next_authorizer(self):
        """Get next available authorizer"""
        authorizers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('payment_approval_pro.group_payment_authorizer').id)
        ], limit=1)
        
        return authorizers[0] if authorizers else False
    
    def _create_payment_entry(self):
        """Create standard Odoo payment when authorized"""
        self.ensure_one()
        
        if not self.journal_id:
            # Get default payment journal
            journal = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            
            if not journal:
                raise UserError(_("No payment journal found. Please configure a bank or cash journal."))
            
            self.journal_id = journal
        
        payment_vals = {
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'payment_date': self.payment_date,
            'ref': f"{self.voucher_number} - {self.reference or ''}".strip(' -'),
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
        }
        
        payment = self.env['account.payment'].create(payment_vals)
        
        return payment
    
    def _generate_verification_token(self):
        """Generate secure verification token"""
        return secrets.token_urlsafe(32)
    
    def _get_qr_code_data(self):
        """Generate QR code data string"""
        return f"{self.qr_verification_url}?voucher={self.voucher_number}&amount={self.amount}"
    
    def _create_review_activity(self, reviewer):
        """Create review activity for assigned reviewer"""
        self.activity_schedule(
            'payment_approval_pro.mail_activity_payment_review',
            user_id=reviewer.id,
            summary=f"Review payment voucher {self.voucher_number}",
            note=f"Payment voucher {self.voucher_number} for {self.partner_id.name} "
                 f"({format_amount(self.env, self.amount, self.currency_id)}) needs review."
        )
    
    def _create_authorization_activity(self, authorizer):
        """Create authorization activity"""
        self.activity_schedule(
            'payment_approval_pro.mail_activity_payment_authorize',
            user_id=authorizer.id,
            summary=f"Authorize payment voucher {self.voucher_number}",
            note=f"Payment voucher {self.voucher_number} for {self.partner_id.name} "
                 f"({format_amount(self.env, self.amount, self.currency_id)}) is approved and needs authorization."
        )
    
    def _send_notification(self, stage, assigned_user=None):
        """Send email notification for workflow stage"""
        template_map = {
            'review': 'payment_approval_pro.email_template_payment_review',
            'approve': 'payment_approval_pro.email_template_payment_approved',
            'authorize': 'payment_approval_pro.email_template_payment_authorized',
            'paid': 'payment_approval_pro.email_template_payment_paid',
            'cancel': 'payment_approval_pro.email_template_payment_cancelled',
        }
        
        template_id = template_map.get(stage)
        if template_id:
            try:
                template = self.env.ref(template_id)
                if assigned_user:
                    template.with_context(assigned_user=assigned_user).send_mail(self.id, force_send=True)
                else:
                    template.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.warning(f"Failed to send notification for stage {stage}: {e}")

    # ================================
    # REPORT METHODS
    # ================================
    
    def action_print_voucher(self):
        """Print payment voucher report"""
        self.ensure_one()
        return self.env.ref('payment_approval_pro.action_report_payment_voucher').report_action(self)
    
    def get_report_data(self):
        """Get data for voucher report"""
        self.ensure_one()
        return {
            'voucher': self,
            'company': self.company_id,
            'qr_code': self.qr_code,
            'amount_words': self.amount_words,
            'workflow_status': dict(self._fields['state'].selection).get(self.state),
        }
