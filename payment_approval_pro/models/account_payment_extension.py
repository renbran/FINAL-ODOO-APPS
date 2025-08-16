# -*- coding: utf-8 -*-
"""
Account Payment Extension for Enhanced Reporting
Extends standard account.payment with enhanced report functionality
"""

import base64
import io
import qrcode
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    """
    Extends account.payment with enhanced reporting capabilities
    for the Payment Approval Pro module
    """
    _inherit = 'account.payment'

    # Enhanced QR Code for payments
    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code',
        store=False,
        help="QR code for payment verification"
    )
    
    qr_verification_token = fields.Char(
        string='QR Verification Token',
        copy=False,
        help="Unique token for QR code verification"
    )

    @api.depends('name', 'amount', 'partner_id', 'date')
    def _compute_qr_code(self):
        """Generate QR code for payment verification"""
        for record in self:
            if record.name and record.amount and record.partner_id:
                try:
                    # Generate verification token if not exists
                    if not record.qr_verification_token:
                        record.qr_verification_token = record._generate_verification_token()
                    
                    qr_data = record._get_qr_code_data()
                    
                    # Generate QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    # Create QR code image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convert to binary
                    buffer = io.BytesIO()
                    qr_img.save(buffer, format='PNG')
                    record.qr_code = base64.b64encode(buffer.getvalue())
                    
                except Exception as e:
                    _logger.warning(f"Failed to generate QR code for payment {record.name}: {e}")
                    record.qr_code = False
            else:
                record.qr_code = False

    def _generate_verification_token(self):
        """Generate a unique verification token"""
        import secrets
        return secrets.token_urlsafe(32)

    def _get_qr_code_data(self):
        """Get data for QR code generation"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        verification_url = f"{base_url}/payment/verify/{self.qr_verification_token or 'invalid'}"
        
        qr_data = f"""OSUS Payment Verification
Payment: {self.name}
Amount: {self.currency_id.symbol}{self.amount:,.2f}
Partner: {self.partner_id.name}
Date: {self.date}
Verify: {verification_url}"""
        
        return qr_data

    # ================================
    # ENHANCED REPORT ACTIONS
    # ================================
    
    def action_print_enhanced_voucher(self):
        """Print enhanced payment voucher report with comprehensive details"""
        self.ensure_one()
        return self.env.ref('payment_approval_pro.action_report_payment_voucher_enhanced').report_action(self)
    
    def action_print_compact_voucher(self):
        """Print compact payment voucher report for quick reference"""
        self.ensure_one()
        return self.env.ref('payment_approval_pro.action_report_payment_voucher_compact').report_action(self)
    
    def action_print_professional_summary(self):
        """Print professional payment summary report"""
        self.ensure_one()
        return self.env.ref('payment_approval_pro.action_report_payment_summary_professional').report_action(self)
    
    def action_print_multiple_reports(self):
        """Print multiple payment reports for batch processing"""
        if len(self) == 1:
            # Single record - show enhanced report
            return self.action_print_enhanced_voucher()
        else:
            # Multiple records - show summary table
            return self.env.ref('payment_approval_pro.action_report_multiple_payments').report_action(self)

    # ================================
    # REPORT DATA METHODS
    # ================================
    
    def get_enhanced_report_data(self):
        """Get comprehensive data for enhanced voucher report"""
        self.ensure_one()
        
        # Get move lines for itemization
        move_lines = []
        if self.move_id:
            move_lines = self.move_id.line_ids.filtered(
                lambda l: l.account_id.user_type_id.type in ['receivable', 'payable']
            )
        
        # Get related invoices
        related_invoices = []
        if hasattr(self, 'reconciled_invoice_ids'):
            related_invoices = self.reconciled_invoice_ids
        
        return {
            'payment': self,
            'company': self.company_id,
            'qr_code': self.qr_code,
            'move_lines': move_lines,
            'related_invoices': related_invoices,
            'amount_words': self.currency_id.amount_to_text(self.amount),
            'verification_token': self.qr_verification_token,
        }

    def get_professional_summary_data(self):
        """Get data for professional summary report"""
        self.ensure_one()
        
        return {
            'payment': self,
            'company': self.company_id,
            'stats': {
                'total_amount': self.amount,
                'transaction_type': 'RECEIVED' if self.payment_type == 'inbound' else 'PAID',
                'current_status': self.state.upper(),
                'currency': self.currency_id.name,
            },
            'details': {
                'reference': self.name,
                'partner': self.partner_id.name,
                'method': self.journal_id.name,
                'date': self.date,
                'created_by': self.create_uid.name,
                'created_date': self.create_date,
            }
        }

    @api.model
    def get_multiple_payments_data(self, payment_ids):
        """Get data for multiple payments report"""
        payments = self.browse(payment_ids)
        
        total_amount = sum(payments.mapped('amount'))
        inbound_total = sum(payments.filtered(lambda p: p.payment_type == 'inbound').mapped('amount'))
        outbound_total = sum(payments.filtered(lambda p: p.payment_type == 'outbound').mapped('amount'))
        
        return {
            'payments': payments,
            'totals': {
                'total_amount': total_amount,
                'inbound_total': inbound_total,
                'outbound_total': outbound_total,
                'count': len(payments),
            },
            'summary': {
                'inbound_count': len(payments.filtered(lambda p: p.payment_type == 'inbound')),
                'outbound_count': len(payments.filtered(lambda p: p.payment_type == 'outbound')),
                'currencies': list(set(payments.mapped('currency_id.name'))),
                'date_range': {
                    'from': min(payments.mapped('date')) if payments else False,
                    'to': max(payments.mapped('date')) if payments else False,
                }
            }
        }

    # ================================
    # WORKFLOW INTEGRATION
    # ================================
    
    def post(self):
        """Override post to ensure QR code is generated"""
        result = super().post()
        
        # Force QR code computation after posting
        for payment in self:
            if not payment.qr_verification_token:
                payment.qr_verification_token = payment._generate_verification_token()
            payment._compute_qr_code()
        
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate verification tokens"""
        for vals in vals_list:
            if 'qr_verification_token' not in vals:
                vals['qr_verification_token'] = self._generate_verification_token()
        
        return super().create(vals_list)
