# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import logging
import base64
import json

_logger = logging.getLogger(__name__)


class QRVerificationController(http.Controller):
    """Controller for QR code verification"""

    @http.route('/payment/verify/<string:token>', type='http', auth='public', website=True)
    def verify_payment(self, token, **kwargs):
        """Public verification page for QR codes"""
        try:
            # Search for payment with this verification token
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return request.render('account_payment_approval.verification_not_found', {
                    'token': token,
                    'page_name': 'Payment Verification - Not Found'
                })

            # Prepare verification data
            verification_data = {
                'payment': payment,
                'token': token,
                'is_valid': True,
                'verification_status': self._get_verification_status(payment),
                'signatures': self._get_signature_status(payment),
                'page_name': f'Payment Verification - {payment.voucher_number}'
            }

            return request.render('account_payment_approval.verification_result', verification_data)

        except Exception as e:
            _logger.error("Error in QR verification: %s", str(e))
            return request.render('account_payment_approval.verification_error', {
                'error_message': _('An error occurred during verification'),
                'token': token,
                'page_name': 'Payment Verification - Error'
            })

    @http.route('/payment/verify/api/<string:token>', type='json', auth='public', methods=['GET'], csrf=False)
    def verify_payment_api(self, token, **kwargs):
        """API endpoint for payment verification"""
        try:
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return {
                    'success': False,
                    'error': 'Invalid verification token',
                    'token': token
                }

            # Build verification response
            verification_data = {
                'success': True,
                'payment': {
                    'voucher_number': payment.voucher_number,
                    'voucher_type': 'Payment Voucher' if payment.payment_type == 'outbound' else 'Receipt Voucher',
                    'state': payment.voucher_state,
                    'state_display': payment._get_state_display(),
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'date': payment.date.strftime('%Y-%m-%d') if payment.date else None,
                    'partner': payment.partner_id.name,
                    'payment_method': payment.payment_method_id.name,
                    'journal': payment.journal_id.name,
                    'reference': payment.ref,
                    'company': payment.company_id.name,
                },
                'verification': {
                    'token': token,
                    'verified_at': request.env.context.get('now', ''),
                    'status': self._get_verification_status(payment),
                    'is_authentic': True,
                    'signatures': self._get_signature_status(payment)
                }
            }

            return verification_data

        except Exception as e:
            _logger.error("Error in API verification: %s", str(e))
            return {
                'success': False,
                'error': str(e),
                'token': token
            }

    @http.route('/payment/verify/qr/scan', type='http', auth='public', website=True)
    def qr_scanner_page(self, **kwargs):
        """QR code scanner page"""
        return request.render('account_payment_approval.qr_scanner_template', {
            'page_name': 'Payment QR Scanner'
        })

    @http.route('/payment/verify/batch', type='json', auth='user', methods=['POST'], csrf=False)
    def batch_verify_payments(self, tokens=None, **kwargs):
        """Batch verification for multiple tokens"""
        try:
            if not tokens or not isinstance(tokens, list):
                return {'error': 'Tokens list is required'}

            results = []
            for token in tokens:
                try:
                    payment = request.env['account.payment'].search([
                        ('verification_token', '=', token)
                    ], limit=1)

                    if payment:
                        results.append({
                            'token': token,
                            'success': True,
                            'voucher_number': payment.voucher_number,
                            'state': payment.voucher_state,
                            'amount': payment.amount,
                            'partner': payment.partner_id.name,
                            'date': payment.date.strftime('%Y-%m-%d') if payment.date else None
                        })
                    else:
                        results.append({
                            'token': token,
                            'success': False,
                            'error': 'Token not found'
                        })
                except Exception as e:
                    results.append({
                        'token': token,
                        'success': False,
                        'error': str(e)
                    })

            success_count = len([r for r in results if r['success']])
            
            return {
                'success': True,
                'message': f'{success_count} of {len(tokens)} tokens verified successfully',
                'results': results
            }

        except Exception as e:
            _logger.error("Error in batch verification: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/verify/download/<string:token>', type='http', auth='public')
    def download_verification_report(self, token, **kwargs):
        """Download verification report as PDF"""
        try:
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return request.not_found()

            # Generate PDF report
            report = request.env.ref('account_payment_approval.action_report_qr_verification')
            pdf_content, content_type = report.sudo()._render_qweb_pdf([payment.id])

            # Prepare response
            response = request.make_response(
                pdf_content,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="Payment_Verification_{payment.voucher_number}_{token[:8]}.pdf"'),
                    ('Content-Length', len(pdf_content))
                ]
            )
            
            return response

        except Exception as e:
            _logger.error("Error downloading verification report: %s", str(e))
            return request.not_found()

    @http.route('/payment/verify/status/<string:token>', type='json', auth='public', methods=['GET'], csrf=False)
    def get_verification_status(self, token, **kwargs):
        """Get real-time verification status"""
        try:
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)

            if not payment:
                return {'success': False, 'error': 'Token not found'}

            return {
                'success': True,
                'status': {
                    'state': payment.voucher_state,
                    'display_name': payment._get_state_display(),
                    'is_completed': payment.voucher_state == 'posted',
                    'is_rejected': payment.voucher_state == 'rejected',
                    'progress_percentage': self._calculate_progress_percentage(payment),
                    'next_action': self._get_next_action(payment),
                    'last_updated': payment.write_date.strftime('%Y-%m-%d %H:%M:%S') if payment.write_date else None
                }
            }

        except Exception as e:
            _logger.error("Error getting verification status: %s", str(e))
            return {'success': False, 'error': str(e)}

    def _get_verification_status(self, payment):
        """Get human-readable verification status"""
        status_map = {
            'draft': 'Draft - Not yet submitted',
            'submitted': 'Submitted for Review',
            'reviewed': 'Reviewed - Pending Approval',
            'approved': 'Approved - Pending Authorization',
            'authorized': 'Authorized - Ready for Posting',
            'posted': 'Posted - Payment Completed',
            'rejected': 'Rejected',
        }
        return status_map.get(payment.voucher_state, 'Unknown Status')

    def _get_signature_status(self, payment):
        """Get signature status for verification"""
        signatures = []
        
        # Creator signature
        signatures.append({
            'role': 'Creator',
            'name': payment.creator_name,
            'signed': bool(payment.creator_signature),
            'date': payment.creator_signature_date.strftime('%Y-%m-%d %H:%M:%S') if payment.creator_signature_date else None
        })

        # Reviewer signature
        signatures.append({
            'role': 'Reviewer',
            'name': payment.reviewer_name,
            'signed': bool(payment.reviewer_signature),
            'date': payment.reviewer_signature_date.strftime('%Y-%m-%d %H:%M:%S') if payment.reviewer_signature_date else None
        })

        # Approver signature (only for payment vouchers)
        if payment.payment_type == 'outbound':
            signatures.append({
                'role': 'Approver',
                'name': payment.approver_name,
                'signed': bool(payment.approver_signature),
                'date': payment.approver_signature_date.strftime('%Y-%m-%d %H:%M:%S') if payment.approver_signature_date else None
            })

        # Authorizer signature
        signatures.append({
            'role': 'Authorizer',
            'name': payment.authorizer_name,
            'signed': bool(payment.authorizer_signature),
            'date': payment.authorizer_signature_date.strftime('%Y-%m-%d %H:%M:%S') if payment.authorizer_signature_date else None
        })

        return signatures

    def _calculate_progress_percentage(self, payment):
        """Calculate completion percentage"""
        state_progress = {
            'draft': 0,
            'submitted': 20,
            'reviewed': 40,
            'approved': 60,
            'authorized': 80,
            'posted': 100,
            'rejected': 0,
        }
        return state_progress.get(payment.voucher_state, 0)

    def _get_next_action(self, payment):
        """Get next required action"""
        next_actions = {
            'draft': 'Submit for approval',
            'submitted': 'Waiting for review',
            'reviewed': 'Waiting for approval' if payment.payment_type == 'outbound' else 'Waiting for authorization',
            'approved': 'Waiting for authorization',
            'authorized': 'Ready for posting',
            'posted': 'Completed',
            'rejected': 'Rejected - No further action',
        }
        return next_actions.get(payment.voucher_state, 'Unknown')
