from odoo import models, fields, api
import base64
import qrcode
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'

    qr_in_report = fields.Boolean(string='Show QR Code in Report', default=True)
    qr_image = fields.Binary(string='QR Code Image', compute='_compute_qr_code')

    @api.depends('name', 'partner_id', 'amount_total')
    def _compute_qr_code(self):
        for record in self:
            if record.name and record.partner_id:
                # Create QR code content (you can customize this)
                qr_content = f"Invoice: {record.name}\nVendor: {record.partner_id.name}\nAmount: {record.amount_total} AED"
                
                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(qr_content)
                qr.make(fit=True)
                
                # Create QR code image
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                qr_image_base64 = base64.b64encode(buffer.getvalue())
                
                record.qr_image = qr_image_base64
            else:
                record.qr_image = False

    def _amount_to_words(self, amount):
        # Basic implementation - you can enhance this or use a library
        try:
            from num2words import num2words
            words = num2words(amount, lang='en')
            return f"{words.title()} AED Only"
        except ImportError:
            # Fallback if num2words is not available
            return f"{amount:.2f} AED"

    def action_print_custom_invoice(self):
        self.ensure_one()
        return self.env.ref('osus_invoice_report.action_report_custom_invoice').report_action(self)

    def action_print_custom_bill(self):
        self.ensure_one()
        return self.env.ref('osus_invoice_report.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        self.ensure_one()
        return self.env.ref('osus_invoice_report.action_report_custom_receipt').report_action(self)