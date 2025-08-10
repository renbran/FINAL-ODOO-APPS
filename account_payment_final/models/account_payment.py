import base64
import qrcode
import io
import logging
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
        ('for_authorization', 'For Authorization'),  # Only for payments
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
        domain="[('is_active', '=', True)]"
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
                amount_str = f"{record.currency_id.symbol}{record.amount:,.2f}" if record.amount else ""
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
    
    @api.depends('id', 'voucher_number')
    def _compute_verification_url(self):
        """Generate verification URL for QR code"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for record in self:
            if record.id and base_url:
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
    # WORKFLOW METHODS - ENHANCED
    # ============================================================================
    
    def action_submit_for_review(self):
        """Submit payment for review with enhanced validation"""
        self.ensure_one()
        self._validate_payment_data()
        self._check_workflow_permission('submit')
        
        if not self.voucher_number:
            self._generate_voucher_number()
        
        # Create activity for reviewer
        reviewer_group = 'payment_voucher_enhanced.group_payment_voucher_reviewer'
        reviewer_users = self.env.ref(reviewer_group).users
        
        self.write({
            'approval_state': 'under_review',
            'submitted_by': self.env.user.id,
            'submitted_date': fields.Datetime.now(),
            'workflow_step': 1,
        })
        
        # Create activities for reviewers
        for user in reviewer_users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Review Payment Voucher {self.voucher_number}',
                note=f'Payment voucher for {self.partner_id.name} - Amount: {self.currency_id.symbol}{self.amount:,.2f}',
                user_id=user.id,
            )
        
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
            activity_group = 'payment_voucher_enhanced.group_payment_voucher_poster'
            message = "reviewed and approved (receipt workflow)"
        else:
            next_state = 'for_approval'
            next_step = 2
            activity_group = 'payment_voucher_enhanced.group_payment_voucher_approver'
            message = "reviewed and moved to approval stage"
        
        self.write({
            'approval_state': next_state,
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
            'workflow_step': next_step,
        })
        
        # Create activities for next stage
        next_users = self.env.ref(activity_group).users
        for user in next_users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'{"Approve" if next_state == "for_approval" else "Post"} Payment Voucher {self.voucher_number}',
                note=f'Payment voucher for {self.partner_id.name} - Amount: {self.currency_id.symbol}{self.amount:,.2f}',
                user_id=user.id,
            )
        
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
        authorizer_users = self.env.ref('payment_voucher_enhanced.group_payment_voucher_authorizer').users
        for user in authorizer_users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Authorize Payment Voucher {self.voucher_number}',
                note=f'Payment voucher for {self.partner_id.name} - Amount: {self.currency_id.symbol}{self.amount:,.2f}',
                user_id=user.id,
            )
        
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
        poster_users = self.env.ref('payment_voucher_enhanced.group_payment_voucher_poster').users
        for user in poster_users:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Post Payment Voucher {self.voucher_number}',
                note=f'Payment voucher for {self.partner_id.name} - Amount: {self.currency_id.symbol}{self.amount:,.2f}',
                user_id=user.id,
            )
        
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
            sequence = self.env['ir.sequence'].search([('code', '=', sequence_code), ('company_id', '=', self.company_id.id)], limit=1)
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
        import secrets
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
            raise ValidationError(_("Journal must be specified."))
        if not self.date:
            raise ValidationError(_("Payment date must be specified."))
        
        # Check for large amounts requiring remarks
        max_amount = self.company_id.max_approval_amount or 10000.0
        if self.amount > max_amount and not self.remarks:
            raise ValidationError(_("Remarks are required for payments above %s %s") % (max_amount, self.currency_id.name))
    
    def _check_workflow_permission(self, action):
        """Check if user has permission for workflow action"""
        permission_map = {
            'submit': 'payment_voucher_enhanced.group_payment_voucher_user',
            'review': 'payment_voucher_enhanced.group_payment_voucher_reviewer',
            'approve': 'payment_voucher_enhanced.group_payment_voucher_approver',
            'authorize': 'payment_voucher_enhanced.group_payment_voucher_authorizer',
            'post': 'payment_voucher_enhanced.group_payment_voucher_poster',
        }
        
        required_group = permission_map.get(action)
        if required_group and not self.env.user.has_group(required_group):
            raise AccessError(_("You don't have permission to %s payments.") % action)
    
    def _check_rejection_permissions(self):
        """Check if user can reject at current stage"""
        current_stage = self.approval_state
        
        if current_stage == 'under_review':
            if not self.env.user.has_group('payment_voucher_enhanced.group_payment_voucher_reviewer'):
                raise AccessError(_("You don't have permission to reject payments at review stage."))
        elif current_stage == 'for_approval':
            if not self.env.user.has_group('payment_voucher_enhanced.group_payment_voucher_approver'):
                raise AccessError(_("You don't have permission to reject payments at approval stage."))
        elif current_stage == 'for_authorization':
            if not self.env.user.has_group('payment_voucher_enhanced.group_payment_voucher_authorizer'):
                raise AccessError(_("You don't have permission to reject payments at authorization stage."))
        else:
            raise AccessError(_("Cannot reject payment in current state."))
    
    def _clear_workflow_fields(self):
        """Clear workflow fields when rejecting"""
        clear_fields = {
            'submitted_by': False,
            'submitted_date': False,
            'reviewed_by': False,
            'reviewed_date': False,
            'approved_by': False,
            'approved_date': False,
            'authorized_by': False,
            'authorized_date': False,
        }
        self.write(clear_fields)
    
    def _post_workflow_message(self, action):
        """Post message to chatter for workflow actions"""
        body = _("Payment voucher %s %s by %s") % (
            self.voucher_number or self.name,
            action,
            self.env.user.name
        )
        self.message_post(
            body=body,
            subject=_("Payment Voucher %s") % action.title()
        )
    
    def _send_workflow_notification(self, notification_type):
        """Send email notifications for workflow actions"""
        template_map = {
            'submitted': 'payment_voucher_enhanced.email_template_payment_submitted',
            'reviewed': 'payment_voucher_enhanced.email_template_payment_reviewed',
            'approved': 'payment_voucher_enhanced.email_template_payment_approved',
            'authorized': 'payment_voucher_enhanced.email_template_payment_authorized',
            'posted': 'payment_voucher_enhanced.email_template_payment_posted',
            'rejected': 'payment_voucher_enhanced.email_template_payment_rejected',
        }
        
        template_ref = template_map.get(notification_type)
        if template_ref and self.company_id.send_approval_notifications:
            try:
                template = self.env.ref(template_ref, raise_if_not_found=False)
                if template:
                    template.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.warning(f"Failed to send notification email: {e}")
    
    def _return_success_notification(self, message):
        """Return success notification to user"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
    
    # ============================================================================
    # REPORT HELPER METHODS
    # ============================================================================
    
    def get_related_document_info(self):
        """Get detailed information about related documents for report"""
        self.ensure_one()
        
        documents = []
        
        # Get related invoices
        for invoice in self.reconciled_invoice_ids:
            documents.append(invoice)
        
        # Get related bills  
        for bill in self.reconciled_bill_ids:
            documents.append(bill)
        
        if documents:
            doc_count = len(documents)
            references = ", ".join([doc.name for doc in documents[:3]])  # Show first 3
            if doc_count > 3:
                references += f" and {doc_count - 3} more"
                
            if doc_count == 1:
                label = "Related Invoice/Bill"
            else:
                label = f"Related Documents ({doc_count})"
                
            return {
                'count': doc_count,
                'label': label,
                'references': references,
                'documents': documents,
            }
        else:
            return {
                'count': 0,
                'label': 'Related Document',
                'references': 'No related documents',
                'documents': [],
            }
    
    def get_signatory_info(self):
        """Get signatory information for report display"""
        self.ensure_one()
        
        signatories = []
        
        # Creator (always present)
        signatories.append({
            'role': 'Created By',
            'name': self.create_uid.name,
            'date': self.create_date,
            'signature': self.creator_signature,
            'required': True,
        })
        
        # Reviewer
        if self.reviewed_by:
            signatories.append({
                'role': 'Reviewed By',
                'name': self.reviewed_by.name,
                'date': self.reviewed_date,
                'signature': self.reviewer_signature,
                'required': True,
            })
        
        # For payments (4 signatures required)
        if self.payment_type == 'outbound':
            if self.approved_by:
                signatories.append({
                    'role': 'Approved By',
                    'name': self.approved_by.name,
                    'date': self.approved_date,
                    'signature': self.approver_signature,
                    'required': True,
                })
            
            if self.authorized_by:
                signatories.append({
                    'role': 'Authorized By',
                    'name': self.authorized_by.name,
                    'date': self.authorized_date,
                    'signature': self.authorizer_signature,
                    'required': True,
                })
        
        # Posted by (final)
        if self.posted_by:
            signatories.append({
                'role': 'Posted By',
                'name': self.posted_by.name,
                'date': self.posted_date,
                'signature': None,  # No signature required for posting
                'required': True,
            })
        
        # Receiver signature (for manual collection)
        signatories.append({
            'role': 'Received By',
            'name': 'Recipient Signature',
            'date': None,
            'signature': self.receiver_signature,
            'required': False,
        })
        
        return signatories
    
    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_workflow_history(self):
        """Show detailed workflow history"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Workflow History - {self.voucher_number}',
            'res_model': 'account.payment',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('payment_voucher_enhanced.view_payment_workflow_history').id,
            'target': 'new',
        }
    
    def action_print_voucher_osus(self):
        """Print OSUS branded payment voucher"""
        self.ensure_one()
        
        if self.approval_state == 'draft':
            raise UserError(_("Cannot print voucher for draft payments. Please submit for review first."))
        
        return self.env.ref('payment_voucher_enhanced.action_report_payment_voucher_osus').report_action(self)
    
    def action_verify_qr_code(self):
        """Open QR code verification in new tab"""
        self.ensure_one()
        
        if not self.verification_url:
            raise UserError(_("QR verification URL not available."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.verification_url,
            'target': 'new',
        }


# ============================================================================
# PAYMENT SIGNATORY MODEL
# ============================================================================

class PaymentSignatory(models.Model):
    _name = 'payment.signatory'
    _description = 'Payment Signatory'
    _order = 'sequence, name'

    name = fields.Char(string='Signatory Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    role = fields.Selection([
        ('creator', 'Creator'),
        ('reviewer', 'Reviewer'),
        ('approver', 'Approver'),
        ('authorizer', 'Authorizer'),
        ('receiver', 'Receiver'),
    ], string='Role', required=True)
    
    user_id = fields.Many2one('res.users', string='User', required=True)
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    is_active = fields.Boolean(string='Active', default=True)
    
    signature_image = fields.Binary(string='Signature Image')
    signature_style = fields.Selection([
        ('manual', 'Manual Signature'),
        ('digital', 'Digital Signature'),
        ('stamp', 'Stamp'),
    ], string='Signature Style', default='manual')
    
    notes = fields.Text(string='Notes')


# ============================================================================
# ACCOUNT MOVE INTEGRATION
# ============================================================================

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # Add workflow for invoices/bills
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Approval State', default='draft', tracking=True)
    
    voucher_count = fields.Integer(
        string='Payment Vouchers',
        compute='_compute_voucher_count'
    )
    
    @api.depends('line_ids.payment_id')
    def _compute_voucher_count(self):
        """Count related payment vouchers"""
        for move in self:
            vouchers = self.env['account.payment'].search([
                '|',
                ('reconciled_invoice_ids', 'in', move.ids),
                ('reconciled_bill_ids', 'in', move.ids)
            ])
            move.voucher_count = len(vouchers)
    
    def action_view_vouchers(self):
        """View related payment vouchers"""
        self.ensure_one()
        vouchers = self.env['account.payment'].search([
            '|',
            ('reconciled_invoice_ids', 'in', self.ids),
            ('reconciled_bill_ids', 'in', self.ids)
        ])
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Payment Vouchers',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', vouchers.ids)],
            'context': {'default_partner_id': self.partner_id.id}
        }
    
    def action_submit_invoice_for_approval(self):
        """Submit invoice/bill for approval workflow"""
        self.ensure_one()
        
        if self.move_type not in ['in_invoice', 'out_invoice']:
            raise UserError(_("Approval workflow is only available for invoices and bills."))
        
        self.approval_state = 'submitted'
        
        # Create activity for approvers
        approver_group = 'payment_voucher_enhanced.group_invoice_approver'
        if self.env.ref(approver_group, raise_if_not_found=False):
            approver_users = self.env.ref(approver_group).users
            for user in approver_users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=f'Approve Invoice {self.name}',
                    note=f'Invoice for {self.partner_id.name} - Amount: {self.currency_id.symbol}{self.amount_total:,.2f}',
                    user_id=user.id,
                )
        
        self.message_post(
            body=f"Invoice {self.name} submitted for approval by {self.env.user.name}",
            subject="Invoice Submitted for Approval"
        )
        
        return self._return_success_notification(_('Invoice submitted for approval.'))
    
    def action_approve_invoice(self):
        """Approve invoice/bill"""
        self.ensure_one()
        
        if not self.env.user.has_group('payment_voucher_enhanced.group_invoice_approver'):
            raise AccessError(_("You don't have permission to approve invoices."))
        
        self.approval_state = 'approved'
        self.activity_ids.action_done()
        
        self.message_post(
            body=f"Invoice {self.name} approved by {self.env.user.name}",
            subject="Invoice Approved"
        )
        
        return self._return_success_notification(_('Invoice approved successfully.'))
    
    def _return_success_notification(self, message):
        """Return success notification"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }


