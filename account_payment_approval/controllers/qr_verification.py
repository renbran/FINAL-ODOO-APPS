# -*- coding: utf-8 -*-
#############################################################################
#
#    QR Verification Controller
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class PaymentQRVerification(http.Controller):
    """Public controller for QR code verification"""
    
    @http.route('/payment/verify/<string:token>', type='http', auth='public', website=True, csrf=False)
    def verify_payment_qr(self, token, **kwargs):
        """Public QR verification endpoint"""
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return request.render('account_payment_approval.qr_verification_error', {
                    'error_title': _('Invalid Verification Code'),
                    'error_message': _('The QR code you scanned contains an invalid or expired verification token.'),
                    'error_code': 'INVALID_TOKEN'
                })
            
            # Check if payment is in verifiable state
            if payment.voucher_state not in ['authorized', 'posted']:
                return request.render('account_payment_approval.qr_verification_error', {
                    'error_title': _('Payment Not Yet Verified'),
                    'error_message': _('This payment has not been authorized yet and cannot be verified.'),
                    'error_code': 'NOT_AUTHORIZED'
                })
            
            # Increment verification counter
            payment.increment_qr_verification()
            
            # Prepare verification data
            verification_data = {
                'payment': payment,
                'voucher_number': payment.voucher_number,
                'amount': payment.amount,
                'currency': payment.currency_id,
                'partner': payment.partner_id,
                'date': payment.date,
                'voucher_state': payment.voucher_state,
                'verification_count': payment.qr_verification_count,
                'last_verification': payment.last_qr_verification,
                'amount_in_words': payment.amount_in_words,
                'payment_method': payment.payment_method_display,
                'authorized_by': payment.authorized_by,
                'authorized_date': payment.authorized_date,
                'company': payment.company_id,
            }
            
            # Render verification page
            return request.render('account_payment_approval.qr_verification_success', verification_data)
            
        except Exception as e:
            _logger.error(f"Error in QR verification for token {token}: {str(e)}")
            return request.render('account_payment_approval.qr_verification_error', {
                'error_title': _('Verification Error'),
                'error_message': _('An error occurred while verifying the payment. Please try again later.'),
                'error_code': 'SYSTEM_ERROR'
            })
    
    @http.route('/payment/verify/api/<string:token>', type='json', auth='public', csrf=False)
    def verify_payment_api(self, token, **kwargs):
        """JSON API for QR verification (for mobile apps)"""
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return {
                    'success': False,
                    'error': 'INVALID_TOKEN',
                    'message': _('Invalid or expired verification token')
                }
            
            # Check if payment is in verifiable state
            if payment.voucher_state not in ['authorized', 'posted']:
                return {
                    'success': False,
                    'error': 'NOT_AUTHORIZED',
                    'message': _('Payment not yet authorized for verification')
                }
            
            # Increment verification counter
            payment.increment_qr_verification()
            
            # Return verification data
            return {
                'success': True,
                'data': {
                    'voucher_number': payment.voucher_number,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'currency_symbol': payment.currency_id.symbol,
                    'partner_name': payment.partner_id.name if payment.partner_id else '',
                    'date': payment.date.isoformat() if payment.date else '',
                    'voucher_state': payment.voucher_state,
                    'verification_count': payment.qr_verification_count,
                    'last_verification': payment.last_qr_verification.isoformat() if payment.last_qr_verification else '',
                    'amount_in_words': payment.amount_in_words,
                    'payment_method': payment.payment_method_display,
                    'authorized_by': payment.authorized_by.name if payment.authorized_by else '',
                    'authorized_date': payment.authorized_date.isoformat() if payment.authorized_date else '',
                    'company_name': payment.company_id.name,
                    'company_logo': f'/web/image/res.company/{payment.company_id.id}/logo' if payment.company_id.logo else '',
                }
            }
            
        except Exception as e:
            _logger.error(f"Error in QR API verification for token {token}: {str(e)}")
            return {
                'success': False,
                'error': 'SYSTEM_ERROR',
                'message': _('System error during verification')
            }
    
    @http.route('/payment/qr/stats/<string:token>', type='json', auth='public', csrf=False)
    def get_qr_stats(self, token, **kwargs):
        """Get QR verification statistics"""
        try:
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return {
                    'success': False,
                    'error': 'INVALID_TOKEN'
                }
            
            return {
                'success': True,
                'stats': {
                    'verification_count': payment.qr_verification_count,
                    'last_verification': payment.last_qr_verification.isoformat() if payment.last_qr_verification else None,
                    'first_verification': payment.create_date.isoformat(),
                    'days_since_creation': (request.env.cr.now() - payment.create_date).days,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error getting QR stats for token {token}: {str(e)}")
            return {
                'success': False,
                'error': 'SYSTEM_ERROR'
            }


class PaymentVerificationPortal(http.Controller):
    """Portal controller for authenticated verification"""
    
    @http.route('/my/payments/verify', type='http', auth='user', website=True)
    def portal_payment_verification(self, **kwargs):
        """Portal page for payment verification"""
        # Get user's verifiable payments
        payments = request.env['account.payment'].search([
            ('voucher_state', 'in', ['authorized', 'posted']),
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        
        return request.render('account_payment_approval.portal_verification', {
            'payments': payments,
            'page_name': 'payment_verification',
        })
    
    @http.route('/my/payments/<int:payment_id>/verify', type='http', auth='user', website=True)
    def portal_payment_detail(self, payment_id, **kwargs):
        """Portal page for specific payment verification"""
        try:
            payment = request.env['account.payment'].browse(payment_id)
            
            # Check access rights
            if not payment.exists():
                return request.not_found()
            
            # Check if user can access this payment
            if (payment.partner_id != request.env.user.partner_id and 
                not request.env.user.has_group('account_payment_approval.group_payment_reviewer')):
                return request.not_found()
            
            # Prepare verification data
            verification_data = {
                'payment': payment,
                'can_verify': payment.voucher_state in ['authorized', 'posted'],
                'verification_url': payment.verification_url,
                'qr_code_data': payment.qr_code,
            }
            
            return request.render('account_payment_approval.portal_payment_detail', verification_data)
            
        except Exception as e:
            _logger.error(f"Error in portal payment detail for ID {payment_id}: {str(e)}")
            return request.not_found()
    
    @http.route('/my/payments/<int:payment_id>/qr', type='http', auth='user')
    def download_qr_code(self, payment_id, **kwargs):
        """Download QR code as image"""
        try:
            payment = request.env['account.payment'].browse(payment_id)
            
            # Check access rights
            if not payment.exists() or not payment.qr_code:
                return request.not_found()
            
            # Check if user can access this payment
            if (payment.partner_id != request.env.user.partner_id and 
                not request.env.user.has_group('account_payment_approval.group_payment_reviewer')):
                return request.not_found()
            
            # Return QR code image
            return request.make_response(
                base64.b64decode(payment.qr_code),
                headers=[
                    ('Content-Type', 'image/png'),
                    ('Content-Disposition', f'attachment; filename="payment_{payment.voucher_number}_qr.png"'),
                ]
            )
            
        except Exception as e:
            _logger.error(f"Error downloading QR code for payment {payment_id}: {str(e)}")
            return request.not_found()
