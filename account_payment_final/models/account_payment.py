from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
import qrcode
import base64
from io import BytesIO
import logging
import datetime

_logger = logging.getLogger(__name__)


def generate_qr_code_payment(value):
    """Generate QR code for payment data with enhanced error handling"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(value)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        stream = BytesIO()
        img.save(stream, format="PNG")
        qr_img = base64.b64encode(stream.getvalue())
        return qr_img
    except Exception as e:
        _logger.error(f"Error generating QR code: {e}")
        return False


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # ============================================================================
    # FIELDS
    # ============================================================================

    # QR Code fields
    qr_code = fields.Binary(
        string="Payment QR Code",
        compute='_compute_payment_qr_code',
        store=True,
        help="QR code containing payment verification URL"
    )
    
    qr_in_report = fields.Boolean(
        string='Display QR Code in Report',
        default=True,
        help="Whether to display QR code in payment voucher report"
    )

    # Enhanced 4-Stage Approval Workflow State
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('for_authorization', 'For Authorization'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Approval State', default='draft', tracking=True, copy=False,
       help="Current approval state of the payment voucher")

    # Enhanced fields for OSUS voucher system
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for this payment voucher"
    )

    # Voucher number with automatic generation
    voucher_number = fields.Char(
        string='Voucher Number',
        copy=False,
        readonly=True,
        index=True,
        help="Unique voucher number generated automatically"
    )

    # Enhanced workflow fields for 4-stage approval
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        copy=False,
        help="User who reviewed the payment (Stage 1)"
    )

    reviewer_date = fields.Datetime(
        string='Review Date',
        copy=False,
        help="Date when the payment was reviewed"
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        copy=False,
        help="User who approved the payment (Stage 2)"
    )

    approver_date = fields.Datetime(
        string='Approval Date',
        copy=False,
        help="Date when the payment was approved"
    )

    authorizer_id = fields.Many2one(
        'res.users',
        string='Authorized By',
        copy=False,
        help="User who authorized the payment (Stage 3 - Vendor payments only)"
    )

    authorizer_date = fields.Datetime(
        string='Authorization Date',
        copy=False,
        help="Date when the payment was authorized"
    )

    authorized_by = fields.Char(
        string='Final Authorized By',
        compute='_compute_authorized_by',
        store=True,
        help="Name of the person who gave final authorization"
    )

    actual_approver_id = fields.Many2one(
        'res.users',
        string='Posted By User',
        copy=False,
        help="User who actually posted the payment",
        readonly=True
    )

    destination_account_id = fields.Many2one(
        'account.account',
        string='Destination Account',
        domain="[('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card'])]",
        help="Account where the payment will be posted"
    )

    # Enhanced display name for vouchers
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    # Color field for kanban view
    color = fields.Integer(
        string='Color',
        compute='_compute_color',
        store=True
    )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================

    @api.depends('name', 'payment_type', 'partner_id', 'amount', 'currency_id', 'voucher_number')
    def _compute_display_name(self):
        """Compute enhanced display name for vouchers"""
        for record in self:
            if record.voucher_number and record.partner_id:
                payment_type_label = 'Receipt' if record.payment_type == 'inbound' else 'Payment'
                record.display_name = f"{payment_type_label} Voucher {record.voucher_number} - {record.partner_id.name}"
            elif record.name and record.partner_id:
                payment_type_label = 'Receipt' if record.payment_type == 'inbound' else 'Payment'
                record.display_name = f"{payment_type_label} Voucher {record.name} - {record.partner_id.name}"
            else:
                record.display_name = record.voucher_number or record.name or 'New Payment'

    @api.depends('approval_state')
    def _compute_color(self):
        """Compute color for kanban view based on approval state"""
        color_map = {
            'draft': 1,          # Light blue
            'under_review': 3,   # Yellow
            'for_approval': 7,   # Orange
            'for_authorization': 9,  # Red
            'approved': 10,      # Green
            'posted': 10,        # Green
            'cancelled': 2,      # Gray
        }
        for record in self:
            record.color = color_map.get(record.approval_state, 0)

    @api.depends('name', 'amount', 'partner_id', 'date', 'approval_state', 'voucher_number', 'qr_in_report')
    def _compute_payment_qr_code(self):
        """Generate QR code for payment voucher verification"""
        for record in self:
            if record.qr_in_report and record.id:
                try:
                    # Get base URL from system parameters
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
                    
                    if base_url and record._origin.id:
                        # Create verification URL that points to our controller
                        qr_data = f"{base_url}/payment/verify/{record._origin.id}"
                    else:
                        # Fallback: Include structured payment details for manual verification
                        voucher_ref = record.voucher_number or record.name or 'Draft Payment'
                        partner_name = record.partner_id.name if record.partner_id else 'Unknown Partner'
                        amount_str = f"{record.amount:.2f} {record.currency_id.name if record.currency_id else 'USD'}"
                        date_str = record.date.strftime('%Y-%m-%d') if record.date else 'Draft'
                        
                        # Structured data that can be manually verified
                        qr_data = f"""PAYMENT VERIFICATION
