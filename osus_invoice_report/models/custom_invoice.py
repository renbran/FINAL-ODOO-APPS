from odoo import models, fields, api
import base64
import qrcode
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    qr_in_report = fields.Boolean(string='Show QR Code in Report', default=True)
    qr_image = fields.Binary(string='QR Code Image', compute='_compute_qr_code')
    booking_date = fields.Date(string='Booking Date')
    buyer = fields.Many2one('res.partner', string='Buyer')
    project = fields.Many2one('project.project', string='Project')
    unit = fields.Char(string='Unit')
    sale_value = fields.Float(string='Sale Value', compute='_compute_sale_value')
    amount_total_words = fields.Char(string='Amount in Words', compute='_compute_amount_words')
    
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
    
    @api.depends('invoice_line_ids')
    def _compute_sale_value(self):
        for record in self:
            # Calculate sale value based on your business logic
            if record.invoice_line_ids:
                record.sale_value = sum(line.price_unit for line in record.invoice_line_ids)
            else:
                record.sale_value = 0.0
    
    def _compute_amount_words(self):
        for record in self:
            # Convert amount to words (you might want to use a library for this)
            record.amount_total_words = self._amount_to_words(record.amount_total)
    
    def _amount_to_words(self, amount):
        # Basic implementation - you can enhance this or use a library
        try:
            from num2words import num2words
            words = num2words(amount, lang='en')
            return f"{words.title()} AED Only"
        except ImportError:
            # Fallback if num2words is not available
            return f"{amount:.2f} AED"