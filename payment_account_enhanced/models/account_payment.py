from odoo import models, fields, api, _
from odoo.exceptions import UserError
import qrcode
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

def generate_qr_code_payment(value):
    """Generate QR code for payment data"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(value)
        qr.make(fit=True)
        img = qr.make_image()
        stream = BytesIO()
        img.save(stream, format="PNG")
        qr_img = base64.b64encode(stream.getvalue())
        return qr_img
    except Exception as e:
        _logger.error(f"Error generating QR code: {e}")
        return False

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    # QR Code fields
    qr_code = fields.Binary(
        string="Payment QR Code", 
        compute='_generate_payment_qr_code',
        help="QR code containing payment verification URL"
    )
    qr_in_report = fields.Boolean(
        string='Display QR Code in Report?', 
        default=True,
        help="Whether to display QR code in payment voucher report"
    )
    
    # Enhanced fields for OSUS voucher system
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for this payment voucher"
    )
    
    # Enhanced signatory fields
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewed By',
        help="User who reviewed the payment before approval"
    )
    
    reviewer_date = fields.Datetime(
        string='Review Date',
        help="Date when the payment was reviewed"
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Final Approver',
        help="User who gave final approval for the payment"
    )
    
    approver_date = fields.Datetime(
        string='Approval Date',
        help="Date when the payment was finally approved"
    )
    
    authorized_by = fields.Char(
        string='Authorized By',
        compute='_compute_authorized_by',
        store=True,
        help="Name of the person who approved and posted the payment"
    )
    
    actual_approver_id = fields.Many2one(
        'res.users',
        string='Approved By User',
        help="User who actually approved and posted the payment",
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
    
    # Computed voucher number that shows even in draft state
    voucher_number = fields.Char(
        string='Voucher Number',
        compute='_compute_voucher_number',
        store=True,
        help="Voucher number that displays even in draft state"
    )
    
    @api.depends('name', 'payment_type', 'partner_id', 'amount', 'currency_id')
    def _compute_display_name(self):
        """Compute enhanced display name for vouchers"""
        for record in self:
            if record.name and record.partner_id:
                payment_type_label = 'Payment' if record.payment_type == 'outbound' else 'Receipt'
                record.display_name = f"{payment_type_label} Voucher {record.name} - {record.partner_id.name}"
            else:
                record.display_name = record.name or 'New Payment'
    
    @api.depends('name', 'state', 'payment_type')
    def _compute_voucher_number(self):
        """Compute voucher number that shows even in draft state"""
        for record in self:
            if record.name and record.name != '/':
                # Use existing name if available
                record.voucher_number = record.name
            else:
                # Generate temporary number for draft payments
                payment_type_prefix = 'PV' if record.payment_type == 'outbound' else 'RV'
                if record._origin.id:
                    # Use the record's database ID if available
                    record.voucher_number = f"DRAFT-{payment_type_prefix}-{record._origin.id:06d}"
                else:
                    # Fallback for new records
                    record.voucher_number = f"NEW-{payment_type_prefix}"
    
    @api.depends('name', 'amount', 'partner_id', 'date', 'state')
    def _generate_payment_qr_code(self):
        """Generate QR code for payment voucher verification"""
        for record in self:
            if record.qr_in_report:
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
Status: {record.state.upper()}
Company: {record.company_id.name}
Verify at: {base_url}/payment/qr-guide"""
                    
                    # Generate the QR code image
                    record.qr_code = generate_qr_code_payment(qr_data)
                except Exception as e:
                    _logger.error(f"Error generating QR code for payment {record.name or 'Draft'}: {e}")
                    record.qr_code = False
            else:
                record.qr_code = False
    
    def action_send_for_review(self):
        """Send payment for review"""
        if self.state != 'draft':
            raise UserError(_("Only draft payments can be sent for review."))
        
        # Here you can add logic to notify reviewers
        # For now, we'll just log it
        _logger.info(f"Payment {self.name} sent for review")
        return True
    
    def action_review_payment(self):
        """Mark payment as reviewed"""
        if not self.reviewer_id:
            self.reviewer_id = self.env.user
            self.reviewer_date = fields.Datetime.now()
        
        # Here you can add logic to notify approvers
        _logger.info(f"Payment {self.name} reviewed by {self.env.user.name}")
        return True
    
    def action_approve_payment(self):
        """Mark payment as approved and set approver"""
        if not self.approver_id:
            self.approver_id = self.env.user
            self.approver_date = fields.Datetime.now()
        
        _logger.info(f"Payment {self.name} approved by {self.env.user.name}")
        return True
    
    def action_review_payment(self):
        """Mark payment as reviewed"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft payments can be reviewed."))
        
        self.reviewer_id = self.env.user
        self.reviewer_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Payment has been marked as reviewed.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_approve_payment(self):
        """Mark payment as approved by final approver"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft payments can be approved."))
        
        self.approver_id = self.env.user
        self.approver_date = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Payment has been approved and is ready for posting.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.depends('state', 'actual_approver_id', 'write_uid', 'write_date')
    def _compute_authorized_by(self):
        """Compute authorization field showing who approved and posted the payment"""
        for record in self:
            if record.actual_approver_id:
                # Show the actual approver who approved and posted the entry
                record.authorized_by = record.actual_approver_id.name
            elif record.state == 'posted' and record.write_uid:
                # If posted but no specific approver, show who posted it
                record.authorized_by = record.write_uid.name
            else:
                # For draft or other states, show who initiated
                record.authorized_by = record.create_uid.name if record.create_uid else 'System'
    
    @api.model
    def create(self, vals):
        """Enhanced create method with validation"""
        # Add any custom validation here if needed
        if 'remarks' in vals and vals['remarks']:
            # Log the creation with remarks for audit trail
            self.env['mail.message'].create({
                'body': f"Payment voucher created with remarks: {vals['remarks']}",
                'model': 'account.payment',
                'res_id': 0,  # Will be updated after creation
                'message_type': 'comment',
            })
        
        return super(AccountPayment, self).create(vals)
    
    def write(self, vals):
        """Override write to track the approver when payment is posted"""
        # Track state changes for audit
        for record in self:
            if vals.get('state') == 'posted' and record.state != 'posted':
                # Payment is being posted, track who is posting it
                if not record.actual_approver_id:
                    vals['actual_approver_id'] = self.env.user.id
                
                # Log the approval action
                record.message_post(
                    body=f"Payment voucher approved and posted by {self.env.user.name}",
                    subject="Payment Voucher Approved"
                )
        
        return super(AccountPayment, self).write(vals)
    
    def action_print_osus_voucher(self):
        """Print OSUS branded payment voucher"""
        if self.state == 'draft':
            raise UserError(_("Cannot print voucher for draft payments. Please post the payment first."))
        
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher_osus').report_action(self)
    
    def action_print_standard_voucher(self):
        """Print standard payment voucher (fallback)"""
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher').report_action(self)
    
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
    
    def _get_voucher_data(self):
        """Get formatted data for voucher printing"""
        self.ensure_one()
        
        # Format amount in words (if needed for check printing)
        amount_in_words = ""
        try:
            from num2words import num2words
            amount_in_words = num2words(self.amount, lang='en').title()
        except ImportError:
            # Fallback if num2words is not available
            amount_in_words = "Amount in words not available"
        
        return {
            'voucher_type': 'Payment Voucher' if self.payment_type == 'outbound' else 'Receipt Voucher',
            'amount_in_words': amount_in_words,
            'currency_symbol': self.currency_id.symbol,
            'formatted_date': self.date.strftime('%d %B %Y') if self.date else '',
            'company_logo_url': self.company_id.logo_web if self.company_id.logo_web else '',
            'is_posted': self.state == 'posted',
            'approval_date': self.write_date.strftime('%d/%m/%Y %H:%M') if self.write_date and self.state == 'posted' else '',
        }
    
    def action_validate_and_post(self):
        """Enhanced validation and posting with OSUS specific checks"""
        for record in self:
            # OSUS specific validations
            if not record.partner_id:
                raise UserError(_("Partner is required for OSUS payment vouchers."))
            
            if record.amount <= 0:
                raise UserError(_("Payment amount must be greater than zero."))
            
            # Check if user has approval rights for large amounts
            if record.amount > 10000 and not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Payments above AED 10,000 require manager approval."))
        
        # Call standard posting method
        return super(AccountPayment, self).action_post()
    
    def action_cancel(self):
        """Enhanced cancel action with proper validation"""
        for record in self:
            if record.state == 'posted':
                # Check if user has permission to cancel posted payments
                if not self.env.user.has_group('account.group_account_manager'):
                    raise UserError(_("Only account managers can cancel posted payments."))
                
                # Log the cancellation
                record.message_post(
                    body=f"Payment voucher cancelled by {self.env.user.name}",
                    subject="Payment Voucher Cancelled"
                )
        
        # Call standard cancel method
        return super(AccountPayment, self).action_cancel()
    
    def action_draft(self):
        """Enhanced draft action for cancelled payments"""
        for record in self:
            if record.state != 'cancel':
                raise UserError(_("Only cancelled payments can be set back to draft."))
            
            if not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Only account managers can reset payments to draft."))
            
            # Log the reset action
            record.message_post(
                body=f"Payment voucher reset to draft by {self.env.user.name}",
                subject="Payment Voucher Reset"
            )
        
        # Reset state to draft manually since parent method doesn't exist
        self.write({'state': 'draft'})
    
    @api.model
    def get_osus_branding_data(self):
        """Get OSUS branding data for reports"""
        return {
            'primary_color': '#8B1538',
            'secondary_color': '#D4AF37',
            'company_tagline': 'Luxury Real Estate Excellence',
            'website': 'www.osusproperties.com',
            'logo_url': 'https://osusproperties.com/wp-content/uploads/2025/02/OSUS-logotype-2.png'
        }


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


class ResCompany(models.Model):
    """Enhanced company model for OSUS branding"""
    _inherit = 'res.company'
    
    voucher_footer_message = fields.Text(
        string='Voucher Footer Message',
        default='Thank you for your business',
        help="Custom message to display in payment voucher footer"
    )
    
    voucher_terms = fields.Text(
        string='Voucher Terms',
        default='This is a computer-generated document. No physical signature or stamp required for system verification.',
        help="Terms and conditions to display in payment voucher"
    )
    
    use_osus_branding = fields.Boolean(
        string='Use OSUS Branding',
        default=True,
        help="Apply OSUS brand guidelines to reports and vouchers"
    )