# ============================================================================
# RES CONFIG SETTINGS
# ============================================================================

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Payment Voucher Settings
    auto_post_approved_payments = fields.Boolean(
        related='company_id.auto_post_approved_payments',
        readonly=False
    )
    
    max_approval_amount = fields.Monetary(
        related='company_id.max_approval_amount',
        readonly=False
    )
    
    send_approval_notifications = fields.Boolean(
        related='company_id.send_approval_notifications',
        readonly=False
    )
    
    use_osus_branding = fields.Boolean(
        related='company_id.use_osus_branding',
        readonly=False
    )
    
    voucher_footer_message = fields.Text(
        related='company_id.voucher_footer_message',
        readonly=False
    )


# ============================================================================
# RES COMPANY EXTENSION
# ============================================================================

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # OSUS Payment Settings
    auto_post_approved_payments = fields.Boolean(
        string='Auto-Post Approved Payments',
        default=False,
        help="Automatically post payments when approved"
    )
    
    max_approval_amount = fields.Monetary(
        string='Maximum Approval Amount',
        currency_field='currency_id',
        default=10000.0,
        help="Maximum amount that can be approved without additional authorization"
    )
    
    send_approval_notifications = fields.Boolean(
        string='Send Email Notifications',
        default=True,
        help="Send email notifications for approval workflow"
    )
    
    use_osus_branding = fields.Boolean(
        string='Use OSUS Branding',
        default=True,
        help="Apply OSUS brand styling to reports"
    )
    
    voucher_footer_message = fields.Text(
        string='Voucher Footer Message',
        default='Thank you for your business with OSUS Real Estate',
        help="Custom footer message for payment vouchers"
    )
