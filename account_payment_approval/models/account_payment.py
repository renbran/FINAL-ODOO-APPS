# -*- coding: utf-8 -*-
#############################################################################
#
#    Enhanced Payment Voucher System - OSUS
#    Additional methods for enhanced reporting functionality
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


class AccountPaymentEnhanced(models.Model):
    """Enhanced Payment with additional report methods"""
    _inherit = "account.payment"
    
    # Add computed fields for smart buttons
    signature_count = fields.Integer(string='Signature Count', compute='_compute_signature_count')
    verification_count = fields.Integer(string='Verification Count', compute='_compute_verification_count')
    
    @api.depends('voucher_state')
    def _compute_signature_count(self):
        """Compute number of digital signatures"""
        for record in self:
            signatures = self.env['payment.voucher.signature'].search_count([
                ('payment_id', '=', record.id)
            ])
            record.signature_count = signatures
    
    @api.depends('verification_token')
    def _compute_verification_count(self):
        """Compute number of verifications performed"""
        for record in self:
            if record.verification_token:
                verification = self.env['payment.voucher.qr.verification'].search([
                    ('payment_id', '=', record.id)
                ], limit=1)
                record.verification_count = verification.verification_count if verification else 0
            else:
                record.verification_count = 0
    
    def action_view_signatures(self):
        """Smart button action to view signatures"""
        self.ensure_one()
        signatures = self.env['payment.voucher.signature'].search([
            ('payment_id', '=', self.id)
        ])
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Digital Signatures - {self.voucher_number or self.name}',
            'res_model': 'payment.voucher.signature',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', signatures.ids)],
            'context': {'default_payment_id': self.id},
            'target': 'current',
        }
    
    def action_view_verifications(self):
        """Smart button action to view verifications"""
        self.ensure_one()
        verification = self.env['payment.voucher.qr.verification'].search([
            ('payment_id', '=', self.id)
        ], limit=1)
        
        if not verification:
            raise UserError(_("No verification record found for this payment."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'QR Verifications - {self.voucher_number or self.name}',
            'res_model': 'payment.voucher.qr.verification',
            'view_mode': 'form',
            'res_id': verification.id,
            'target': 'current',
        }
    
    def action_send_report_email(self):
        """Send payment report via email"""
        self.ensure_one()
        
        # Get email template
        template = self.env.ref('account_payment_approval.mail_template_report_generated')
        
        # Prepare context with timestamp
        ctx = self.env.context.copy()
        ctx['timestamp'] = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Send email
        template.with_context(ctx).send_mail(self.id, force_send=True)
        
        # Show notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Email Sent'),
                'message': _('Payment report has been sent via email.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_generate_qr_verification_page(self):
        """Generate a standalone QR verification page"""
        self.ensure_one()
        
        if not self.verification_token:
            raise UserError(_("This payment does not have a verification token. Please save the payment first."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/payment/verify/{self.verification_token}',
            'target': 'new',
        }
    
    def action_print_multiple_reports(self):
        """Action to print multiple report types"""
        self.ensure_one()
        
        wizard = self.env['payment.report.wizard'].create({
            'payment_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Reports',
            'res_model': 'payment.report.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def get_related_document_info(self):
        """Get information about related documents (invoices/bills)"""
        self.ensure_one()
        
        result = {
            'references': 'N/A',
            'count': 0,
            'total_amount': 0.0,
            'documents': []
        }
        
        # Check for reconciled invoices
        if self.reconciled_invoice_ids:
            invoices = self.reconciled_invoice_ids
            result['count'] = len(invoices)
            result['total_amount'] = sum(invoices.mapped('amount_total'))
            
            # Build reference string
            references = []
            for invoice in invoices:
                ref = invoice.name or invoice.ref or 'Draft'
                if invoice.invoice_date:
                    ref += f" ({invoice.invoice_date.strftime('%d/%m/%Y')})"
                references.append(ref)
            
            result['references'] = ', '.join(references)
            result['documents'] = invoices
        
        # If no reconciled invoices, check for related document fields
        elif self.related_document_number:
            result['references'] = f"{self.related_document_type or 'Document'} - {self.related_document_number}"
            result['count'] = 1
            
        return result
    
    def get_payment_summary(self):
        """Get payment summary information for reports"""
        self.ensure_one()
        
        summary = {
            'total_invoice_amount': 0.0,
            'payment_amount': self.amount,
            'currency': self.currency_id,
            'is_full_payment': False,
            'remaining_amount': 0.0,
            'invoices': []
        }
        
        if self.reconciled_invoice_ids:
            invoices = self.reconciled_invoice_ids
            total_invoice_amount = sum(invoices.mapped('amount_total'))
            total_paid = sum(invoices.mapped('amount_total_in_currency_signed'))
            
            summary.update({
                'total_invoice_amount': abs(total_invoice_amount),
                'is_full_payment': abs(total_paid) >= abs(total_invoice_amount),
                'remaining_amount': abs(total_invoice_amount) - abs(total_paid),
                'invoices': invoices
            })
        
        return summary
    
    def get_voucher_description(self):
        """Get a descriptive text for the voucher purpose"""
        self.ensure_one()
        
        if self.payment_type == 'outbound':
            if self.reconciled_invoice_ids:
                invoice_count = len(self.reconciled_invoice_ids)
                if invoice_count == 1:
                    return f"Payment for Vendor Bill {self.reconciled_invoice_ids[0].name}"
                else:
                    return f"Payment for {invoice_count} Vendor Bills"
            else:
                return "Vendor Payment"
        else:  # inbound
            if self.reconciled_invoice_ids:
                invoice_count = len(self.reconciled_invoice_ids)
                if invoice_count == 1:
                    return f"Receipt for Customer Invoice {self.reconciled_invoice_ids[0].name}"
                else:
                    return f"Receipt for {invoice_count} Customer Invoices"
            else:
                return "Customer Receipt"
    
    def _get_amount_in_words(self):
        """Convert amount to words with currency"""
        self.ensure_one()
        
        if not self.amount or not self.currency_id:
            return "Zero"
            
        try:
            # Use the existing amount_in_words field if available
            if hasattr(self, 'amount_in_words') and self.amount_in_words:
                return self.amount_in_words
                
            # Fallback to manual conversion
            currency_name = self.currency_id.name or 'USD'
            amount_words = num2words(self.amount, to='currency', currency=currency_name)
            return amount_words.title()
        except Exception as e:
            _logger.warning(f"Error converting amount to words: {e}")
            return f"{self.currency_id.symbol or ''} {self.amount:,.2f}"
    
    def get_workflow_stage_info(self):
        """Get current workflow stage information"""
        self.ensure_one()
        
        stage_info = {
            'current_stage': self.voucher_state,
            'display_name': self.voucher_state.title().replace('_', ' '),
            'progress_percentage': self.workflow_progress if hasattr(self, 'workflow_progress') else 0,
            'next_action': '',
            'completed_stages': [],
            'pending_stages': []
        }
        
        # Define workflow stages
        if hasattr(self, 'voucher_type') and self.voucher_type == 'payment':
            stages = ['draft', 'submitted', 'under_review', 'approved', 'authorized', 'posted']
        else:
            stages = ['draft', 'submitted', 'under_review', 'posted']
        
        # Find current stage index
        current_state = self.voucher_state if hasattr(self, 'voucher_state') else self.state
        try:
            current_index = stages.index(current_state)
            stage_info['completed_stages'] = stages[:current_index + 1]
            stage_info['pending_stages'] = stages[current_index + 1:]
        except ValueError:
            # Handle special states like rejected, cancelled
            if current_state in ['rejected', 'cancelled', 'cancel']:
                stage_info['completed_stages'] = []
                stage_info['pending_stages'] = stages
        
        # Determine next action
        if current_state == 'draft':
            stage_info['next_action'] = 'Submit for approval'
        elif current_state == 'submitted':
            stage_info['next_action'] = 'Waiting for review'
        elif current_state == 'under_review':
            if hasattr(self, 'voucher_type') and self.voucher_type == 'payment':
                stage_info['next_action'] = 'Waiting for approval'
            else:
                stage_info['next_action'] = 'Ready for posting'
        elif current_state == 'approved':
            stage_info['next_action'] = 'Waiting for authorization'
        elif current_state == 'authorized':
            stage_info['next_action'] = 'Ready for posting'
        elif current_state == 'posted':
            stage_info['next_action'] = 'Completed'
        else:
            stage_info['next_action'] = 'No action required'
        
        return stage_info
    
    def get_signature_summary(self):
        """Get summary of all signatures for reports"""
        self.ensure_one()
        
        signatures = []
        
        # Creator signature
        signatures.append({
            'role': 'Creator',
            'name': getattr(self, 'creator_name', None) or self.create_uid.name,
            'signed': bool(getattr(self, 'creator_signature', False)),
            'date': getattr(self, 'creator_signature_date', None),
            'required': True
        })
        
        # Reviewer signature
        signatures.append({
            'role': 'Reviewer',
            'name': getattr(self, 'reviewer_name', None),
            'signed': bool(getattr(self, 'reviewer_signature', False)),
            'date': getattr(self, 'reviewer_signature_date', None),
            'required': True
        })
        
        # Approver signature (only for payment vouchers)
        if hasattr(self, 'voucher_type') and self.voucher_type == 'payment':
            signatures.append({
                'role': 'Approver',
                'name': getattr(self, 'approver_name', None),
                'signed': bool(getattr(self, 'approver_signature', False)),
                'date': getattr(self, 'approver_signature_date', None),
                'required': True
            })
        
        # Authorizer signature
        signatures.append({
            'role': 'Authorizer',
            'name': getattr(self, 'authorizer_name', None),
            'signed': bool(getattr(self, 'authorizer_signature', False)),
            'date': getattr(self, 'authorizer_signature_date', None),
            'required': True
        })
        
        # Receiver signature
        signatures.append({
            'role': 'Receiver',
            'name': self.partner_id.name,
            'signed': bool(getattr(self, 'receiver_signature', False)),
            'date': getattr(self, 'receiver_signature_date', None),
            'required': False
        })
        
        return signatures
    
    def get_verification_info(self):
        """Get verification information for QR codes and reports"""
        self.ensure_one()
        
        info = {
            'token': getattr(self, 'verification_token', None),
            'url': getattr(self, 'verification_url', None),
            'qr_code': getattr(self, 'qr_code', None),
            'is_verifiable': bool(getattr(self, 'verification_token', None)),
            'verification_instructions': 'Scan QR code or visit verification URL to authenticate this document'
        }
        
        return info
    
    def get_company_info(self):
        """Get formatted company information for reports"""
        self.ensure_one()
        
        company = self.company_id
        info = {
            'name': company.name,
            'street': company.street or '',
            'street2': company.street2 or '',
            'city': company.city or '',
            'state': company.state_id.name if company.state_id else '',
            'zip': company.zip or '',
            'country': company.country_id.name if company.country_id else '',
            'phone': company.phone or '',
            'email': company.email or '',
            'website': company.website or '',
            'vat': company.vat or '',
            'formatted_address': self._format_address(company)
        }
        
        return info
    
    def _format_address(self, partner):
        """Format partner address for display"""
        address_parts = []
        
        if partner.street:
            address_parts.append(partner.street)
        if partner.street2:
            address_parts.append(partner.street2)
        
        city_line = []
        if partner.city:
            city_line.append(partner.city)
        if partner.state_id:
            city_line.append(partner.state_id.name)
        if partner.zip:
            city_line.append(partner.zip)
        
        if city_line:
            address_parts.append(', '.join(city_line))
        
        if partner.country_id:
            address_parts.append(partner.country_id.name)
        
        return '\n'.join(address_parts)
    
    def get_partner_info(self):
        """Get formatted partner information"""
        self.ensure_one()
        
        partner = self.partner_id
        info = {
            'name': partner.name,
            'street': partner.street or '',
            'street2': partner.street2 or '',
            'city': partner.city or '',
            'state': partner.state_id.name if partner.state_id else '',
            'zip': partner.zip or '',
            'country': partner.country_id.name if partner.country_id else '',
            'phone': partner.phone or '',
            'mobile': partner.mobile or '',
            'email': partner.email or '',
            'vat': partner.vat or '',
            'formatted_address': self._format_address(partner),
            'is_company': partner.is_company
        }
        
        return info
    
    def get_payment_method_info(self):
        """Get detailed payment method information"""
        self.ensure_one()
        
        info = {
            'name': self.payment_method_id.name if self.payment_method_id else '',
            'code': self.payment_method_id.code if self.payment_method_id else '',
            'type': self.payment_method_id.payment_type if self.payment_method_id else '',
            'journal': self.journal_id.name if self.journal_id else '',
            'journal_type': self.journal_id.type if self.journal_id else '',
            'bank_account': ''
        }
        
        # Add bank account info if available
        if self.journal_id and self.journal_id.bank_account_id:
            bank_acc = self.journal_id.bank_account_id
            info['bank_account'] = f"{bank_acc.acc_number} ({bank_acc.bank_id.name})"
        
        return info
    
    def get_audit_trail(self):
        """Get audit trail information for the payment"""
        self.ensure_one()
        
        trail = []
        
        # Creation
        trail.append({
            'action': 'Created',
            'user': self.create_uid.name,
            'date': self.create_date,
            'details': f'Payment voucher created by {self.create_uid.name}'
        })
        
        # Submission
        if hasattr(self, 'submitted_date') and self.submitted_date:
            trail.append({
                'action': 'Submitted',
                'user': self.create_uid.name,
                'date': self.submitted_date,
                'details': 'Submitted for approval workflow'
            })
        
        # Review
        if hasattr(self, 'reviewed_date') and self.reviewed_date and hasattr(self, 'reviewer_id') and self.reviewer_id:
            trail.append({
                'action': 'Reviewed',
                'user': self.reviewer_id.name,
                'date': self.reviewed_date,
                'details': f'Reviewed by {self.reviewer_id.name}'
            })
        
        # Approval
        if hasattr(self, 'approved_date') and self.approved_date and hasattr(self, 'approver_id') and self.approver_id:
            trail.append({
                'action': 'Approved',
                'user': self.approver_id.name,
                'date': self.approved_date,
                'details': f'Approved by {self.approver_id.name}'
            })
        
        # Authorization
        if hasattr(self, 'authorized_date') and self.authorized_date and hasattr(self, 'authorizer_id') and self.authorizer_id:
            trail.append({
                'action': 'Authorized',
                'user': self.authorizer_id.name,
                'date': self.authorized_date,
                'details': f'Authorized by {self.authorizer_id.name}'
            })
        
        # Posting
        if self.state == 'posted':
            trail.append({
                'action': 'Posted',
                'user': self.write_uid.name if self.write_uid else 'System',
                'date': self.write_date,
                'details': 'Payment posted to accounting'
            })
        
        # Rejection
        if hasattr(self, 'rejected_date') and self.rejected_date:
            trail.append({
                'action': 'Rejected',
                'user': self.write_uid.name if self.write_uid else 'System',
                'date': self.rejected_date,
                'details': f'Rejected: {getattr(self, "rejection_reason", None) or "No reason provided"}'
            })
        
        return trail
    
    @api.model
    def get_report_options(self):
        """Get available report options and templates"""
        return {
            'templates': [
                {
                    'id': 'enhanced',
                    'name': 'Enhanced OSUS Template',
                    'description': 'Professional template with digital signatures and QR verification'
                },
                {
                    'id': 'compact',
                    'name': 'Compact Business Template',
                    'description': 'Space-efficient template for quick printing'
                },
                {
                    'id': 'detailed',
                    'name': 'Detailed Audit Template',
                    'description': 'Comprehensive template with full audit trail'
                }
            ],
            'formats': ['PDF', 'HTML'],
            'features': [
                'Digital Signatures',
                'QR Code Verification',
                'Multi-language Support',
                'Custom Branding',
                'Audit Trail',
                'Mobile Responsive'
            ]
        }


class PaymentVoucherSignatureEnhanced(models.Model):
    """Enhanced Digital Signature Model"""
    _inherit = 'payment.voucher.signature'
    
    def get_signature_details(self):
        """Get detailed signature information for reports"""
        self.ensure_one()
        
        return {
            'role': self.signature_type.title(),
            'user_name': self.user_id.name,
            'signature_date': self.signature_date,
            'formatted_date': self.signature_date.strftime('%B %d, %Y at %I:%M %p') if self.signature_date else '',
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'has_image': bool(self.signature_data),
            'company': self.company_id.name
        }


class PaymentVoucherQRVerificationEnhanced(models.Model):
    """Enhanced QR Verification Model"""
    _inherit = 'payment.voucher.qr.verification'
    
    def get_verification_stats(self):
        """Get verification statistics"""
        self.ensure_one()
        
        return {
            'verification_count': self.verification_count,
            'last_verified': self.last_verified_date,
            'last_verified_formatted': self.last_verified_date.strftime('%B %d, %Y at %I:%M %p') if self.last_verified_date else 'Never',
            'last_ip': self.last_verified_ip or 'Unknown',
            'is_active': self.is_active,
            'token': self.token,
            'created_date': self.create_date,
            'payment_reference': self.payment_id.voucher_number if hasattr(self.payment_id, 'voucher_number') else self.payment_id.name
        }