Voucher: {voucher_ref}
Amount: {amount_str}
To: {partner_name}
Date: {date_str}
Status: {record.approval_state.upper()}
Company: {record.company_id.name}
Verify at: {base_url}/payment/qr-guide"""
                    
                    # Generate the QR code image
                    record.qr_code = generate_qr_code_payment(qr_data)
                except Exception as e:
                    _logger.error(f"Error generating QR code for payment {record.voucher_number or 'Draft'}: {e}")
                    record.qr_code = False
            else:
                record.qr_code = False

    @api.depends('approval_state', 'actual_approver_id', 'write_uid', 'authorizer_id', 'approver_id')
    def _compute_authorized_by(self):
        """Compute authorization field showing who approved and posted the payment"""
        for record in self:
            if record.actual_approver_id:
                record.authorized_by = record.actual_approver_id.name
            elif record.authorizer_id:
                record.authorized_by = record.authorizer_id.name
            elif record.approver_id:
                record.authorized_by = record.approver_id.name
            elif record.approval_state == 'posted' and record.write_uid:
                record.authorized_by = record.write_uid.name
            else:
                record.authorized_by = record.create_uid.name if record.create_uid else 'System'

    # ============================================================================
    # ONCHANGE METHODS
    # ============================================================================

    @api.onchange('payment_type', 'partner_id', 'amount')
    def _onchange_payment_details(self):
        """Enhanced onchange for real-time field updates and validations"""
        if self.approval_state not in ['draft', 'cancelled']:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Payment details cannot be changed after submission for approval.')
                }
            }

        # Auto-generate voucher number if missing
        if not self.voucher_number:
            self._generate_voucher_number()

    @api.onchange('approval_state')
    def _onchange_approval_state(self):
        """Real-time status bar updates and field state changes"""
        if self.approval_state == 'posted' and self.state != 'posted':
            self.state = 'posted'
        elif self.approval_state == 'cancelled' and self.state != 'cancel':
            self.state = 'cancel'

    @api.onchange('journal_id')
    def _onchange_journal_id_destination_account(self):
        """Set default destination account based on journal"""
        if self.journal_id and self.journal_id.default_account_id:
            self.destination_account_id = self.journal_id.default_account_id.id

    @api.onchange('partner_id')
    def _onchange_partner_id_enhanced(self):
        """Enhanced partner change logic"""
        if self.partner_id:
            # Auto-populate bank details if available
            partner_banks = self.partner_id.bank_ids
            if partner_banks:
                self.partner_bank_id = partner_banks[0].id
            
            # Set destination account for vendor payments
            if self.payment_type == 'outbound' and not self.destination_account_id:
                self.destination_account_id = self.partner_id.property_account_payable_id

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def _amount_in_words(self):
        """Convert payment amount to words"""
        self.ensure_one()
        try:
            # Try to use the built-in Odoo method if available
            if hasattr(self.currency_id, 'amount_to_text'):
                return self.currency_id.amount_to_text(self.amount)
            
            # Fallback to num2words library
            try:
                from num2words import num2words
                amount_text = num2words(self.amount, lang='en', to='currency')
                # Capitalize first letter of each word
                return ' '.join(word.capitalize() for word in amount_text.split())
            except ImportError:
                # Ultimate fallback - manual conversion for common amounts
                return self._manual_amount_to_words()
                
        except Exception as e:
            _logger.warning(f"Error converting amount to words: {e}")
            return f"{self.currency_id.name} {self.amount:,.2f} Only"

    def _manual_amount_to_words(self):
        """Manual amount to words conversion for basic amounts"""
        amount = self.amount
        currency = self.currency_id.name or 'Dollars'
        
        if amount == 0:
            return f"Zero {currency} Only"
        
        # Simple conversion for whole numbers up to thousands
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", 
                "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_hundreds(num):
            result = ""
            if num >= 100:
                result += ones[num // 100] + " Hundred "
                num %= 100
            if num >= 20:
                result += tens[num // 10] + " "
                num %= 10
            elif num >= 10:
                result += teens[num - 10] + " "
                num = 0
            if num > 0:
                result += ones[num] + " "
            return result.strip()
        
        # Split into integer and decimal parts
        integer_part = int(amount)
        decimal_part = int((amount - integer_part) * 100)
        
        result = ""
        if integer_part >= 1000000:
            result += convert_hundreds(integer_part // 1000000) + " Million "
            integer_part %= 1000000
        if integer_part >= 1000:
            result += convert_hundreds(integer_part // 1000) + " Thousand "
            integer_part %= 1000
        if integer_part > 0:
            result += convert_hundreds(integer_part)
        
        if not result:
            result = "Zero"
        
        result += f" {currency}"
        
        if decimal_part > 0:
            result += f" and {decimal_part:02d}/100"
        
        return result.strip() + " Only"

    # ============================================================================
    # WORKFLOW METHODS
    # ============================================================================

    def action_submit_for_review(self):
        """Submit payment for initial review (Stage 1)"""
        self.ensure_one()
        self._check_workflow_permissions('submit')
        
        if self.approval_state != 'draft':
            raise UserError(_("Only draft payments can be submitted for review."))
        
        # Enhanced validation before submission
        self._validate_payment_data()
        
        # Generate voucher number if not already generated
        if not self.voucher_number:
            self._generate_voucher_number()
        
        # Update approval state
        self.approval_state = 'under_review'
        
        self._post_workflow_message('submitted for review')
        self._send_workflow_notification('review')
        
        return self._return_success_message(_('Payment has been submitted for review.'))

    def action_review_payment(self):
        """Review payment and move to next stage (Stage 1 → Stage 2)"""
        self.ensure_one()
        self._check_workflow_permissions('review')
        
        if self.approval_state != 'under_review':
            raise UserError(_("Only payments under review can be reviewed."))
        
        # Set review fields
        self.reviewer_id = self.env.user
        self.reviewer_date = fields.Datetime.now()
        
        # Determine next stage based on payment type
        if self.payment_type == 'outbound':  # Vendor payment
            self.approval_state = 'for_approval'
            next_stage_msg = "sent for approval"
            notification_type = 'approval'
        else:  # Customer receipt - skip to approved
            self.approval_state = 'approved'
            next_stage_msg = "approved and ready for posting"
            notification_type = 'posting'
        
        self._post_workflow_message(f"reviewed and {next_stage_msg}")
        self._send_workflow_notification(notification_type)
        
        return self._return_success_message(_('Payment has been reviewed successfully.'))

    def action_approve_payment(self):
        """Approve payment (Stage 2 → Stage 3 for vendor, Stage 2 → Posted for customer)"""
        self.ensure_one()
        self._check_workflow_permissions('approve')
        
        if self.payment_type == 'outbound' and self.approval_state != 'for_approval':
            raise UserError(_("Only vendor payments waiting for approval can be approved."))
        elif self.payment_type == 'inbound' and self.approval_state != 'under_review':
            raise UserError(_("Only customer receipts under review can be approved."))
        
        # Set approval fields
        self.approver_id = self.env.user
        self.approver_date = fields.Datetime.now()
        
        # Determine next stage based on payment type
        if self.payment_type == 'outbound':  # Vendor payment
            self.approval_state = 'for_authorization'
            next_stage_msg = "sent for authorization"
            notification_type = 'authorization'
        else:  # Customer receipt
            self.approval_state = 'approved'
            next_stage_msg = "approved and ready for posting"
            notification_type = 'posting'
        
        self._post_workflow_message(f"approved and {next_stage_msg}")
        self._send_workflow_notification(notification_type)
        
        return self._return_success_message(_('Payment has been approved successfully.'))

    def action_authorize_payment(self):
        """Authorize vendor payment (Stage 3 → Ready for posting) - Vendor payments only"""
        self.ensure_one()
        self._check_workflow_permissions('authorize')
        
        if self.payment_type != 'outbound':
            raise UserError(_("Authorization stage only applies to vendor payments."))
        
        if self.approval_state != 'for_authorization':
            raise UserError(_("Only vendor payments waiting for authorization can be authorized."))
        
        # Set authorization fields
        self.authorizer_id = self.env.user
        self.authorizer_date = fields.Datetime.now()
        self.approval_state = 'approved'
        
        self._post_workflow_message("authorized and ready for posting")
        self._send_workflow_notification('posting')
        
        return self._return_success_message(_('Payment has been authorized and is ready for posting.'))

    def action_post_payment(self):
        """Post payment after all approvals (Final stage)"""
        self.ensure_one()
        self._check_workflow_permissions('post')
        
        # Allow posting for both 'approved' and 'authorized' states
        if self.approval_state not in ['approved', 'authorized']:
            raise UserError(_("Only approved or authorized payments can be posted."))
        
        # Additional validation before posting
        self._validate_payment_data()
        
        # Auto-set destination account if not specified
        if not self.destination_account_id and self.payment_type == 'outbound':
            self.destination_account_id = self.partner_id.property_account_payable_id
        
        # Set posting fields
        self.actual_approver_id = self.env.user
        
        # Post the payment with error handling
        try:
            self.action_post()
            self.approval_state = 'posted'
            
            self._post_workflow_message("posted")
            self._send_workflow_notification('posted')
            
        except Exception as e:
            # Rollback approval state if posting fails
            self.approval_state = 'approved'
            raise UserError(_("Failed to post payment: %s") % str(e))
        
        return self._return_success_message(_('Payment has been posted successfully.'))

    def action_reject_payment(self):
        """Reject payment and return to draft"""
        self.ensure_one()
        
        if self.approval_state not in ['under_review', 'for_approval', 'for_authorization']:
            raise UserError(_("Only payments in review/approval stages can be rejected."))
        
        # Check user permissions for rejection based on current stage
        self._check_rejection_permissions()
        
        # Clear relevant fields and return to draft
        self._clear_workflow_fields()
        self.approval_state = 'draft'
        
        self._post_workflow_message("rejected and returned to draft for revision")
        
        return self._return_success_message(_('Payment has been rejected and returned to draft.'))

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _generate_voucher_number(self):
        """Generate unique voucher number using sequence"""
        if not self.voucher_number:
            sequence_code = 'payment.voucher' if self.payment_type == 'outbound' else 'receipt.voucher'
            
            # Try to get sequence, create if not exists
            sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
            if not sequence:
                sequence = self._create_voucher_sequence(sequence_code)
            
            self.voucher_number = sequence.next_by_id()

    def _create_voucher_sequence(self, sequence_code):
        """Create voucher sequence if it doesn't exist"""
        sequence_name = 'Payment Voucher' if self.payment_type == 'outbound' else 'Receipt Voucher'
        prefix = 'PV' if self.payment_type == 'outbound' else 'RV'
        
        return self.env['ir.sequence'].create({
            'name': sequence_name,
            'code': sequence_code,
            'prefix': prefix,
            'padding': 5,
            'company_id': self.company_id.id or False,
        })

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

    def _check_workflow_permissions(self, action):
        """Check if user has permission for workflow action"""
        permission_map = {
            'submit': 'account.group_account_user',
            'review': 'account_payment_final.group_payment_voucher_reviewer',
            'approve': 'account_payment_final.group_payment_voucher_approver',
            'authorize': 'account_payment_final.group_payment_voucher_authorizer',
            'post': 'account_payment_final.group_payment_voucher_poster',
        }
        
        required_group = permission_map.get(action)
        if required_group and not self.env.user.has_group(required_group):
            raise AccessError(_("You don't have permission to %s payments.") % action)

    def _check_rejection_permissions(self):
        """Check rejection permissions based on current stage"""
        current_stage = self.approval_state
        
        if current_stage == 'under_review':
            if not self.env.user.has_group('account_payment_final.group_payment_voucher_reviewer'):
                raise AccessError(_("You don't have permission to reject payments at review stage."))
        elif current_stage == 'for_approval':
            if not self.env.user.has_group('account_payment_final.group_payment_voucher_approver'):
                raise AccessError(_("You don't have permission to reject payments at approval stage."))
        elif current_stage == 'for_authorization':
            if not self.env.user.has_group('account_payment_final.group_payment_voucher_authorizer'):
                raise AccessError(_("You don't have permission to reject payments at authorization stage."))

    def _clear_workflow_fields(self):
        """Clear workflow fields when rejecting"""
        current_stage = self.approval_state
        
        if current_stage == 'under_review':
            self.reviewer_id = False
            self.reviewer_date = False
        elif current_stage == 'for_approval':
            self.approver_id = False
            self.approver_date = False
        elif current_stage == 'for_authorization':
            self.authorizer_id = False
            self.authorizer_date = False

    def _post_workflow_message(self, action):
        """Post message to chatter for workflow actions"""
        self.message_post(
            body=f"Payment voucher {self.voucher_number} {action} by {self.env.user.name}",
            subject=f"Payment Voucher {action.title()}"
        )

    def _send_workflow_notification(self, notification_type):
        """Send email notifications for workflow actions"""
        # Implement email notifications based on company settings
        if self.company_id.send_approval_notifications:
            # This would be implemented with email templates
            pass

    def _return_success_message(self, message):
        """Return success message for workflow actions"""
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'message': message,
                'type': 'success',
            }
        }

    # ============================================================================
    # ACTION METHODS
    # ============================================================================

    def action_view_approval_details(self):
        """Show approval details and current status information"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Approval Details - {self.voucher_number or self.name}',
            'res_model': 'account.payment',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('account_payment_final.view_account_payment_form_enhanced').id,
            'target': 'new',
            'context': {
                'default_approval_state': self.approval_state,
                'show_approval_details': True,
            }
        }

    def action_print_osus_voucher(self):
        """Print OSUS branded payment voucher"""
        if self.approval_state == 'draft':
            raise UserError(_("Cannot print voucher for draft payments. Please submit for approval first."))
        
        return self.env.ref('account_payment_final.action_report_payment_voucher_osus_enhanced').report_action(self)

    def action_generate_qr_code(self):
        """Generate QR code for payment verification"""
        self.ensure_one()
        
        if not self.qr_code:
            # Force QR code generation
            self._compute_payment_qr_code()
        
        if self.qr_code:
            return self._return_success_message(_('QR Code generated successfully.'))
        else:
            raise UserError(_('Failed to generate QR Code. Please try again.'))

    def action_view_qr_verification(self):
        """Open QR verification page in browser"""
        self.ensure_one()
        
        if not self.qr_code:
            raise UserError(_('QR Code has not been generated yet. Please generate QR Code first.'))
        
        # Generate verification URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        verification_url = f"{base_url}/payment/verify/{self.id}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': verification_url,
            'target': 'new',
            'name': _('Payment Verification Page')
        }

    def action_cancel(self):
        """Enhanced cancel action with proper validation"""
        for record in self:
            if record.state == 'posted':
                if not self.env.user.has_group('account.group_account_manager'):
                    raise UserError(_("Only account managers can cancel posted payments."))
                
                record.approval_state = 'cancelled'
                record._post_workflow_message("cancelled")
            else:
                record.approval_state = 'cancelled'
        
        return super(AccountPayment, self).action_cancel()

    def action_post(self):
        """Override core action_post to enforce approval workflow"""
        for record in self:
            # For records with approval workflow, enforce approval state check
            if hasattr(record, 'approval_state') and record.approval_state:
                if record.approval_state not in ['approved', 'posted']:
                    raise UserError(_("Only approved or authorized payments can be posted. Current state: %s") % record.approval_state)
        
        return super(AccountPayment, self).action_post()

    def action_draft(self):
        """Enhanced draft action for cancelled payments"""
        for record in self:
            if record.state != 'cancel':
                raise UserError(_("Only cancelled payments can be set back to draft."))
            
            if not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Only account managers can reset payments to draft."))
            
            record.approval_state = 'draft'
            record._post_workflow_message("reset to draft")
        
        self.write({'state': 'draft'})

    # ============================================================================
    # OVERRIDE METHODS
    # ============================================================================

    @api.model
    def create(self, vals):
        """Enhanced create method with voucher number generation"""
        # Generate voucher number before record creation
        if not vals.get('voucher_number'):
            payment_type = vals.get('payment_type', 'outbound')
            sequence_code = 'payment.voucher' if payment_type == 'outbound' else 'receipt.voucher'
            
            sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
            if not sequence:
                sequence_name = 'Payment Voucher' if payment_type == 'outbound' else 'Receipt Voucher'
                prefix = 'PV' if payment_type == 'outbound' else 'RV'
                sequence = self.env['ir.sequence'].create({
                    'name': sequence_name,
                    'code': sequence_code,
                    'prefix': prefix,
                    'padding': 5,
                    'company_id': vals.get('company_id', False),
                })
            vals['voucher_number'] = sequence.next_by_id()

        payment = super(AccountPayment, self).create(vals)
        
        # Log the creation
        if vals.get('remarks'):
            payment._post_workflow_message(f"created with remarks: {vals['remarks']}")
        else:
            payment._post_workflow_message("created")
            
        return payment

    def write(self, vals):
        """Enhanced write method with real-time state management and audit tracking"""
        # Prevent modification of critical fields when not in draft
        restricted_fields = ['partner_id', 'amount', 'currency_id', 'payment_type']
        if any(field in vals for field in restricted_fields):
            for record in self:
                if record.approval_state not in ['draft', 'cancelled']:
                    raise UserError(_("Cannot modify payment details after submission for approval."))

        # Track state changes for audit
        for record in self:
            if vals.get('approval_state') and vals['approval_state'] != record.approval_state:
                old_state = record.approval_state
                new_state = vals['approval_state']
                record._post_workflow_message(f"state changed from {old_state} to {new_state}")

            # Handle standard Odoo posting
            if vals.get('state') == 'posted' and record.state != 'posted':
                if record.approval_state not in ['approved', 'posted']:
                    vals['approval_state'] = 'posted'
                    vals['actual_approver_id'] = self.env.user.id
                    if not record.approver_id:
                        vals['approver_id'] = self.env.user.id
                        vals['approver_date'] = fields.Datetime.now()

        result = super(AccountPayment, self).write(vals)

        # Trigger QR code regeneration if relevant fields changed
        if any(field in vals for field in ['partner_id', 'amount', 'approval_state', 'qr_in_report']):
            self._compute_payment_qr_code()

        return result

    @api.constrains('amount', 'partner_id', 'approval_state')
    def _check_payment_requirements(self):
        """Enhanced validation constraints for payment requirements"""
        for record in self:
            if record.approval_state != 'draft':
                record._validate_payment_data()

    def unlink(self):
        """Enhanced unlink method with proper validation"""
        for record in self:
            if record.approval_state not in ['draft', 'cancelled']:
                raise UserError(_("You can only delete draft or cancelled payments."))
            if record.state == 'posted':
                raise UserError(_("You cannot delete posted payments."))
        
        return super(AccountPayment, self).unlink()

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def _get_voucher_data(self):
        """Get formatted data for voucher printing"""
        self.ensure_one()
        
        # Format amount in words (if needed for check printing)
        amount_in_words = ""
        try:
            from num2words import num2words
            amount_in_words = num2words(self.amount, lang='en').title()
        except ImportError:
            amount_in_words = f"{self.currency_id.name} {self.amount:,.2f}"

        return {
            'voucher_type': 'Payment Voucher' if self.payment_type == 'outbound' else 'Receipt Voucher',
            'amount_in_words': amount_in_words,
            'currency_symbol': self.currency_id.symbol,
            'formatted_date': self.date.strftime('%d %B %Y') if self.date else '',
            'company_logo_url': self.company_id.logo_web if self.company_id.logo_web else '',
            'is_posted': self.approval_state == 'posted',
            'approval_date': self.write_date.strftime('%d/%m/%Y %H:%M') if self.write_date and self.approval_state == 'posted' else '',
            'voucher_number': self.voucher_number,
            'approval_state': self.approval_state,
        }

    @api.model
    def get_osus_branding_data(self):
        """Get OSUS branding data for reports"""
        return {
            'primary_color': '#800020',
            'secondary_color': '#ffd700',
            'website': 'www.osusproperties.com',
            'logo_url': 'https://osusproperties.com/wp-content/uploads/2025/02/OSUS-logotype-2.png'
        }

    @api.model
    def get_approval_statistics(self):
        """Get approval workflow statistics for dashboard"""
        domain = [('payment_type', 'in', ['outbound', 'inbound'])]
        
        stats = {}
        for state in ['draft', 'under_review', 'for_approval', 'for_authorization', 'approved', 'posted', 'cancelled']:
            stats[state] = self.search_count(domain + [('approval_state', '=', state)])
        
        return stats


class AccountPaymentRegister(models.TransientModel):
    """Enhanced payment registration wizard"""
    _inherit = 'account.payment.register'

    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks for the payment voucher"
    )

    def _create_payment_vals_from_wizard(self, batch_result):
        """Override to include remarks in payment creation"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        if self.remarks:
            payment_vals['remarks'] = self.remarks
            
        return payment_vals