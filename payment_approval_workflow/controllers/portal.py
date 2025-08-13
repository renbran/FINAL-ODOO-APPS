import base64
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from werkzeug.security import safe_str_cmp as consteq
import logging

_logger = logging.getLogger(__name__)


class PaymentVerificationController(http.Controller):
    """Public controller for payment verification via QR codes"""

    @http.route(['/payment/verify/<string:token>'], type='http', auth='public', 
                website=True, csrf=False)
    def payment_verification(self, token, **kwargs):
        """
        Public route for payment verification using QR token
        """
        try:
            # Search for payment with the given verification token
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return request.render('payment_approval_workflow.payment_not_found', {
                    'page_name': _('Payment Verification'),
                })
            
            # Prepare data for the template
            verification_data = {
                'payment': payment,
                'partner_name': payment.partner_id.name,
                'amount': payment.amount,
                'currency': payment.currency_id,
                'payment_date': payment.date,
                'reference': payment.ref or payment.name,
                'state_display': dict(payment._fields['approval_state'].selection).get(payment.approval_state),
                'company': payment.company_id,
                'page_name': _('Payment Verification'),
            }
            
            return request.render('payment_approval_workflow.payment_verification_template', 
                                verification_data)
                                
        except Exception as e:
            _logger.error("Error in payment verification: %s", str(e))
            return request.render('payment_approval_workflow.payment_verification_error', {
                'page_name': _('Payment Verification Error'),
                'error_message': _('An error occurred while verifying the payment.'),
            })

    @http.route(['/payment/verify/qr/<string:token>'], type='http', auth='public', 
                website=True, csrf=False)
    def payment_qr_code(self, token, **kwargs):
        """
        Generate QR code image for payment verification
        """
        try:
            payment = request.env['account.payment'].sudo().search([
                ('verification_token', '=', token)
            ], limit=1)
            
            if not payment:
                return request.not_found()
            
            qr_code_data = payment._generate_qr_code()
            if qr_code_data:
                return request.make_response(
                    base64.b64decode(qr_code_data),
                    headers=[
                        ('Content-Type', 'image/png'),
                        ('Content-Disposition', f'inline; filename="payment_qr_{token}.png"'),
                        ('Cache-Control', 'public, max-age=3600'),
                    ]
                )
            
            return request.not_found()
            
        except Exception as e:
            _logger.error("Error generating QR code: %s", str(e))
            return request.not_found()


class PaymentPortalController(CustomerPortal):
    """Portal controller for authenticated payment access"""

    @http.route(['/my/payments', '/my/payments/page/<int:page>'], 
                type='http', auth="user", website=True)
    def portal_my_payments(self, page=1, date_begin=None, date_end=None, 
                          sortby=None, filterby=None, search=None, search_in='content', **kw):
        """
        Customer portal page to view their payments
        """
        values = self._prepare_portal_layout_values()
        
        # Get payments for current user's partners
        partner_ids = request.env.user.partner_id.ids
        if request.env.user.partner_id.child_ids:
            partner_ids.extend(request.env.user.partner_id.child_ids.ids)
        
        domain = [('partner_id', 'in', partner_ids)]
        
        # Apply date filters
        if date_begin and date_end:
            domain += [('date', '>=', date_begin), ('date', '<=', date_end)]
        
        # Search functionality
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = ['|', ('name', 'ilike', search), ('ref', 'ilike', search)]
            domain += search_domain
        
        # Count payments
        payment_count = request.env['account.payment'].search_count(domain)
        
        # Pagination
        pager = request.website.pager(
            url="/my/payments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 
                     'sortby': sortby, 'filterby': filterby, 'search': search, 
                     'search_in': search_in},
            total=payment_count,
            page=page,
            step=self._items_per_page
        )
        
        # Get payments
        payments = request.env['account.payment'].search(
            domain, 
            order='date desc, id desc',
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        values.update({
            'payments': payments,
            'page_name': 'payment',
            'pager': pager,
            'default_url': '/my/payments',
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
        })
        
        return request.render("payment_approval_workflow.portal_my_payments", values)

    @http.route(['/my/payments/<int:payment_id>'], type='http', auth="user", website=True)
    def portal_payment_page(self, payment_id=None, report_type=None, access_token=None, **kw):
        """
        Individual payment page in customer portal
        """
        try:
            payment_sudo = self._document_check_access('account.payment', payment_id, access_token)
        except Exception:
            return request.redirect('/my')
        
        values = {
            'payment': payment_sudo,
            'page_name': 'payment',
        }
        
        return request.render("payment_approval_workflow.portal_payment_page", values)

    def _document_check_access(self, model_name, document_id, access_token=None):
        """
        Check access rights for document
        """
        document = request.env[model_name].browse([document_id])
        document_sudo = document.sudo()
        
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except Exception:
            if not access_token or not document_sudo.access_token or \
               not consteq(document_sudo.access_token, access_token):
                raise
        
        return document_sudo
