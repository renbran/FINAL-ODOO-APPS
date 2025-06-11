# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import qrcode
from io import BytesIO

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    qr_code = fields.Binary("QR Code", compute="_compute_qr_code", store=False)

    def _compute_qr_code(self):
        for rec in self:
            url = rec._get_portal_url()
            if url:
                qr = qrcode.QRCode(box_size=4, border=2)
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                rec.qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.qr_code = False

    def _get_portal_url(self):
        self.ensure_one()
        return self.get_portal_url() if hasattr(self, 'get_portal_url') else False
