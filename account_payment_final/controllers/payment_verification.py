# -*- coding: utf-8 -*-

import json
import logging
from werkzeug.exceptions import NotFound, Forbidden
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    """Controller for Payment Voucher QR Code Verification"""

    @http.route('/payment/verify/<string:token>', type='http', auth='public', 
                methods=['GET'], website=True, csrf=False)
    def verify_payment_voucher(self, token, **kwargs):
        """
        Public route to verify payment voucher using QR code token
        Accessible without login for external verification
        """
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('qr_verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return request.render('payment_voucher_enhanced.verification_not_found', {
                    'error_title': _('Voucher Not Found'),
                    'error_message': _('The verification code is invalid or expired.'),
                    'token': token
                })
            
            # Check if payment is in verifiable state
            if payment.approval_state in ['draft', 'cancelled']:
                return request.render('payment_voucher_enhanced.verification_error', {
                    'error_title': _('Verification Not Available'),
                    'error_message': _('This voucher is not yet available for verification.'),
                    'payment': payment
                })
            
            # Prepare verification data
            verification_data = {
                'payment': payment,
                'company': payment.company_id,
                'partner': payment.partner_id,
                'verification_token': token,
                'verification_date': request.env.context.get('tz_offset', 0),
                'is_valid': True,
                'related_documents': payment.get_related_document_info(),
                'workflow_history': payment._get_workflow_history_for_verification(),
            }
            
            # Log verification attempt
            request.env['payment.verification.log'].sudo().create({
                'payment_id': payment.id,
                'token': token,
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
                'verification_date': request.env.context.get('tz_offset', 0),
                'is_successful': True,
            })
            
            return request.render('payment_voucher_enhanced.payment_verification', verification_data)
            
        except Exception as e:
            _logger.error(f"Payment verification error for token {token}: {str(e)}")
            
            # Log failed verification
            try:
                request.env['payment.verification.log'].sudo().create({
                    'token': token,
                    'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                    'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
                    'verification_date': request.env.context.get('tz_offset', 0),
                    'is_successful': False,
                    'error_message': str(e),
                })
            except:
                pass  # Don't fail verification if logging fails
            
            return request.render('payment_voucher_enhanced.verification_error', {
                'error_title': _('Verification Error'),
                'error_message': _('An error occurred while verifying the voucher. Please try again.'),
                'token': token
            })

    @http.route('/payment/verify/api/<string:token>', type='json', auth='public', 
                methods=['POST'], csrf=False)
    def verify_payment_api(self, token, **kwargs):
        """
        JSON API endpoint for payment verification
        Returns structured data for API integrations
        """
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('qr_verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return {
                    'success': False,
                    'error': 'VOUCHER_NOT_FOUND',
                    'message': _('The verification code is invalid or expired.'),
                    'token': token
                }
            
            # Check if payment is in verifiable state
            if payment.approval_state in ['draft', 'cancelled']:
                return {
                    'success': False,
                    'error': 'VERIFICATION_NOT_AVAILABLE',
                    'message': _('This voucher is not yet available for verification.'),
                    'voucher_state': payment.approval_state
                }
            
            # Prepare API response data
            response_data = {
                'success': True,
                'voucher': {
                    'number': payment.voucher_number,
                    'type': payment.payment_type,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'date': payment.date.isoformat() if payment.date else None,
                    'partner': {
                        'name': payment.partner_id.name,
                        'vat': payment.partner_id.vat,
                    },
                    'state': payment.approval_state,
                    'posted': payment.state == 'posted',
                },
                'company': {
                    'name': payment.company_id.name,
                    'vat': payment.company_id.vat,
                    'logo': payment.company_id.logo,
                },
                'verification': {
                    'token': token,
                    'timestamp': request.env.context.get('tz_offset', 0),
                    'is_valid': True,
                },
                'workflow': payment._get_workflow_history_for_verification(),
            }
            
            # Log API verification
            request.env['payment.verification.log'].sudo().create({
                'payment_id': payment.id,
                'token': token,
                'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
                'verification_date': request.env.context.get('tz_offset', 0),
                'is_successful': True,
                'is_api_call': True,
            })
            
            return response_data
            
        except Exception as e:
            _logger.error(f"API payment verification error for token {token}: {str(e)}")
            
            # Log failed API verification
            try:
                request.env['payment.verification.log'].sudo().create({
                    'token': token,
                    'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
                    'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
                    'verification_date': request.env.context.get('tz_offset', 0),
                    'is_successful': False,
                    'error_message': str(e),
                    'is_api_call': True,
                })
            except:
                pass
            
            return {
                'success': False,
                'error': 'VERIFICATION_ERROR',
                'message': _('An error occurred while verifying the voucher.'),
                'token': token
            }

    @http.route('/payment/verify/download/<string:token>', type='http', auth='public', 
                methods=['GET'], csrf=False)
    def download_voucher_pdf(self, token, **kwargs):
        """
        Download verified voucher as PDF
        """
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('qr_verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                raise NotFound(_('Voucher not found'))
            
            # Check if payment is in verifiable state
            if payment.approval_state in ['draft', 'cancelled']:
                raise Forbidden(_('Voucher not available for download'))
            
            # Generate PDF report
            pdf_content, content_type = request.env.ref(
                'payment_voucher_enhanced.action_report_payment_voucher_osus'
            ).sudo()._render_qweb_pdf([payment.id])
            
            # Log download
            request.env['payment.verification.log'].sudo().create({
                'payment_id': payment.id,
                'token': token,
                'ip_address': request.httprequest.environ.get('