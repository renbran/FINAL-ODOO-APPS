# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import logging
import json

_logger = logging.getLogger(__name__)


class AccountPaymentController(http.Controller):
    """Controller for payment approval operations"""

    @http.route('/payment/approval/dashboard', type='http', auth='user', website=True)
    def payment_approval_dashboard(self, **kwargs):
        """Dashboard for payment approval overview"""
        try:
            # Check if user has access to payments
            if not request.env.user.has_group('account_payment_approval.group_payment_voucher_user'):
                raise AccessError(_("You don't have access to payment approvals."))

            # Get payment statistics
            Payment = request.env['account.payment']
            
            stats = {
                'pending_review': Payment.search_count([('voucher_state', '=', 'submitted')]),
                'pending_approval': Payment.search_count([('voucher_state', '=', 'reviewed')]),
                'pending_authorization': Payment.search_count([('voucher_state', '=', 'approved')]),
                'posted_today': Payment.search_count([
                    ('voucher_state', '=', 'posted'),
                    ('date', '=', request.env.context.get('today', fields.Date.today()))
                ]),
            }

            # Get recent payments for current user
            user_payments = Payment.search([
                ('create_uid', '=', request.env.user.id)
            ], order='create_date desc', limit=10)

            return request.render('account_payment_approval.payment_dashboard_template', {
                'stats': stats,
                'user_payments': user_payments,
                'page_name': 'Payment Approval Dashboard'
            })

        except Exception as e:
            _logger.error("Error in payment approval dashboard: %s", str(e))
            return request.render('website.404')

    @http.route('/payment/approval/submit', type='json', auth='user', methods=['POST'], csrf=False)
    def submit_payment_approval(self, payment_id=None, **kwargs):
        """Submit payment for approval"""
        try:
            if not payment_id:
                return {'error': 'Payment ID is required'}

            payment = request.env['account.payment'].browse(int(payment_id))
            if not payment.exists():
                return {'error': 'Payment not found'}

            # Check if user can submit
            if not payment.can_submit_for_approval():
                return {'error': 'Cannot submit this payment for approval'}

            result = payment.action_submit_for_approval()
            
            return {
                'success': True,
                'message': _('Payment submitted for approval successfully'),
                'new_state': payment.voucher_state
            }

        except Exception as e:
            _logger.error("Error submitting payment approval: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/approval/review', type='json', auth='user', methods=['POST'], csrf=False)
    def review_payment(self, payment_id=None, action=None, **kwargs):
        """Review payment (approve or reject)"""
        try:
            if not payment_id or not action:
                return {'error': 'Payment ID and action are required'}

            payment = request.env['account.payment'].browse(int(payment_id))
            if not payment.exists():
                return {'error': 'Payment not found'}

            if action == 'approve':
                if not payment.can_review():
                    return {'error': 'Cannot review this payment'}
                result = payment.action_review()
                message = _('Payment reviewed successfully')
            elif action == 'reject':
                if not payment.can_reject():
                    return {'error': 'Cannot reject this payment'}
                result = payment.action_reject()
                message = _('Payment rejected')
            else:
                return {'error': 'Invalid action'}

            return {
                'success': True,
                'message': message,
                'new_state': payment.voucher_state
            }

        except Exception as e:
            _logger.error("Error reviewing payment: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/approval/authorize', type='json', auth='user', methods=['POST'], csrf=False)
    def authorize_payment(self, payment_id=None, **kwargs):
        """Authorize payment"""
        try:
            if not payment_id:
                return {'error': 'Payment ID is required'}

            payment = request.env['account.payment'].browse(int(payment_id))
            if not payment.exists():
                return {'error': 'Payment not found'}

            if not payment.can_authorize():
                return {'error': 'Cannot authorize this payment'}

            result = payment.action_authorize()
            
            return {
                'success': True,
                'message': _('Payment authorized successfully'),
                'new_state': payment.voucher_state
            }

        except Exception as e:
            _logger.error("Error authorizing payment: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/signature/capture', type='http', auth='user', website=True)
    def signature_capture_page(self, payment_id=None, **kwargs):
        """Page for capturing digital signatures"""
        try:
            if not payment_id:
                return request.render('website.404')

            payment = request.env['account.payment'].browse(int(payment_id))
            if not payment.exists():
                return request.render('website.404')

            # Check if user can sign this payment
            can_sign = False
            signature_type = None

            if payment.can_review() and request.env.user.has_group('account_payment_approval.group_payment_voucher_reviewer'):
                can_sign = True
                signature_type = 'reviewer'
            elif payment.can_approve() and request.env.user.has_group('account_payment_approval.group_payment_voucher_approver'):
                can_sign = True
                signature_type = 'approver'
            elif payment.can_authorize() and request.env.user.has_group('account_payment_approval.group_payment_voucher_authorizer'):
                can_sign = True
                signature_type = 'authorizer'

            if not can_sign:
                return request.render('account_payment_approval.signature_access_denied', {
                    'payment': payment
                })

            return request.render('account_payment_approval.signature_capture_template', {
                'payment': payment,
                'signature_type': signature_type,
                'page_name': f'Sign Payment {payment.voucher_number}'
            })

        except Exception as e:
            _logger.error("Error in signature capture page: %s", str(e))
            return request.render('website.404')

    @http.route('/payment/signature/save', type='json', auth='user', methods=['POST'], csrf=False)
    def save_signature(self, payment_id=None, signature_data=None, signature_type=None, **kwargs):
        """Save digital signature"""
        try:
            if not all([payment_id, signature_data, signature_type]):
                return {'error': 'Missing required parameters'}

            payment = request.env['account.payment'].browse(int(payment_id))
            if not payment.exists():
                return {'error': 'Payment not found'}

            # Validate signature type and permissions
            if signature_type == 'reviewer' and not payment.can_review():
                return {'error': 'Cannot sign as reviewer'}
            elif signature_type == 'approver' and not payment.can_approve():
                return {'error': 'Cannot sign as approver'}
            elif signature_type == 'authorizer' and not payment.can_authorize():
                return {'error': 'Cannot sign as authorizer'}

            # Save signature
            result = payment.save_digital_signature(signature_data, signature_type)
            
            if result:
                return {
                    'success': True,
                    'message': _('Signature saved successfully'),
                    'new_state': payment.voucher_state
                }
            else:
                return {'error': 'Failed to save signature'}

        except Exception as e:
            _logger.error("Error saving signature: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/bulk/action', type='json', auth='user', methods=['POST'], csrf=False)
    def bulk_payment_action(self, payment_ids=None, action=None, **kwargs):
        """Bulk actions on payments"""
        try:
            if not payment_ids or not action:
                return {'error': 'Payment IDs and action are required'}

            payments = request.env['account.payment'].browse(payment_ids)
            if not payments:
                return {'error': 'No valid payments found'}

            results = []
            for payment in payments:
                try:
                    if action == 'submit' and payment.can_submit_for_approval():
                        payment.action_submit_for_approval()
                        results.append({'id': payment.id, 'success': True})
                    elif action == 'review' and payment.can_review():
                        payment.action_review()
                        results.append({'id': payment.id, 'success': True})
                    elif action == 'approve' and payment.can_approve():
                        payment.action_approve()
                        results.append({'id': payment.id, 'success': True})
                    elif action == 'authorize' and payment.can_authorize():
                        payment.action_authorize()
                        results.append({'id': payment.id, 'success': True})
                    else:
                        results.append({'id': payment.id, 'success': False, 'error': 'Action not allowed'})
                except Exception as e:
                    results.append({'id': payment.id, 'success': False, 'error': str(e)})

            success_count = len([r for r in results if r['success']])
            
            return {
                'success': True,
                'message': f'{success_count} of {len(payment_ids)} payments processed successfully',
                'results': results
            }

        except Exception as e:
            _logger.error("Error in bulk payment action: %s", str(e))
            return {'error': str(e)}

    @http.route('/payment/approval/api/stats', type='json', auth='user', methods=['GET'], csrf=False)
    def get_approval_stats(self, **kwargs):
        """API endpoint for approval statistics"""
        try:
            Payment = request.env['account.payment']
            
            # Get user's permissions
            user_groups = {
                'can_submit': request.env.user.has_group('account_payment_approval.group_payment_voucher_user'),
                'can_review': request.env.user.has_group('account_payment_approval.group_payment_voucher_reviewer'),
                'can_approve': request.env.user.has_group('account_payment_approval.group_payment_voucher_approver'),
                'can_authorize': request.env.user.has_group('account_payment_approval.group_payment_voucher_authorizer'),
                'can_post': request.env.user.has_group('account_payment_approval.group_payment_voucher_poster'),
                'is_manager': request.env.user.has_group('account_payment_approval.group_payment_voucher_manager'),
            }

            # Get statistics based on user permissions
            stats = {}
            
            if user_groups['can_review']:
                stats['pending_review'] = Payment.search_count([('voucher_state', '=', 'submitted')])
            
            if user_groups['can_approve']:
                stats['pending_approval'] = Payment.search_count([('voucher_state', '=', 'reviewed')])
            
            if user_groups['can_authorize']:
                stats['pending_authorization'] = Payment.search_count([('voucher_state', '=', 'approved')])
            
            if user_groups['can_post']:
                stats['pending_posting'] = Payment.search_count([('voucher_state', '=', 'authorized')])

            # Overall statistics for managers
            if user_groups['is_manager']:
                stats.update({
                    'total_draft': Payment.search_count([('voucher_state', '=', 'draft')]),
                    'total_submitted': Payment.search_count([('voucher_state', '=', 'submitted')]),
                    'total_in_process': Payment.search_count([('voucher_state', 'in', ['submitted', 'reviewed', 'approved', 'authorized'])]),
                    'total_posted': Payment.search_count([('voucher_state', '=', 'posted')]),
                    'total_rejected': Payment.search_count([('voucher_state', '=', 'rejected')]),
                })

            return {
                'success': True,
                'stats': stats,
                'user_permissions': user_groups
            }

        except Exception as e:
            _logger.error("Error getting approval stats: %s", str(e))
            return {'error': str(e)}
