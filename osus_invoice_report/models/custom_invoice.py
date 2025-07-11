from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    # Deal Tracking Fields
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
        string='Developer Commission %',
        tracking=True,
        digits=(16, 2),
        help="Commission percentage for this deal"
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="The buyer of the property"
    )
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        help="The real estate project this deal belongs to"
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        help="The specific property unit in this deal"
    )
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

    @api.depends()
    def _compute_qr_code(self):
        # Dummy implementation, replace with actual QR code logic
        for record in self:
            record.qr_image = False

    def action_print_custom_invoice(self):
        return self.env.ref('osus_invoice_report.action_report_custom_invoice').report_action(self)

    def action_print_custom_bill(self):
        return self.env.ref('osus_invoice_report.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        return self.env.ref('osus_invoice_report.action_report_custom_receipt').report_action(self)