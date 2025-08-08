from odoo import http
from odoo.http import request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class PaymentVerificationController(http.Controller):
    
    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True)
    def verify_payment(self, payment_id, **kwargs):
        """Public endpoint for QR code payment verification"""
        try:
            # Search for the payment record
            payment = request.env['account.payment'].sudo().search([
                ('id', '=', payment_id)
            ], limit=1)
            
            if not payment:
                return self._render_error(
                    error_title="Payment Not Found",
                    error_message="The payment you're trying to verify could not be found in our system.",
                    error_code="PAYMENT_NOT_FOUND"
                )
            
            # Log verification attempt for audit
            self._log_verification_attempt(payment, success=True)
            
            # Prepare payment data for template
            payment_data = self._prepare_payment_data(payment)
            
            return request.render('account_payment_final.payment_verification_success', payment_data)
            
        except Exception as e:
            _logger.error(f"Error verifying payment ID {payment_id}: {str(e)}")
            return self._render_error(
                error_title="Verification Error",
                error_message="An error occurred while verifying the payment. Please try again later.",
                error_code="VERIFICATION_ERROR"
            )
    
    @http.route('/payment/qr-guide', type='http', auth='public', website=True)
    def qr_verification_guide(self, **kwargs):
        """QR code verification guide page"""
        try:
            company = request.env.company
            return request.render('account_payment_final.qr_verification_guide', {
                'company_name': company.name,
                'company_website': company.website,
            })
        except Exception as e:
            _logger.error(f"Error loading QR guide: {str(e)}")
            return request.not_found()
    
    def _prepare_payment_data(self, payment):
        """Prepare payment data for verification template"""
        try:
            # Map approval_state to display state
            state_mapping = {
                'draft': 'draft',
                'under_review': 'submitted',
                'for_approval': 'submitted',
                'for_authorization': 'submitted',
                'approved': 'approved',
                'posted': 'posted',
                'cancelled': 'cancelled'
            }
            
            # Determine payment type display
            payment_type_display = 'Vendor Payment' if payment.payment_type == 'outbound' else 'Customer Receipt'
            
            # Get the appropriate authorizer based on workflow stage
            authorized_by = ''
            if payment.authorizer_id:
                authorized_by = payment.authorizer_id.name
            elif payment.actual_approver_id:
                authorized_by = payment.actual_approver_id.name
            elif payment.approver_id:
                authorized_by = payment.approver_id.name
            elif payment.reviewer_id:
                authorized_by = payment.reviewer_id.name
            
            # Format verification timestamp
            verification_timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')
            
            return {
                'voucher_number': payment.voucher_number or payment.name,
                'payment_reference': payment.ref or payment.name,
                'amount': f"{payment.amount:,.2f}",
                'currency': payment.currency_id.name or 'USD',
                'partner_name': payment.partner_id.name if payment.partner_id else 'N/A',
                'payment_date': payment.date.strftime('%B %d, %Y') if payment.date else 'N/A',
                'state': state_mapping.get(payment.approval_state, 'unknown'),
                'payment_type_display': payment_type_display,
                'journal_name': payment.journal_id.name if payment.journal_id else 'N/A',
                'company_name': payment.company_id.name,
                'verification_timestamp': verification_timestamp,
                'is_verified': payment.approval_state == 'posted',
                'authorized_by': authorized_by,
                'approval_state': payment.approval_state,
                'workflow_stage': self._get_workflow_stage_display(payment),
            }
        except Exception as e:
            _logger.error(f"Error preparing payment data: {str(e)}")
            raise
    
    def _get_workflow_stage_display(self, payment):
        """Get human-readable workflow stage"""
        stage_mapping = {
            'draft': 'Draft - Not yet submitted',
            'under_review': 'Under Review - Pending reviewer approval',
            'for_approval': 'For Approval - Pending approver decision',
            'for_authorization': 'For Authorization - Pending final authorization',
            'approved': 'Approved - Ready for posting',
            'posted': 'Posted - Payment completed',
            'cancelled': 'Cancelled - Payment cancelled'
        }
        return stage_mapping.get(payment.approval_state, 'Unknown Status')
    
    def _render_error(self, error_title, error_message, error_code):
        """Render error template with provided details"""
        return request.render('account_payment_final.payment_verification_error', {
            'error_title': error_title,
            'error_message': error_message,
            'error_code': error_code,
        })
    
    def _log_verification_attempt(self, payment, success=True):
        """Log verification attempt for audit purposes"""
        try:
            user_ip = request.httprequest.environ.get('REMOTE_ADDR', 'unknown')
            user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', 'unknown')
            
            log_message = f"""QR Code Verification Attempt:
- Payment ID: {payment.id}
- Voucher Number: {payment.voucher_number}
- Success: {success}
- IP Address: {user_ip}
- User Agent: {user_agent}
- Timestamp: {datetime.now()}
- Current Status: {payment.approval_state}"""
            
            # Log to payment record
            payment.message_post(
                body=log_message,
                subject="QR Code Verification",
                message_type='notification'
            )
            
            # Log to system
            _logger.info(f"QR verification for payment {payment.voucher_number}: {'SUCCESS' if success else 'FAILED'}")
            
        except Exception as e:
            _logger.error(f"Error logging verification attempt: {str(e)}")
    
    @http.route('/payment/verify/status/<int:payment_id>', type='json', auth='public')
    def get_payment_status(self, payment_id):
        """JSON endpoint for real-time payment status checking"""
        try:
            payment = request.env['account.payment'].sudo().search([
                ('id', '=', payment_id)
            ], limit=1)
            
            if not payment:
                return {'error': 'Payment not found'}
            
            return {
                'status': 'success',
                'approval_state': payment.approval_state,
                'voucher_number': payment.voucher_number,
                'amount': payment.amount,
                'currency': payment.currency_id.name,
                'partner_name': payment.partner_id.name if payment.partner_id else '',
                'is_posted': payment.approval_state == 'posted',
                'workflow_stage': self._get_workflow_stage_display(payment),
                'last_updated': payment.write_date.isoformat() if payment.write_date else None
            }
            
        except Exception as e:
            _logger.error(f"Error getting payment status: {str(e)}")
            return {'error': 'Unable to retrieve payment status'}
    
    @http.route('/payment/verify/batch', type='json', auth='public')
    def verify_batch_payments(self, payment_ids):
        """Verify multiple payments at once (for bulk verification)"""
        try:
            if not isinstance(payment_ids, list) or len(payment_ids) > 50:  # Limit batch size
                return {'error': 'Invalid payment IDs or batch too large'}
            
            payments = request.env['account.payment'].sudo().search([
                ('id', 'in', payment_ids)
            ])
            
            results = []
            for payment in payments:
                self._log_verification_attempt(payment, success=True)
                results.append({
                    'id': payment.id,
                    'voucher_number': payment.voucher_number,
                    'approval_state': payment.approval_state,
                    'amount': payment.amount,
                    'currency': payment.currency_id.name,
                    'is_verified': payment.approval_state == 'posted'
                })
            
            return {
                'status': 'success',
                'payments': results,
                'verified_count': len([p for p in results if p['is_verified']])
            }
            
        except Exception as e:
            _logger.error(f"Error in batch verification: {str(e)}")
            return {'error': 'Batch verification failed'}