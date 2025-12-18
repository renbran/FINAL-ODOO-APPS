from odoo import fields, api, models


class BookingWizard(models.TransientModel):
    _name = 'booking.wizard'
    _description = 'Create Booking While Property on Sale'

    customer_id = fields.Many2one('res.partner', string='Customer', domain="[('user_type','=','customer')]")
    property_id = fields.Many2one('property.details', string='Property')
    price = fields.Monetary(related="property_id.price")
    dld_fee = fields.Monetary(related="property_id.dld_fee", string="DLD Fee (4%)")
    admin_fee = fields.Monetary(related="property_id.admin_fee", string="Admin Fee")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    book_price = fields.Monetary(string="Advance")
    ask_price = fields.Monetary(string="Customer Price")
    sale_price = fields.Monetary(related="property_id.sale_price", string="Sale Price")
    is_any_broker = fields.Boolean(string='Any Broker?')
    broker_id = fields.Many2one('res.partner', string='Broker', domain=[('user_type', '=', 'broker')])
    commission_type = fields.Selection([('f', 'Fix'), ('p', 'Percentage')], string="Commission Type")
    broker_commission = fields.Monetary(string='Commission')
    broker_commission_percentage = fields.Float(string='Percentage')
    commission_from = fields.Selection([('customer', 'Customer'),
                                        ('landlord', 'Landlord',)],
                                       default='customer', string="Commission From")
    from_inquiry = fields.Boolean('From Enquiry')
    note = fields.Text(string="Note", translate=True)
    lead_id = fields.Many2one('crm.lead', string="Enquiry", domain="[('property_id','=',property_id)]")

    # Maintenance and utility Service
    is_any_maintenance = fields.Boolean(related="property_id.is_maintenance_service")
    total_maintenance = fields.Monetary(related="property_id.total_maintenance")
    is_utility_service = fields.Boolean(related="property_id.is_extra_service")
    total_service = fields.Monetary(related="property_id.extra_service_cost")

    # Booking Item
    booking_item_id = fields.Many2one('product.product', string="Booking Item")
    broker_item_id = fields.Many2one('product.product', string="Broker Item")

    # Deprecated
    inquiry_id = fields.Many2one('sale.inquiry', string="Enquiry ")

    @api.model
    def default_get(self, fields):
        res = super(BookingWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        property_id = self.env['property.details'].browse(active_id)
        default_broker_item = self.env['ir.config_parameter'].sudo().get_param(
            'rental_management.account_broker_item_id')
        default_deposit_item = self.env['ir.config_parameter'].sudo().get_param(
            'rental_management.account_deposit_item_id')
        res['property_id'] = property_id.id
        # Customer Price = Property Price + DLD Fee + Admin Fee (Total Customer Obligation)
        if property_id.sale_lease == 'for_sale':
            res['ask_price'] = property_id.total_customer_obligation or property_id.price
        else:
            res['ask_price'] = property_id.price
        res['booking_item_id'] = int(default_deposit_item) if default_deposit_item else self.env.ref(
            'rental_management.property_product_2').id
        res['broker_item_id'] = int(default_broker_item) if default_broker_item else self.env.ref(
            'rental_management.property_product_3').id
        return res

    def create_booking_action(self):
        invoice_post_type = self.env['ir.config_parameter'].sudo().get_param('rental_management.invoice_post_type')
        self.customer_id.user_type = "customer"
        lead = self._context.get('from_crm')
        
        # Prepare contract data with payment schedule inheritance
        data = {
            'customer_id': self.customer_id.id,
            'property_id': self.property_id.id,
            'book_price': self.book_price * (-1),
            'ask_price': self.ask_price,
            'sale_price': self.ask_price,  # Set sale_price to total customer obligation
            'is_any_broker': self.is_any_broker,
            'broker_id': self.broker_id.id,
            'commission_type': self.commission_type,
            'broker_commission': self.broker_commission,
            'broker_commission_percentage': self.broker_commission_percentage,
            'stage': 'draft',  # Start in 'draft' stage - will move to 'booked' after payment
            'commission_from': self.commission_from,
            'booking_item_id': self.booking_item_id.id,
            'broker_item_id': self.broker_item_id.id,
        }
        
        # Inherit payment schedule from property if available
        if self.property_id.is_payment_plan and self.property_id.payment_schedule_id:
            data.update({
                'payment_schedule_id': self.property_id.payment_schedule_id.id,
                'use_schedule': True,
                'schedule_from_property': True,
            })
        
        # Pass DLD and Admin fees to contract (they will be auto-calculated but we ensure values)
        if self.property_id.sale_lease == 'for_sale':
            data.update({
                'dld_fee': self.dld_fee,
                'admin_fee': self.admin_fee,
                'include_dld_in_plan': True,
                'include_admin_in_plan': True,
                # Inherit booking configuration from property
                'booking_percentage': self.property_id.booking_percentage or 10.0,
                'booking_type': self.property_id.booking_type or 'percentage',
            })
        booking_id = self.env['property.vendor'].create(data)
        self.property_id.sold_booking_id = booking_id.id
        
        # Send booking confirmation email
        mail_template = self.env.ref(
            'rental_management.property_book_mail_template')
        if mail_template:
            mail_template.send_mail(booking_id.id, force_send=True)
        
        # Automatically generate booking invoices (booking + DLD + admin fees)
        # These must be paid before client can proceed with installment plan
        booking_id.action_generate_booking_invoices()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Booking',
            'res_model': 'property.vendor',
            'res_id': booking_id.id,
            'view_mode': 'form,tree',
            'target': 'current'
        }

    @api.onchange('from_inquiry')
    def _onchange_property_sale_inquiry(self):
        inquiry_ids = self.env['sale.inquiry'].search(
            [('property_id', '=', self.property_id.id)]).mapped('id')
        for rec in self:
            if not rec.from_inquiry:
                return
            return {'domain': {'inquiry_id': [('id', 'in', inquiry_ids)]}}

    @api.onchange('lead_id')
    def _onchange_ask_price(self):
        for rec in self:
            if not rec.from_inquiry and not rec.lead_id:
                return
            rec.ask_price = rec.lead_id.ask_price
            rec.note = rec.lead_id.description
            rec.customer_id = rec.lead_id.partner_id.id
