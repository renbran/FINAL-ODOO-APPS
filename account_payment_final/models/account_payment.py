import base64
import qrcode
import io
import logging
import secrets
from datetime import datetime, timedelta
from num2words import num2words
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools import html_escape

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _order = 'date desc, id desc'

    # ============================================================================
    # ENHANCED FIELDS
    # ============================================================================
    
    # Core Voucher Fields
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
        copy=False,
        help="Unique voucher number generated automatically"
    )
    
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('for_authorization', 'For Authorization'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Approval State', default='draft', tracking=True, 
       help="Current state in the approval workflow")
    
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional notes or remarks for this payment voucher"
    )
    
    # Workflow Users and Timestamps
    submitted_by = fields.Many2one('res.users', string='Submitted By', readonly=True)
    submitted_date = fields.Datetime(string='Submitted Date', readonly=True)
    
    reviewed_by = fields.Many2one('res.users', string='Reviewed By', readonly=True)
    reviewed_date = fields.Datetime(string='Reviewed Date', readonly=True)
    
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    
    authorized_by = fields.Many2one('res.users', string='Authorized By', readonly=True)
    authorized_date = fields.Datetime(string='Authorized Date', readonly=True)
    
    posted_by = fields.Many2one('res.users', string='Posted By', readonly=True)
    posted_date = fields.Datetime(string='Posted Date', readonly=True)
    
    # Enhanced Signature Management
    signatory_ids = fields.Many2many(
        'payment.signatory',
        string='Required Signatories',
        domain="[('is_active', '=', True), ('company_id', '=', company_id)]"
    )
    
    creator_signature = fields.Binary(string='Creator Signature')
    creator_signature_date = fields.Datetime(string='Creator Signature Date')
    
    reviewer_signature = fields.Binary(string='Reviewer Signature')
    reviewer_signature_date = fields.Datetime(string='Reviewer Signature Date')
    
    approver_signature = fields.Binary(string='Approver Signature')
    approver_signature_date = fields.Datetime(string='Approver Signature Date')
    
    authorizer_signature = fields.Binary(string='Authorizer Signature')
    authorizer_signature_date = fields.Datetime(string='Authorizer Signature Date')
    
    receiver_signature = fields.Binary(string='Receiver Signature')
    receiver_signature_date = fields.Datetime(string='Receiver Signature Date')
    
    # QR Code and Verification
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code', store=True)
    qr_in_report = fields.Boolean(string='Include QR in Report', default=True)
    verification_url = fields.Char(string='Verification URL', compute='_compute_verification_url')
    qr_verification_token = fields.Char(string='QR Verification Token', readonly=True)
    
    # Amount in Words
    amount_in_words = fields.Char(
        string='Amount in Words',
        compute='_compute_amount_in_words',
        store=True
    )
    
    # Enhanced Display and Workflow
    display_name = fields.Char(compute='_compute_display_name', store=True)
    color = fields.Integer(compute='_compute_color')
    workflow_step = fields.Integer(default=0, help="Current workflow step number")
    total_steps = fields.Integer(compute='_compute_total_steps')
    
    # Document Information
    related_document_info = fields.Char(
        string='Related Document Info',
        compute='_compute_related_document_info',
        help="Information about related invoices/bills"
    )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('payment_type')
    def _compute_total_steps(self):
        """Compute total workflow steps based on payment type"""
        for record in self:
            # Receipts: 3 steps (submit → review → post)
            # Payments: 5 steps (submit → review → approve → authorize → post)
            record.total_steps = 3 if record.payment_type == 'inbound' else 5
    
    @api.depends('amount', 'currency_id')
    def _compute_amount_in_words(self):
        """Convert amount to words with enhanced formatting"""
        for record in self:
            if record.amount and record.currency_id:
                try:
                    # Use num2words for better conversion
                    amount_words = num2words(record.amount, lang='en').title()
                    currency_name = record.currency_id.name
                    
                    # Format: "One Thousand Five Hundred United States Dollars Only"
                    record.amount_in_words = f"{amount_words} {currency_name} Only"
                except Exception as e:
                    _logger.warning(f"Error converting amount to words: {e}")
                    record.amount_in_words = f"{record.currency_id.name} {record.amount:,.2f}"
            else:
                record.amount_in_words = ""
    
    @api.depends('voucher_number', 'name', 'partner_id', 'payment_type', 'amount')
    def _compute_display_name(self):
        """Enhanced display name for better UX"""
        for record in self:
            if record.partner_id:
                payment_type = 'Receipt' if record.payment_type == 'inbound' else 'Payment'
                voucher_ref = record.voucher_number or record.name or 'New'
                amount_str = f"{record.currency_id.symbol or ''}{record.amount:,.2f}" if record.amount else ""
                record.display_name = f"{payment_type} {voucher_ref} - {record.partner_id.name} {amount_str}"
            else:
                record.display_name = record.voucher_number or record.name or 'New Payment'
    
    @api.depends('approval_state')
    def _compute_color(self):
        """Compute color for kanban view based on approval state"""
        color_map = {
            'draft': 1,          # Light blue
            'submitted': 2,      # Blue
            'under_review': 3,   # Yellow
            'for_approval': 7,   # Orange
            'for_authorization': 9,  # Red
            'approved': 10,      # Green
            'posted': 10,        # Green
            'cancelled': 8,      # Gray
        }
        for record in self:
            record.color = color_map.get(record.approval_state, 0)
    
    @api.depends('voucher_number', 'qr_verification_token')
    def _compute_verification_url(self):
        """Generate verification URL for QR code"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for record in self:
            if record.voucher_number and base_url:
                # Generate verification token if not exists
                if not record.qr_verification_token:
                    record.qr_verification_token = record._generate_verification_token()
                record.verification_url = f"{base_url}/payment/verify/{record.qr_verification_token}"
            else:
                record.verification_url = ""
    
    @api.depends('verification_url', 'qr_in_report')
    def _compute_qr_code(self):
        """Generate QR code for payment verification"""
        for record in self:
            if record.qr_in_report and record.verification_url:
                try:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(record.verification_url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    temp = io.BytesIO()
                    img.save(temp, format="PNG")
                    qr_img = temp.getvalue()
                    record.qr_code = base64.b64encode(qr_img)
                except Exception as e:
                    _logger.warning(f"Error generating QR code: {e}")
                    record.qr_code = False
            else:
                record.qr_code = False
    
    @api.depends('reconciled_invoice_ids', 'reconciled_bill_ids')
    def _compute_related_document_info(self):
        """Compute information about related documents"""
        for record in self:
            documents = []
            
            # Get related invoices
            for invoice in record.reconciled_invoice_ids:
                documents.append({
                    'name': invoice.name,
                    'type': 'Customer Invoice' if invoice.move_type == 'out_invoice' else 'Customer Credit Note',
                    'amount': invoice.amount_total,
                    'date': invoice.invoice_date,
                })
            
            # Get related bills
            for bill in record.reconciled_bill_ids:
                documents.append({
                    'name': bill.name,
                    'type': 'Vendor Bill' if bill.move_type == 'in_invoice' else 'Vendor Credit Note',
                    'amount': bill.amount_total,
                    'date': bill.invoice_date,
                })
            
            if documents:
                doc_count = len(documents)
                if doc_count == 1:
                    record.related_document_info = f"{documents[0]['name']} ({documents[0]['type']})"
                else:
                    record.related_document_info = f"{doc_count} documents"
            else:
                record.related_document_info = "No related documents"

    # ============================================================================
    # WORKFLOW METHODS
    # ============================================================================
    
    def action_submit_for_review(self):
        """Submit payment for review with enhanced validation"""
        self.ensure_one()
        self._validate_payment_data()
        self._check_workflow_permission('submit')
        
        if not self.voucher_number:
            self._generate_voucher_number()
        
        self.write({
            'approval_state': 'under_review',
            'submitted_by': self.env.user.id,
            'submitted_date': fields.Datetime.now(),
            'workflow_step': 1,
        })
        
        # Create activities for reviewers
        self._create_workflow_activities('review')
        self._send_workflow_notification('submitted')
        self._post_workflow_message("submitted for review")
        
        return self._return_success_notification(_('Payment voucher submitted for review successfully.'))
    
    def action_review_approve(self):
        """Review and approve - moves to next stage based on payment type"""
        self.ensure_one()
        self._check_workflow_permission('review')
        
        # For receipts, go directly to approved
        # For payments, go to for_approval
        if self.payment_type == 'inbound':
            next_state = 'approved'
            next_step = 2
            activity_type = 'post'
            message = "reviewed and approved (receipt workflow)"
        else:
            next_state = 'for_approval'
            next_step = 2
            activity_type = 'approve'
            message = "reviewed and moved to approval stage"
        
        self.write({
            'approval_state': next_state,
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
            'workflow_step': next_step,
        })
        
        # Create activities for next stage
        self._create_workflow_activities(activity_type)
        self._send_workflow_notification('reviewed')
        self._post_workflow_message(message)
        
        return self._return_success_notification(_('Payment voucher reviewed successfully.'))
    
    def action_approve_payment(self):
        """Approve payment (only for outbound payments)"""
        self.ensure_one()
        self._check_workflow_permission('approve')
        
        if self.payment_type != 'outbound':
            raise UserError(_("This action is only available for outbound payments."))
        
        self.write({
            'approval_state': 'for_authorization',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
            'workflow_step': 3,
        })
        
        # Create activities for authorizers
        self._create_workflow_activities('authorize')
        self._send_workflow_notification('approved')
        self._post_workflow_message("approved and moved to authorization stage")
        
        return self._return_success_notification(_('Payment voucher approved successfully.'))
    
    def action_authorize_payment(self):
        """Authorize payment (final approval before posting)"""
        self.ensure_one()
        self._check_workflow_permission('authorize')
        
        self.write({
            'approval_state': 'approved',
            'authorized_by': self.env.user.id,
            'authorized_date': fields.Datetime.now(),
            'workflow_step': 4,
        })
        
        # Create activities for posters
        self._create_workflow_activities('post')
        self._send_workflow_notification('authorized')
        self._post_workflow_message("authorized and ready for posting")
        
        return self._return_success_notification(_('Payment voucher authorized successfully.'))
    
    def action_post_payment(self):
        """Post the payment (final step)"""
        self.ensure_one()
        self._check_workflow_permission('post')
        
        # Validate one more time before posting
        self._validate_payment_data()
        
        # Post the payment using Odoo's standard method
        self.action_post()
        
        self.write({
            'approval_state': 'posted',
            'posted_by': self.env.user.id,
            'posted_date': fields.Datetime.now(),
            'workflow_step': self.total_steps,
        })
        
        # Close all activities
        self.activity_ids.action_done()
        
        self._send_workflow_notification('posted')
        self._post_workflow_message("posted successfully")
        
        return self._return_success_notification(_('Payment voucher posted successfully.'))
    
    def action_reject_payment(self):
        """Reject payment and return to draft"""
        self.ensure_one()
        self._check_rejection_permissions()
        
        # Reset to draft
        self.write({
            'approval_state': 'draft',
            'workflow_step': 0,
        })
        
        # Clear workflow fields based on current stage
        self._clear_workflow_fields()
        
        # Close all activities
        self.activity_ids.action_done()
        
        self._send_workflow_notification('rejected')
        self._post_workflow_message("rejected and returned to draft")
        
        return self._return_success_notification(_('Payment voucher rejected and returned to draft.'))

    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _generate_voucher_number(self):
        """Generate unique voucher number using sequence"""
        if not self.voucher_number:
            sequence_code = 'payment.voucher.out' if self.payment_type == 'outbound' else 'receipt.voucher.in'
            
            # Try to get sequence, create if not exists
            sequence = self.env['ir.sequence'].search([
                ('code', '=', sequence_code), 
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            
            if not sequence:
                sequence = self._create_voucher_sequence(sequence_code)
            
            self.voucher_number = sequence.next_by_id()
    
    def _create_voucher_sequence(self, sequence_code):
        """Create voucher sequence if it doesn't exist"""
        if self.payment_type == 'outbound':
            sequence_name = 'Payment Voucher'
            prefix = 'PV'
        else:
            sequence_name = 'Receipt Voucher'
            prefix = 'RV'
        
        return self.env['ir.sequence'].create({
            'name': sequence_name,
            'code': sequence_code,
            'prefix': prefix,
            'padding': 5,
            'company_id': self.company_id.id or False,
        })
    
    def _generate_verification_token(self):
        """Generate secure verification token"""
        return secrets.token_urlsafe(32)
    
    def _validate_payment_data(self):
        """Enhanced validation for payment data"""
        if not self.partner_id:
            raise ValidationError(_("Partner must be specified."))
        if not self.amount or self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))
        if not self.currency_id:
            raise ValidationError(_("Currency must be specified."))
        if not self.journal_id:
            raise