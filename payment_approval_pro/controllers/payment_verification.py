# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PaymentVerificationController(http.Controller):
    """
    Controller for QR code verification of payments
    """

    @http.route('/payment/verify/<string:token>', type='http', auth='public', website=True)
    def verify_payment(self, token, **kwargs):
        """
        Verify payment using QR verification token
        """
        try:
            # Search for payment with matching token
            payment = request.env['account.payment'].sudo().search([
                ('qr_verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return request.render('payment_approval_pro.payment_verification_error', {
                    'error': 'Invalid verification token',
                    'message': 'The payment verification link is invalid or expired.'
                })
            
            # Prepare verification data
            verification_data = {
                'payment': payment,
                'verified': True,
                'verification_time': http.datetime.now(),
                'company': payment.company_id,
            }
            
            return request.render('payment_approval_pro.payment_verification_success', verification_data)
            
        except Exception as e:
            return request.render('payment_approval_pro.payment_verification_error', {
                'error': 'Verification failed',
                'message': f'An error occurred during verification: {str(e)}'
            })

    @http.route('/payment/verify', type='http', auth='public', website=True)
    def verify_payment_form(self, **kwargs):
        """
        Show payment verification form
        """
        return request.render('payment_approval_pro.payment_verification_form', {})

    @http.route('/payment/verify/check', type='http', auth='public', website=True, methods=['POST'])
    def check_payment_verification(self, token=None, **kwargs):
        """
        Check payment verification via form submission
        """
        if not token:
            return request.render('payment_approval_pro.payment_verification_error', {
                'error': 'Missing token',
                'message': 'Please provide a verification token.'
            })
        
        return self.verify_payment(token, **kwargs)
