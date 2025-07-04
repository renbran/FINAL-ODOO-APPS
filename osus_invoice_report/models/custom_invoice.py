from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import qrcode
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # QR Code fields
    qr_in_report = fields.Boolean(
        string='Show QR Code in Report',
        default=True,
        help="Enable to display QR code on generated documents"
    )
    qr_image = fields.Binary(
        string='QR Code Image',
        compute='_compute_qr_code',
        store=True,
        help="Automatically generated QR code for this document"
    )
    
    amount_total_words = fields.Char(
        string='Total Amount in Words',
        compute='_compute_amount_total_words',
        help="The total amount expressed in words"
    )

    # Deal Information Fields
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="Date when the property booking was confirmed"
    )
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
        help="Internal reference ID for the real estate deal"
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="Total value of the property sale"
    )
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits=(16, 2),
        help="Commission percentage for this deal"
    )

    # Relational Fields
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        domain="[('is_buyer', '=', True)]",
        help="The buyer of the property"
    )
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        domain="[('is_property', '=', True)]",
        help="The real estate project this deal belongs to"
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        domain="[('product_tmpl_id', '=', project_id)]",
        help="The specific property unit in this deal"
    )

    @api.depends('name', 'partner_id', 'amount_total', 'invoice_date', 'qr_in_report', 'buyer_id', 'project_id', 'unit_id')
    def _compute_qr_code(self):
        for record in self:
            if not record.qr_in_report:
                record.qr_image = False
                continue
                
            try:
                if record.name and record.partner_id:
                    qr_content = self._get_qr_content(record)
                    record.qr_image = self._generate_qr_code(qr_content)
                else:
                    record.qr_image = False
            except Exception as e:
                _logger.error("Error generating QR code for %s: %s", record.name, str(e))
                record.qr_image = False

    def _get_qr_content(self, record):
        """Generate QR code content with real estate deal information"""
        content_lines = [
            f"Invoice: {record.name}",
            f"Company: {record.company_id.name}",
            f"Partner: {record.partner_id.name}",
            f"Amount: {record.amount_total} {record.currency_id.name}",
            f"Date: {record.invoice_date or ''}",
        ]
        
        # Add real estate specific information if available
        if record.buyer_id:
            content_lines.append(f"Buyer: {record.buyer_id.name}")
        if record.project_id:
            content_lines.append(f"Project: {record.project_id.name}")
        if record.unit_id:
            content_lines.append(f"Unit: {record.unit_id.name}")
        if record.deal_id:
            content_lines.append(f"Deal ID: {record.deal_id}")
        if record.sale_value:
            content_lines.append(f"Sale Value: {record.sale_value} {record.currency_id.name}")
        
        return '\n'.join(content_lines)

    def _generate_qr_code(self, content):
        """Generate QR code image from content"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue())
        except Exception as e:
            _logger.error("Error generating QR code image: %s", str(e))
            return False

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for record in self:
            try:
                record.amount_total_words = record._amount_to_words(record.amount_total)
            except Exception as e:
                _logger.error("Error converting amount to words: %s", str(e))
                record.amount_total_words = _("Amount in words unavailable")

    def _amount_to_words(self, amount):
        try:
            from num2words import num2words
            words = num2words(amount, lang='en').title()
            return f"{words} {self.currency_id.name or 'AED'} Only"
        except ImportError:
            _logger.warning("num2words library not found, using simple amount display")
            return f"{amount:.2f} {self.currency_id.name or 'AED'}"

    @api.constrains('developer_commission')
    def _check_developer_commission(self):
        for record in self:
            if record.developer_commission < 0 or record.developer_commission > 100:
                raise ValidationError(_("Commission percentage must be between 0 and 100"))

    @api.model
    def create(self, vals):
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            self._populate_from_sale_order(vals)
        return super().create(vals)

    def _populate_from_sale_order(self, vals):
        sale_order = self.env['sale.order'].search([
            ('name', '=', vals.get('invoice_origin'))
        ], limit=1)
        
        if sale_order:
            field_map = {
                'booking_date': 'booking_date',
                'developer_commission': 'developer_commission',
                'buyer_id': 'buyer_id',
                'deal_id': 'deal_id',
                'project_id': 'project_id',
                'sale_value': 'sale_value',
                'unit_id': 'unit_id',
            }
            
            for invoice_field, sale_field in field_map.items():
                if sale_field in sale_order._fields and invoice_field not in vals:
                    vals[invoice_field] = sale_order[sale_field].id if hasattr(sale_order[sale_field], 'id') else sale_order[sale_field]