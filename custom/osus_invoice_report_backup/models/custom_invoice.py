from odoo import models, fields, api
import base64
import qrcode
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'

    # QR Code fields
    qr_in_report = fields.Boolean(string='Show QR Code in Report', default=True)
    qr_image = fields.Binary(string='QR Code Image', compute='_compute_qr_code')
    
    # Deal tracking fields
    booking_date = fields.Date(string='Booking Date', help="Date when the property booking was confirmed")
    deal_id = fields.Char(string='Deal ID', help="Internal reference ID for the real estate deal")
    sale_value = fields.Monetary(string='Sale Value', currency_field='currency_id', help="Total value of the property sale")
    developer_commission = fields.Float(string='Developer Commission %', digits=(16, 2), help="Commission percentage for this deal")
    buyer = fields.Many2one('res.partner', string='Buyer', help="The buyer of the property")
    project = fields.Char(string='Project Name', help="The real estate project this deal belongs to")
    unit = fields.Char(string='Unit', help="The specific property unit in this deal")
    
    # Amount in words field
    amount_total_words = fields.Char(string='Amount in Words', compute='_compute_amount_total_words')

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for record in self:
            record.amount_total_words = record._amount_to_words(record.amount_total)

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