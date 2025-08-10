import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    
    @http.route('/payment/verify/<string:token>', type='http', auth='public', website=True)
    def verify_payment(self, token, **kwargs):
        """Public payment verification via QR code"""
        try:
            # Find payment by verification token
            payment = request.env['account.payment'].sudo().search([
                ('qr_verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return request.render('payment_voucher_enhanced.payment_verification_error', {
                    'error_message': _('Payment Not Found'),
                    'error_details': _('The payment verification link is invalid or expired.'),
                })
            
            # Prepare verification data
            verification_data = {
                'payment': payment,
                'voucher_number': payment.voucher_number or payment.name,
                'partner_name': payment.partner_id.name,
                'amount': payment.amount,
                'currency': payment.currency_id.name,
                'date': payment.date.strftime('%B %d, %Y') if payment.date else '',
                'status': payment.approval_state,
                'company_name': payment.company_id.name,
                'is_posted': payment.approval_state == 'posted',
                'verification_date': http.request.env.context.get('tz', 'UTC'),
            }
            
            return request.render('payment_voucher_enhanced.payment_verification_success', verification_data)
            
        except Exception as e:
            _logger.error(f"Payment verification error: {e}")
            return request.render('payment_voucher_enhanced.payment_verification_error', {
                'error_message': _('Verification Error'),
                'error_details': _('An error occurred while verifying the payment. Please contact support.'),
            })
    
    @http.route('/payment/verify/guide', type='http', auth='public', website=True)
    def verification_guide(self, **kwargs):
        """QR code verification guide"""
        return request.render('payment_voucher_enhanced.qr_verification_guide', {
            'company_name': request.env.company.name,
        })