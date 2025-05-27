from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class PropertyProperty(models.Model):
    _name = 'property.property'
    _description = 'Property Details'
    _order = 'name'
    
    # Constants for state values
    STATE_AVAILABLE = 'available'
    STATE_RESERVED = 'reserved'
    STATE_BOOKED = 'booked'
    STATE_SOLD = 'sold'

    # Basic Information
    name = fields.Char(string="Property Name", required=True)
    property_reference = fields.Char(string="Property Reference")
    description = fields.Text(string="Description")
    property_type = fields.Char(string="Property Type")
    currency_id = fields.Many2one(
        'res.currency', 
        string="Currency", 
        required=True, 
        default=lambda self: self.env.company.currency_id
    )

    # Media Fields
    property_image = fields.Image("Main Image")
    floor_plan = fields.Image("Floor Plan")
    sale_offer_image = fields.Image("Sale Offer Image")

    # Location Information
    address = fields.Text(string="Full Address")
    tower = fields.Char(string="Tower/Building")
    level = fields.Char(string="Floor Level")
    unit_no = fields.Char(string="Unit Number")
    unit_view = fields.Char(string="View Direction")

    # Pricing Details
    property_price = fields.Monetary(string="Listing Price", required=True)
    total_sqft = fields.Float(string="Total Square Feet")
    price_per_sqft = fields.Float(string="Price per SqFt", compute="_compute_price_per_sqft", store=True)
    total_sale_value = fields.Float(string="Total Value", compute="_compute_total_sale_value", store=True)

    # Relations
    partner_id = fields.Many2one('res.partner', string="Owner/Partner")
    property_sale_offer_ids = fields.One2many(
        'property.sale.offer', 
        'property_id', 
        string="Sale Offers"
    )
    property_sale_ids = fields.One2many(
        'property.sale', 
        'property_id', 
        string="Completed Sales"
    )

    # Status Tracking
    sale_rent = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], string="Transaction Type", required=True, default='for_sale')

    state = fields.Selection([
        (STATE_AVAILABLE, 'Available'),
        (STATE_RESERVED, 'Reserved'),
        (STATE_BOOKED, 'Booked'),
        (STATE_SOLD, 'Sold')
    ], string="Status", default=STATE_AVAILABLE, tracking=True)

    status = fields.Char(
        string="Status Display", 
        compute="_compute_status", 
        store=True
    )

    # Financial Tracking
    payment_progress = fields.Float(
        string="Payment Progress", 
        compute="_compute_payment_progress", 
        store=True
    )
    total_invoiced = fields.Monetary(
        string="Total Invoiced", 
        compute="_compute_payment_details", 
        store=True
    )
    total_paid = fields.Monetary(
        string="Total Received", 
        compute="_compute_payment_details", 
        store=True
    )
    remaining_amount = fields.Monetary(
        string="Pending Amount", 
        compute="_compute_payment_details", 
        store=True
    )

    # Smart Counters
    offer_count = fields.Integer(
        string="Offers Count", 
        compute="_compute_offer_count"
    )
    sale_count = fields.Integer(
        string="Sales Count", 
        compute="_compute_sale_count"
    )

    # Accounting
    revenue_account_id = fields.Many2one(
        'account.account',
        string="Revenue Account",
        domain=[('account_type', '=', 'income')],
        default=lambda self: self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('name', 'ilike', 'sales')
        ], limit=1),
        context="{'no_create': True}"
    )
    
    # Project Information
    project_name = fields.Char(
        string="Project Name", 
        default="Sky Hills Astra"
    )
    active_sale_id = fields.Many2one(
        'property.sale', 
        string="Active Sale", 
        compute="_compute_active_sale"
    )
    broker_commission_count = fields.Integer(
    string="Commission Count", 
    compute='_compute_broker_commission_count'
    )

    # Computed Methods
    @api.depends('total_sqft', 'property_price')
    def _compute_price_per_sqft(self):
        for prop in self:
            prop.price_per_sqft = prop.property_price / prop.total_sqft if prop.total_sqft > 0 else 0

    @api.depends('total_sqft', 'price_per_sqft')
    def _compute_total_sale_value(self):
        for prop in self:
            prop.total_sale_value = prop.total_sqft * prop.price_per_sqft
    def _compute_broker_commission_count(self):
        for prop in self:
            prop.broker_commission_count = len(
                self.env['broker.commission.invoice'].search([
                    ('property_sale_id.property_id', '=', prop.id)
                ])
            )

    @api.depends('state')
    def _compute_status(self):
        status_map = {
            self.STATE_AVAILABLE: 'Available',
            self.STATE_RESERVED: 'Reserved',
            self.STATE_BOOKED: 'Booked',
            self.STATE_SOLD: 'Sold'
        }
        for prop in self:
            prop.status = status_map.get(prop.state, 'Unknown')

    @api.depends('property_sale_offer_ids')
    def _compute_offer_count(self):
        for prop in self:
            prop.offer_count = len(prop.property_sale_offer_ids)

    @api.depends('property_sale_ids')
    def _compute_sale_count(self):
        for prop in self:
            prop.sale_count = len(prop.property_sale_ids)

    @api.depends('property_sale_ids')
    def _compute_active_sale(self):
        for prop in self:
            active_sales = prop.property_sale_ids.filtered(
                lambda s: s.state in ['confirmed', 'invoiced']
            )
            prop.active_sale_id = active_sales[0] if active_sales else False

    # Payment Progress Calculations
    @api.depends('active_sale_id.property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        for prop in self:
            if prop.active_sale_id:
                lines = prop.active_sale_id.property_sale_line_ids
                total = sum(lines.mapped('capital_repayment'))
                paid = sum(lines.filtered(
                    lambda l: l.collection_status == 'paid'
                ).mapped('capital_repayment'))
                prop.payment_progress = (paid / total) * 100 if total > 0 else 0
            else:
                prop.payment_progress = 0

    @api.depends('active_sale_id.property_sale_line_ids')
    def _compute_payment_details(self):
        for prop in self:
            if prop.active_sale_id:
                lines = prop.active_sale_id.property_sale_line_ids
                prop.total_invoiced = sum(lines.mapped('capital_repayment'))
                prop.total_paid = sum(lines.filtered(
                    lambda l: l.collection_status == 'paid'
                ).mapped('capital_repayment'))
                prop.remaining_amount = prop.active_sale_id.sale_price - prop.total_paid
            else:
                prop.total_invoiced = 0
                prop.total_paid = 0
                prop.remaining_amount = 0

    # CRUD Overrides
    @api.model
    def create(self, vals):
        if not vals.get('property_reference'):
            vals['property_reference'] = self.env['ir.sequence'].next_by_code('property.reference')
        return super().create(vals)

    def write(self, vals):
        if 'state' in vals and vals['state'] == self.STATE_SOLD:
            self._handle_sale_state_change()
        return super().write(vals)

    # Business Logic
    def _handle_sale_state_change(self):
        for prop in self:
            sale = self.env['property.sale'].search([
                ('property_id', '=', prop.id),
                ('state', '=', 'confirmed')
            ], limit=1)
            
            if sale:
                prop.write({
                    'partner_id': sale.partner_id.id,
                    'property_sale_offer_id': sale.property_sale_offer_id.id
                })

    # Actions
    def action_create_sale(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Property Sale',
            'res_model': 'property.sale',
            'view_mode': 'form',
            'context': {
                'default_property_id': self.id,
                'default_partner_id': self.partner_id.id
            },
            'target': 'new',
        }

    def action_view_offers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Offers',
            'res_model': 'property.sale.offer',
            'domain': [('property_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {
                'default_property_id': self.id,
                'search_default_open_offers': 1
            }
        }

    def action_view_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sales',
            'res_model': 'property.sale',
            'domain': [('property_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {
                'default_property_id': self.id
            }
        }

    # Constraints
    @api.constrains('property_price')
    def _check_property_price(self):
        for prop in self:
            if prop.property_price <= 0:
                raise ValidationError(_("Property price must be greater than zero!"))