from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, timedelta
import logging
import uuid
import base64
import hashlib
import secrets

# Import QR code libraries with error handling
try:
    import qrcode
    import qrcode.image.svg
    from qrcode.image.styledpil import StyledPilImage
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    logging.getLogger(__name__).warning("QR code libraries not available")

# Import num2words with fallback
try:
    from num2words import num2words
    NUM2WORDS_AVAILABLE = True
except ImportError:
    NUM2WORDS_AVAILABLE = False
    logging.getLogger(__name__).warning("num2words library not available")

# Import PIL with error handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.getLogger(__name__).warning("PIL library not available")

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    """Enhanced Payment with OSUS Approval Workflow - Odoo 17 Compatible"""
    _inherit = "account.payment"
    
    # =============================================================================
    # WORKFLOW STATE FIELD (Separate from core 'state' to avoid conflicts)
    # =============================================================================
    
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
    
    # =============================================================================
    # VOUCHER INFORMATION FIELDS
    # =============================================================================
    
    voucher_number = fields.Char(
        string='Voucher Number', 
        readonly=True, 
        copy=False,
        default=lambda self: _('New'),
        help="Auto-generated voucher number"
    )
    
    voucher_type = fields.Selection([
        ('payment', 'Payment Voucher'),
        ('receipt', 'Receipt Voucher')
    ], string='Voucher Type', compute='_compute_voucher_type', store=True,
       help="Type of voucher based on payment direction")
    
    @api.depends('payment_type')
    def _compute_voucher_type(self):
        """Compute voucher type based on payment type"""
        for payment in self:
            if payment.payment_type == 'inbound':
                payment.voucher_type = 'receipt'
            else:
                payment.voucher_type = 'payment'
    
    # =============================================================================
    # APPROVAL WORKFLOW FIELDS
    # =============================================================================
    
    requires_approval = fields.Boolean(
        string='Requires Approval', 
        compute='_compute_requires_approval',
        store=True,
        help="Whether this payment requires approval workflow"
    )
    
    # User Permission Check Field
    is_approve_person = fields.Boolean(
        string='Can User Approve',
        compute='_compute_is_approve_person',
        help="Check if current user can approve this payment"
    )
    
    @api.depends('amount', 'payment_type', 'currency_id', 'company_id')
    def _compute_requires_approval(self):
        """Determine if payment requires approval based on thresholds"""
        for payment in self:
            payment.requires_approval = payment._check_approval_threshold()
    
    @api.depends('voucher_state')
    def _compute_is_approve_person(self):
        """Check if current user can perform approval actions"""
        for payment in self:
            user = self.env.user
            
            # Check based on current state and user permissions
            if payment.voucher_state == 'submitted':
                payment.is_approve_person = user.has_group('account_payment_approval.group_payment_voucher_reviewer')
            elif payment.voucher_state == 'under_review':
                payment.is_approve_person = user.has_group('account_payment_approval.group_payment_voucher_approver')
            elif payment.voucher_state == 'approved':
                payment.is_approve_person = user.has_group('account_payment_approval.group_payment_voucher_authorizer')
            else:
                payment.is_approve_person = False
    
    def _check_approval_threshold(self):
        """Check if payment amount exceeds approval threshold"""
        self.ensure_one()
        
        if not self.amount or self.amount <= 0:
            return False
        
        # Get threshold from system parameters
        param_key = f'account_payment_approval.{self.payment_type}_approval_threshold'
        threshold = float(self.env['ir.config_parameter'].sudo().get_param(param_key, '1000.0'))
        
        # Convert amount to company currency for comparison
        amount_company_currency = self.amount
        if self.currency_id != self.company_id.currency_id:
            amount_company_currency = self.currency_id._convert(
                self.amount, 
                self.company_id.currency_id, 
                self.company_id, 
                self.date or fields.Date.today()
            )
        
        return amount_company_currency >= threshold
    
    # =============================================================================
    # WORKFLOW TRACKING FIELDS
    # =============================================================================
    
    # Workflow Dates
    submitted_date = fields.Datetime(string='Submitted Date', readonly=True)
    reviewed_date = fields.Datetime(string='Reviewed Date', readonly=True) 
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    authorized_date = fields.Datetime(string='Authorized Date', readonly=True)
    
    # Workflow Users
    reviewer_id = fields.Many2one('res.users', string='Reviewer', readonly=True)
    approver_id = fields.Many2one('res.users', string='Approver', readonly=True)
    authorizer_id = fields.Many2one('res.users', string='Authorizer', readonly=True)
    
    # =============================================================================
    # DIGITAL SIGNATURE FIELDS
    # =============================================================================
    
    creator_signature = fields.Binary(string='Creator Signature', attachment=True)
    creator_signature_date = fields.Datetime(string='Creator Signature Date', readonly=True)
    
    reviewer_signature = fields.Binary(string='Reviewer Signature', attachment=True)
    reviewer_signature_date = fields.Datetime(string='Reviewer Signature Date', readonly=True)
    
    approver_signature = fields.Binary(string='Approver Signature', attachment=True)
    approver_signature_date = fields.Datetime(string='Approved Signature Date', readonly=True)
    
    authorizer_signature = fields.Binary(string='Authorizer Signature', attachment=True)
    authorizer_signature_date = fields.Datetime(string='Authorizer Signature Date', readonly=True)
    
    # =============================================================================
    # QR CODE & VERIFICATION FIELDS
    # =============================================================================
    
    verification_token = fields.Char(
        string='Verification Token', 
        readonly=True, 
        copy=False,
        help="Unique token for QR verification"
    )
    
    qr_code = fields.Binary(
        string='QR Code', 
        compute='_compute_qr_code', 
        attachment=True,
        help="Generated QR code for payment verification"
    )
    
    verification_url = fields.Char(
        string='Verification URL', 
        compute='_compute_verification_url',
        help="URL for QR code verification"
    )
    
    # QR Validation Fields
    qr_validated = fields.Boolean(string='QR Validated', default=False, readonly=True)
    qr_validation_date = fields.Datetime(string='QR Validation Date', readonly=True)
    qr_validator_id = fields.Many2one('res.users', string='QR Validator', readonly=True)
    qr_scan_count = fields.Integer(string='QR Scan Count', default=0, readonly=True)
    
    # =============================================================================
    # PROGRESS TRACKING FIELDS
    # =============================================================================
    
    workflow_progress = fields.Float(
        string='Workflow Progress',
        compute='_compute_workflow_progress',
        help="Percentage of workflow completion"
    )
    
    @api.depends('voucher_state')
    def _compute_workflow_progress(self):
        """Calculate workflow progress percentage"""
        progress_map = {
            'draft': 0,
            'submitted': 20,
            'under_review': 40,
            'approved': 60,
            'authorized': 80,
            'posted': 100,
            'rejected': 0
        }
        
        for payment in self:
            payment.workflow_progress = progress_map.get(payment.voucher_state, 0)
    
    # =============================================================================
    # QR CODE COMPUTATION METHODS
    # =============================================================================
    
    @api.depends('verification_token')
    def _compute_qr_code(self):
        """Generate QR code for payment verification"""
        for payment in self:
            if payment.verification_token and QR_AVAILABLE:
                try:
                    # Create verification URL
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    verification_url = f"{base_url}/payment/verify/{payment.verification_token}"
                    
                    # Generate QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(verification_url)
                    qr.make(fit=True)
                    
                    # Create image
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convert to base64
                    import io
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    img_data = img_buffer.getvalue()
                    
                    payment.qr_code = base64.b64encode(img_data)
                except Exception as e:
                    _logger.error(f"Error generating QR code: {e}")
                    payment.qr_code = False
            else:
                payment.qr_code = False
    
    @api.depends('verification_token')
    def _compute_verification_url(self):
        """Compute verification URL"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for payment in self:
            if payment.verification_token:
                payment.verification_url = f"{base_url}/payment/verify/{payment.verification_token}"
            else:
                payment.verification_url = False
    
    # =============================================================================
    # VOUCHER NUMBER GENERATION
    # =============================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate voucher numbers"""
        for vals in vals_list:
            if vals.get('voucher_number', _('New')) == _('New'):
                vals['voucher_number'] = self._generate_voucher_number(vals)
            
            # Generate verification token
            if not vals.get('verification_token'):
                vals['verification_token'] = self._generate_verification_token()
        
        return super().create(vals_list)
    
    def _generate_voucher_number(self, vals):
        """Generate voucher number based on payment type"""
        payment_type = vals.get('payment_type', 'outbound')
        
        if payment_type == 'inbound':
            sequence = self.env['ir.sequence'].next_by_code('receipt.voucher') or _('RV/') + str(vals.get('id', ''))
        else:
            sequence = self.env['ir.sequence'].next_by_code('payment.voucher') or _('PV/') + str(vals.get('id', ''))
        
        return sequence
    
    def _generate_verification_token(self):
        """Generate secure verification token"""
        return secrets.token_urlsafe(32)
    
    # =============================================================================
    # WORKFLOW ACTION METHODS
    # =============================================================================
    
    def action_submit_for_approval(self):
        """Submit payment for approval - Alias for action_submit_for_review"""
        return self.action_submit_for_review()
    
    def action_submit_for_review(self):
        """Submit payment for review"""
        for payment in self:
            if payment.voucher_state != 'draft':
                raise UserError(_("Only draft payments can be submitted for review."))
            
            payment.write({
                'voucher_state': 'submitted',
                'submitted_date': fields.Datetime.now(),
            })
            
            payment._post_activity_log('Payment submitted for review')
            payment._send_notification_email('submitted')
    
    def action_review(self):
        """Review payment - Alias for action_start_review"""
        return self.action_start_review()

    def action_start_review(self):
        """Start review process"""
        for payment in self:
            if payment.voucher_state != 'submitted':
                raise UserError(_("Only submitted payments can be reviewed."))
            
            if not self._check_user_permission('review'):
                raise AccessError(_("You don't have permission to review payments."))
            
            payment.write({
                'voucher_state': 'under_review',
                'reviewed_date': fields.Datetime.now(),
                'reviewer_id': self.env.user.id,
            })
            
            payment._post_activity_log('Payment review started')
            payment._send_notification_email('under_review')
    
    def action_approve(self):
        """Approve payment"""
        for payment in self:
            if payment.voucher_state != 'under_review':
                raise UserError(_("Only payments under review can be approved."))
            
            if not self._check_user_permission('approve'):
                raise AccessError(_("You don't have permission to approve payments."))
            
            payment.write({
                'voucher_state': 'approved',
                'approved_date': fields.Datetime.now(),
                'approver_id': self.env.user.id,
            })
            
            payment._post_activity_log('Payment approved')
            payment._send_notification_email('approved')
    
    def action_authorize(self):
        """Authorize payment"""
        for payment in self:
            if payment.voucher_state != 'approved':
                raise UserError(_("Only approved payments can be authorized."))
            
            if not self._check_user_permission('authorize'):
                raise AccessError(_("You don't have permission to authorize payments."))
            
            payment.write({
                'voucher_state': 'authorized',
                'authorized_date': fields.Datetime.now(),
                'authorizer_id': self.env.user.id,
            })
            
            payment._post_activity_log('Payment authorized')
            payment._send_notification_email('authorized')
    
    def action_reject(self):
        """Reject payment"""
        for payment in self:
            if payment.voucher_state not in ['submitted', 'under_review', 'approved']:
                raise UserError(_("Only submitted, under review, or approved payments can be rejected."))
            
            payment.write({
                'voucher_state': 'rejected',
            })
            
            payment._post_activity_log('Payment rejected')
            payment._send_notification_email('rejected')
    
    def action_reset_to_draft(self):
        """Reset payment to draft"""
        for payment in self:
            if not self._check_user_permission('reset'):
                raise AccessError(_("You don't have permission to reset payments."))
            
            payment.write({
                'voucher_state': 'draft',
                'submitted_date': False,
                'reviewed_date': False,
                'approved_date': False,
                'authorized_date': False,
                'reviewer_id': False,
                'approver_id': False,
                'authorizer_id': False,
            })
            
            payment._post_activity_log('Payment reset to draft')
    
    # =============================================================================
    # REPORT & VERIFICATION ACTIONS
    # =============================================================================
    
    def action_qr_verification_view(self):
        """Open QR verification view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.verification_url,
            'target': 'new',
        }
    
    def action_print_payment_voucher(self):
        """Print payment voucher report"""
        self.ensure_one()
        return self.env.ref('account_payment_approval.action_report_payment_voucher').report_action(self)
    
    def action_print_receipt_voucher(self):
        """Print receipt voucher report"""
        self.ensure_one()
        return self.env.ref('account_payment_approval.action_report_receipt_voucher').report_action(self)
    
    def action_email_payment_voucher(self):
        """Email payment voucher"""
        self.ensure_one()
        template = self.env.ref('account_payment_approval.email_template_payment_voucher', raise_if_not_found=False)
        if template:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_model': 'account.payment',
                    'default_res_id': self.id,
                    'default_template_id': template.id,
                    'force_email': True,
                }
            }
        else:
            raise UserError(_("Email template not found"))

    def action_print_multiple_reports(self):
        """Open wizard for multiple report options"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Report Options'),
            'res_model': 'payment.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
                'default_report_types': 'enhanced',
                'default_format_type': 'pdf',
            }
        }

    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _check_user_permission(self, action):
        """Check if user has permission for specific action"""
        user = self.env.user
        
        permission_map = {
            'review': 'account_payment_approval.group_payment_voucher_reviewer',
            'approve': 'account_payment_approval.group_payment_voucher_approver',
            'authorize': 'account_payment_approval.group_payment_voucher_authorizer',
            'reset': 'account_payment_approval.group_payment_voucher_manager',
        }
        
        group_xmlid = permission_map.get(action)
        if group_xmlid:
            return user.has_group(group_xmlid)
        
        return False
    
    def _post_activity_log(self, message):
        """Post activity log message"""
        self.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
    
    def _send_notification_email(self, stage):
        """Send notification email for workflow stage"""
        template_name = f'account_payment_approval.email_template_payment_{stage}'
        try:
            template = self.env.ref(template_name)
            template.send_mail(self.id, force_send=True)
        except ValueError:
            _logger.warning(f"Email template {template_name} not found")
    
    # =============================================================================
    # OVERRIDE CORE METHODS
    # =============================================================================
    
    def action_post(self):
        """Override post to check authorization"""
        for payment in self:
            if payment.requires_approval and payment.voucher_state != 'authorized':
                raise UserError(_("Payment must be authorized before posting."))
        
        result = super().action_post()
        
        # Update voucher state after posting
        for payment in self:
            if payment.voucher_state == 'authorized':
                payment.voucher_state = 'posted'
                payment._post_activity_log('Payment posted')
                payment._send_notification_email('posted')
        
        return result