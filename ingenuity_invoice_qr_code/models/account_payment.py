# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
import qrcode
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)


def generate_qr_code_payment(value):
    """Generate QR code for payment data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4
    )
    qr.add_data(value)
    qr.make(fit=True)
    img = qr.make_image()
    stream = BytesIO()
    img.save(stream, format="PNG")
    qr_img = base64.b64encode(stream.getvalue())
    return qr_img


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    qr_code = fields.Binary("Payment QR Code", compute='_generate_payment_qr_code')
    qr_in_report = fields.Boolean('Display QR Code in Payment Report?', default=True)

    @api.depends('name', 'partner_id', 'amount', 'date', 'payment_type', 'qr_in_report')
    def _generate_payment_qr_code(self):
        """Generate QR code for payment information"""
        for payment in self:
            if not payment.qr_in_report:
                payment.qr_code = False
                continue
                
            try:
                # Create payment information for QR code
                qr_content_lines = [
                    f"Payment: {payment.name or 'N/A'}",
                    f"Type: {'Receipt' if payment.payment_type == 'inbound' else 'Payment'}",
                    f"Partner: {payment.partner_id.name if payment.partner_id else 'N/A'}",
                    f"Amount: {payment.amount} {payment.currency_id.name if payment.currency_id else ''}",
                    f"Date: {payment.date or ''}",
                ]
                
                if payment.ref:
                    qr_content_lines.append(f"Reference: {payment.ref}")
                    
                if payment.company_id:
                    qr_content_lines.append(f"Company: {payment.company_id.name}")
                
                qr_content = '\n'.join(qr_content_lines)
                
                # Generate the QR code
                qr_img = generate_qr_code_payment(qr_content)
                
                # Write the generated QR code image to the record
                payment.qr_code = qr_img
                _logger.info("QR code generated for payment %s", payment.name)
                
            except Exception as e:
                _logger.error("Error generating QR code for payment %s: %s", payment.name, str(e))
                payment.qr_code = False
