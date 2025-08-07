from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    
    @http.route('/payment/verify/<int:payment_id>', type='http', auth='public', website=True)
    def verify_payment(self, payment_id):
        """Verify payment via QR code scan"""
        try:
            payment = request.env['account.payment'].sudo().browse(payment_id)
            
            if not payment.exists():
                return self._render_error(
                    'Payment Not Found',
                    'The payment voucher you are trying to verify does not exist.',
                    'PAYMENT_NOT_FOUND'
                )
            
            # Prepare verification data
            verification_data = {
                'voucher_number': payment.voucher_number or payment.name,
                'payment_reference': payment.ref or 'N/A',
                'amount': f"{payment.amount:,.2f}",
                'currency': payment.currency_id.name or 'USD',
                'partner_name': payment.partner_id.name or 'N/A',
                'payment_date': payment.date.strftime('%d %B %Y') if payment.date else 'N/A',
                'state': payment.approval_state,
                'payment_type_display': 'Receipt' if payment.payment_type == 'inbound' else 'Payment',
                'journal_name': payment.journal_id.name or 'N/A',
                'company_name': payment.company_id.name,
                'is_verified': payment.approval_state == 'posted',
                'verification_timestamp': request.env.context.get('tz_offset', 'UTC'),
            }
            
            return request.render('osus_payment_voucher.payment_verification_success', verification_data)
            
        except Exception as e:
            _logger.error(f"Error verifying payment {payment_id}: {e}")
            return self._render_error(
                'Verification Error',
                'An error occurred while verifying the payment. Please try again or contact support.',
                'VERIFICATION_ERROR'
            )
    
    @http.route('/payment/qr-guide', type='http', auth='public', website=True)
    def qr_verification_guide(self):
        """Display QR code verification guide"""
        try:
            company = request.env.company
            return request.render('osus_payment_voucher.qr_verification_guide', {
                'company_name': company.name,
            })
        except Exception as e:
            _logger.error(f"Error loading QR guide: {e}")
            return self._render_error(
                'Page Not Available',
                'The QR verification guide is temporarily unavailable.',
                'GUIDE_ERROR'
            )
    
    def _render_error(self, title, message, error_code):
        """Render error page"""
        return request.render('osus_payment_voucher.payment_verification_error', {
            'error_title': title,
            'error_message': message,
            'error_code': error_code,
        })  