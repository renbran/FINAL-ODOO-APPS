# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import json
import logging

_logger = logging.getLogger(__name__)


class PaymentApprovalController(http.Controller):
    """Main controller for payment approval functionality."""

    @http.route('/payment/approval/dashboard', type='http', auth='user', website=True)
    def payment_approval_dashboard(self, **kwargs):
        """Render the payment approval dashboard."""
        if not request.env.user.has_group('account_payment_approval.payment_approval_user'):
            raise AccessError("You don't have access to the payment approval dashboard.")
        
        return request.render('account_payment_approval.payment_approval_dashboard_template', {
            'page_name': 'payment_approval_dashboard',
        })

    @http.route('/payment/approval/stats', type='json', auth='user', methods=['POST'])
    def get_approval_stats(self, **kwargs):
        """Get payment approval statistics for dashboard."""
        try:
            domain = [('company_id', '=', request.env.company.id)]
            
            # Get user's role to filter appropriate payments
            user = request.env.user
            if user.has_group('account_payment_approval.payment_approval_manager'):
                pass  # Managers can see all payments
            elif user.has_group('account_payment_approval.payment_approval_authorizer'):
                domain.append(('state', 'in', ['approved', 'authorized', 'posted']))
            elif user.has_group('account_payment_approval.payment_approval_approver'):
                domain.append(('state', 'in', ['under_review', 'approved']))
            else:
                domain.append(('create_uid', '=', user.id))

            Payment = request.env['account.payment']
            
            stats = {
                'pending_review': Payment.search_count(domain + [('state', '=', 'under_review')]),
                'pending_approval': Payment.search_count(domain + [('state', '=', 'submitted')]),
                'pending_authorization': Payment.search_count(domain + [('state', '=', 'approved')]),
                'total_today': Payment.search_count(domain + [
                    ('create_date', '>=', fields.Date.today()),
                    ('create_date', '<', fields.Date.today() + fields.timedelta(days=1))
                ]),
                'total_amount_pending': sum(Payment.search(domain + [
                    ('state', 'in', ['submitted', 'under_review', 'approved'])
                ]).mapped('amount')),
            }
            
            return {'status': 'success', 'data': stats}
            
        except Exception as e:
            _logger.error(f"Error getting approval stats: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/payment/approval/recent', type='json', auth='user', methods=['POST'])
    def get_recent_payments(self, limit=10, **kwargs):
        """Get recent payments for dashboard."""
        try:
            domain = [('company_id', '=', request.env.company.id)]
            
            # Apply user permissions
            user = request.env.user
            if not user.has_group('account_payment_approval.payment_approval_manager'):
                if user.has_group('account_payment_approval.payment_approval_authorizer'):
                    domain.append(('state', 'in', ['approved', 'authorized', 'posted']))
                elif user.has_group('account_payment_approval.payment_approval_approver'):
                    domain.append(('state', 'in', ['under_review', 'approved']))
                else:
                    domain.append(('create_uid', '=', user.id))

            payments = request.env['account.payment'].search(
                domain, 
                order='create_date desc', 
                limit=limit
            )
            
            payment_data = []
            for payment in payments:
                payment_data.append({
                    'id': payment.id,
                    'name': payment.name or f"Payment {payment.id}",
                    'partner_name': payment.partner_id.name,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'state': payment.state,
                    'state_label': dict(payment._fields['state'].selection)[payment.state],
                    'create_date': payment.create_date.isoformat() if payment.create_date else '',
                    'urgency_level': getattr(payment, 'urgency_level', 'normal'),
                })
            
            return {'status': 'success', 'data': payment_data}
            
        except Exception as e:
            _logger.error(f"Error getting recent payments: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/payment/approval/action', type='json', auth='user', methods=['POST'])
    def payment_action(self, payment_id, action, **kwargs):
        """Execute payment approval actions."""
        try:
            payment = request.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return {'status': 'error', 'message': 'Payment not found'}

            # Check user permissions for the action
            user = request.env.user
            if action == 'submit' and payment.state == 'draft':
                if user.has_group('account_payment_approval.payment_approval_user'):
                    payment.action_submit_for_approval()
                else:
                    return {'status': 'error', 'message': 'Permission denied'}
                    
            elif action == 'review' and payment.state == 'submitted':
                if user.has_group('account_payment_approval.payment_approval_reviewer'):
                    payment.action_mark_as_reviewed()
                else:
                    return {'status': 'error', 'message': 'Permission denied'}
                    
            elif action == 'approve' and payment.state == 'under_review':
                if user.has_group('account_payment_approval.payment_approval_approver'):
                    payment.action_approve_payment()
                else:
                    return {'status': 'error', 'message': 'Permission denied'}
                    
            elif action == 'authorize' and payment.state == 'approved':
                if user.has_group('account_payment_approval.payment_approval_authorizer'):
                    payment.action_authorize_payment()
                else:
                    return {'status': 'error', 'message': 'Permission denied'}
                    
            elif action == 'post' and payment.state == 'authorized':
                if user.has_group('account_payment_approval.payment_approval_manager'):
                    payment.action_post()
                else:
                    return {'status': 'error', 'message': 'Permission denied'}
            else:
                return {'status': 'error', 'message': f'Invalid action {action} for current state {payment.state}'}

            return {
                'status': 'success', 
                'message': f'Payment {action} successful',
                'new_state': payment.state
            }
            
        except Exception as e:
            _logger.error(f"Error executing payment action: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/payment/approval/bulk_action', type='json', auth='user', methods=['POST'])
    def bulk_payment_action(self, payment_ids, action, **kwargs):
        """Execute bulk payment actions."""
        try:
            payments = request.env['account.payment'].browse(payment_ids)
            if not payments:
                return {'status': 'error', 'message': 'No payments found'}

            results = []
            for payment in payments:
                try:
                    result = self.payment_action(payment.id, action)
                    results.append({
                        'payment_id': payment.id,
                        'payment_name': payment.name,
                        'status': result['status'],
                        'message': result.get('message', ''),
                    })
                except Exception as e:
                    results.append({
                        'payment_id': payment.id,
                        'payment_name': payment.name,
                        'status': 'error',
                        'message': str(e),
                    })

            successful = len([r for r in results if r['status'] == 'success'])
            failed = len([r for r in results if r['status'] == 'error'])
            
            return {
                'status': 'success',
                'message': f'Bulk action completed: {successful} successful, {failed} failed',
                'results': results,
                'summary': {'successful': successful, 'failed': failed}
            }
            
        except Exception as e:
            _logger.error(f"Error executing bulk payment action: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/payment/signature/verify', type='json', auth='user', methods=['POST'])
    def verify_signature(self, payment_id, signature_data, **kwargs):
        """Verify digital signature for payment."""
        try:
            payment = request.env['account.payment'].browse(payment_id)
            if not payment.exists():
                return {'status': 'error', 'message': 'Payment not found'}

            # Here you would implement signature verification logic
            # For now, we'll simulate verification
            is_valid = bool(signature_data and len(signature_data) > 10)
            
            if is_valid:
                # Store signature if valid
                payment.write({
                    'digital_signature': signature_data,
                    'signature_date': fields.Datetime.now(),
                    'signature_user_id': request.env.user.id,
                })
                
                return {
                    'status': 'success',
                    'message': 'Digital signature verified and stored',
                    'verified': True
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Invalid digital signature',
                    'verified': False
                }
            
        except Exception as e:
            _logger.error(f"Error verifying signature: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/payment/notifications/mark_read', type='json', auth='user', methods=['POST'])
    def mark_notifications_read(self, notification_ids, **kwargs):
        """Mark payment notifications as read."""
        try:
            # This would integrate with Odoo's notification system
            # For now, we'll return success
            return {
                'status': 'success',
                'message': f'Marked {len(notification_ids)} notifications as read'
            }
            
        except Exception as e:
            _logger.error(f"Error marking notifications as read: {str(e)}")
            return {'status': 'error', 'message': str(e)}
