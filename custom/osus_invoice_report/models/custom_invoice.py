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

    # Deal Information Fields - These fields are defined in commission modules
    # We don't define them here to avoid conflicts with commission_fields and advance_commission modules
    # The fields are: booking_date, deal_id, sale_value, developer_commission, buyer_id, project_id, unit_id

    # Computed fields for enhanced tree view
    is_property_deal = fields.Boolean(
        string='Is Property Deal',
        compute='_compute_deal_status',
        store=True,
        help="Indicates if this invoice is related to a property deal"
    )
    commission_amount = fields.Monetary(
        string='Commission Amount',
        compute='_compute_commission_amount',
        store=True,
        currency_field='currency_id',
        help="Calculated commission amount based on sale value and percentage"
    )

    @api.depends('name', 'partner_id', 'amount_total', 'invoice_date', 'qr_in_report')
    def _compute_qr_code(self):
        for record in self:
            # Skip QR code generation for cancelled records
            if record.state == 'cancel':
                record.qr_image = False
                continue
                
            if not record.qr_in_report:
                record.qr_image = False
                continue
                
            try:
                if record.name and record.partner_id:
                    portal_url = record._get_portal_url()
                    record.qr_image = self._generate_qr_code(portal_url)
                else:
                    record.qr_image = False
            except Exception as e:
                _logger.error("Error generating QR code for %s: %s", record.name, str(e))
                record.qr_image = False

    def _get_portal_url(self):
        """Generate portal URL for secure access to the document"""
        try:
            # Get the base URL of the Odoo instance
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                base_url = 'http://localhost:8069'  # Fallback URL
            
            # Generate the portal URL with access token for the invoice
            # This uses Odoo's built-in method which automatically includes the access token
            relative_url = self.get_portal_url()
            
            # Combine the base URL with the relative URL
            full_url = base_url + relative_url
            
            _logger.info("Generated portal URL for %s: %s", self.name, full_url)
            return full_url
        except Exception as e:
            _logger.error("Error generating portal URL for %s: %s", self.name, str(e))
            # Fallback to manual URL construction if portal URL fails
            return self._get_manual_portal_url()

    def _get_manual_portal_url(self):
        """Generate manual portal URL as fallback"""
        try:
            # Get the base URL of the Odoo instance
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                base_url = 'http://localhost:8069'  # Fallback URL
            
            # Get or create access token
            access_token = self._portal_ensure_token()
            
            # Construct the portal URL manually
            portal_url = f"{base_url}/my/invoices/{self.id}?access_token={access_token}"
            
            _logger.info("Generated manual portal URL for %s: %s", self.name, portal_url)
            return portal_url
        except Exception as e:
            _logger.error("Error generating manual portal URL for %s: %s", self.name, str(e))
            # Final fallback to informational content
            return self._get_qr_content_fallback()

    def _get_qr_content_fallback(self):
        """Generate QR code content with real estate deal information as fallback"""
        content_lines = [
            f"Invoice: {self.name}",
            f"Company: {self.company_id.name}",
            f"Partner: {self.partner_id.name}",
            f"Amount: {self.amount_total} {self.currency_id.name}",
            f"Date: {self.invoice_date or ''}",
        ]
        
        # Add real estate specific information if available
        # These fields come from commission modules
        if hasattr(self, 'buyer_id') and self.buyer_id:
            content_lines.append(f"Buyer: {self.buyer_id.name}")
        if hasattr(self, 'project_id') and self.project_id:
            content_lines.append(f"Project: {self.project_id.name}")
        if hasattr(self, 'unit_id') and self.unit_id:
            content_lines.append(f"Unit: {self.unit_id.name}")
        if hasattr(self, 'deal_id') and self.deal_id:
            content_lines.append(f"Deal ID: {self.deal_id}")
        if hasattr(self, 'sale_value') and self.sale_value:
            content_lines.append(f"Sale Value: {self.sale_value} {self.currency_id.name}")
        
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
    def _ensure_base_url_configured(self):
        """Ensure the base URL is correctly configured for QR code generation"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not base_url or base_url == 'http://localhost:8069':
            _logger.warning("Base URL not properly configured. QR codes may not work correctly.")
            return False
        return True

    def get_qr_code_url(self):
        """Public method to get the QR code URL for testing purposes"""
        return self._get_portal_url()

    def regenerate_qr_code(self):
        """Manually regenerate QR code for this invoice"""
        self._compute_qr_code()
        return True

    @api.model
    def create(self, vals):
        if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('invoice_origin'):
            self._populate_from_sale_order(vals)
        return super().create(vals)

    def _populate_from_sale_order(self, vals):
        # Ensure we only fetch active (non-cancelled) sale orders
        sale_order = self.env['sale.order'].search([
            ('name', '=', vals.get('invoice_origin')),
            ('state', '!=', 'cancel')  # Exclude cancelled orders
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

    def _compute_deal_status(self):
        """Compute if this is a property deal based on available deal information"""
        for record in self:
            # Check if deal-related fields exist (they come from commission modules)
            has_buyer = hasattr(record, 'buyer_id') and record.buyer_id
            has_project = hasattr(record, 'project_id') and record.project_id
            has_unit = hasattr(record, 'unit_id') and record.unit_id
            has_deal_id = hasattr(record, 'deal_id') and record.deal_id
            has_booking_date = hasattr(record, 'booking_date') and record.booking_date
            
            record.is_property_deal = bool(
                has_buyer or has_project or has_unit or has_deal_id or has_booking_date
            )

    def _compute_commission_amount(self):
        """Compute commission amount from sale value and percentage"""
        for record in self:
            # Check if commission fields exist (they come from commission modules)
            sale_value = getattr(record, 'sale_value', 0) if hasattr(record, 'sale_value') else 0
            commission_pct = getattr(record, 'developer_commission', 0) if hasattr(record, 'developer_commission') else 0
            
            if sale_value and commission_pct:
                record.commission_amount = (sale_value * commission_pct) / 100
            else:
                record.commission_amount = 0.0

    @api.model
    def _get_active_records_domain(self):
        """Return domain to filter out cancelled records"""
        return [('state', '!=', 'cancel')]

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Override search to exclude cancelled records by default"""
        # Add active filter if not explicitly searching for cancelled records
        if not any('state' in str(arg) for arg in args if isinstance(arg, (list, tuple))):
            args = args + self._get_active_records_domain()
        return super().search(args, offset=offset, limit=limit, order=order, count=count)