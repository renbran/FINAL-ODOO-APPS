from odoo import models, fields, api
import base64
import qrcode
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'

    # QR Code fields (existing)
    qr_in_report = fields.Boolean(string='Show QR Code in Report', default=True)
    qr_image = fields.Binary(string='QR Code Image', compute='_compute_qr_code')
    
    # Real Estate Deal Information Fields (merged from custom_fields)
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
    )
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
    )
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits=(16, 2),
    )

    # Relational Fields
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
    )
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        domain="[('product_tmpl_id', '=', project_id)]",
    )

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

    @api.model
    def create(self, vals):
        # Auto-populate real estate fields from sale order if creating from invoice
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([
                ('name', '=', vals.get('invoice_origin'))
            ], limit=1)
            if sale_order:
                vals.update({
                    'booking_date': sale_order.booking_date,
                    'developer_commission': sale_order.developer_commission,
                    'buyer_id': sale_order.buyer_id.id if sale_order.buyer_id else False,
                    'deal_id': sale_order.deal_id,
                    'project_id': sale_order.project_id.id if sale_order.project_id else False,
                    'sale_value': sale_order.sale_value,
                    'unit_id': sale_order.unit_id.id if sale_order.unit_id else False,
                })
        return super(AccountMove, self).create(vals)