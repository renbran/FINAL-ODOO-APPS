# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    
    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', methods=['GET'], website=True)
    def verify_payment(self, payment_id, **kwargs):
        """Public endpoint to verify payment details via QR code scan"""
        try:
            # Search for the payment record
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return request.render('payment_account_enhanced.payment_verification_error', {
                    'error_title': 'Payment Not Found',
                    'error_message': f'No payment found with ID: {payment_id}',
                    'error_code': 'PAYMENT_NOT_FOUND'
                })
            
            # Prepare verification data
            verification_data = {
                'payment': payment,
                'voucher_number': payment.voucher_number,
                'payment_reference': payment.name,
                'amount': payment.amount,
                'currency': payment.currency_id.name,
                'partner_name': payment.partner_id.name if payment.partner_id else 'N/A',
                'payment_date': payment.date,
                'state': payment.state,
                'state_display': dict(payment._fields['state'].selection).get(payment.state),
                'payment_type': payment.payment_type,
                'payment_type_display': dict(payment._fields['payment_type'].selection).get(payment.payment_type),
                'company_name': payment.company_id.name,
                'journal_name': payment.journal_id.name if payment.journal_id else 'N/A',
                'is_verified': payment.state == 'posted',
                'verification_timestamp': fields.Datetime.now(),
            }
            
            # Log the verification attempt
            _logger.info(f"Payment verification accessed for payment ID: {payment_id} by IP: {request.httprequest.remote_addr}")
            
            return request.render('payment_account_enhanced.payment_verification_success', verification_data)
            
        except Exception as e:
            _logger.error(f"Error during payment verification for ID {payment_id}: {str(e)}")
            return request.render('payment_account_enhanced.payment_verification_error', {
                'error_title': 'Verification Error',
                'error_message': 'An error occurred while verifying the payment. Please try again.',
                'error_code': 'VERIFICATION_ERROR'
            })
    
    @http.route('/payment/verify/api/<int:payment_id>', type='json', auth='public', methods=['POST'])
    def verify_payment_api(self, payment_id, **kwargs):
        """JSON API endpoint for mobile apps or systems integration"""
        try:
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return {
                    'success': False,
                    'error': 'PAYMENT_NOT_FOUND',
                    'message': f'No payment found with ID: {payment_id}'
                }
            
            return {
                'success': True,
                'payment_data': {
                    'voucher_number': payment.voucher_number,
                    'reference': payment.name,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'partner': payment.partner_id.name if payment.partner_id else None,
                    'date': payment.date.isoformat() if payment.date else None,
                    'state': payment.state,
                    'state_display': dict(payment._fields['state'].selection).get(payment.state),
                    'payment_type': payment.payment_type,
                    'company': payment.company_id.name,
                    'journal': payment.journal_id.name if payment.journal_id else None,
                    'is_verified': payment.state == 'posted',
                    'verified_at': fields.Datetime.now().isoformat(),
                }
            }
            
        except Exception as e:
            _logger.error(f"API verification error for payment ID {payment_id}: {str(e)}")
            return {
                'success': False,
                'error': 'VERIFICATION_ERROR',
                'message': 'An error occurred during verification'
            }
    
    @http.route('/payment/qr-guide', type='http', auth='public', methods=['GET'], website=True)
    def qr_verification_guide(self, **kwargs):
        """Public page explaining how to use QR code verification"""
        return request.render('payment_account_enhanced.qr_verification_guide', {
            'page_title': 'Payment QR Code Verification Guide',
            'company_name': request.env.company.name,
        })
