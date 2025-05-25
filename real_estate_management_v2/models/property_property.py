from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Property(models.Model):
    _name = 'property.property'
    _description = 'Property Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Constants for state values
    STATE_AVAILABLE = 'available'
    STATE_RESERVED = 'reserved'
    STATE_BOOKED = 'booked'
    STATE_SOLD = 'sold'

    name = fields.Char(string="Property Name", required=True, tracking=True)
    reference = fields.Char(string="Reference", readonly=True, copy=False, default=lambda self: _('New'))
    property_image = fields.Image("Property Image")
    floor_plan = fields.Image("Floor Plan")
    user_id = fields.Many2one('res.users', string="Salesperson", default=lambda self: self.env.user, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Owner", tracking=True)
    property_price = fields.Monetary(string="Property Price", required=True, tracking=True)
    revenue_account_id = fields.Many2one('account.account', string="Revenue Account", required=True, 
                                        domain=[('account_type', '=', 'income')])
    address = fields.Text(string="Address", tracking=True)
    sale_rent = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], string="Sale or Rent", required=True, default='for_sale', tracking=True)
    state = fields.Selection([
        (STATE_AVAILABLE, 'Available'),
        (STATE_RESERVED, 'Reserved'),
        (STATE_BOOKED, 'Booked'),
        (STATE_SOLD, 'Sold')
    ], string="State", default=STATE_AVAILABLE, required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self.env.company.currency_id)
    description = fields.Text(string="Description")
    
    # Property details
    property_type_id = fields.Many2one('property.type', string="Property Type")
    project_id = fields.Many2one('property.project', string="Project")
    tower = fields.Char(string="Tower")
    level = fields.Char(string="Level")
    unit_no = fields.Char(string="Unit No")
    unit_view = fields.Char(string="Unit View")
    total_sqft = fields.Float(string="Total Sqft")
    price_per_sqft = fields.Float(string="Price / Sqft", compute="_compute_price_per_sqft", store=True)
    bedrooms = fields.Integer(string="Bedrooms")
    bathrooms = fields.Integer(string="Bathrooms")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Float(string="Garden Area (sqft)")
    
    # Relationships
    property_offer_ids = fields.One2many('property.offer', 'property_id', string="Offers")
    property_sale_ids = fields.One2many('property.sale', 'property_id', string="Sales")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")
    sale_count = fields.Integer(string="Sale Count", compute="_compute_sale_count")
    
    # Payment tracking fields
    payment_progress = fields.Float(string="Payment Progress (%)", compute="_compute_payment_progress", store=True)
    total_invoiced = fields.Monetary(string="Total Invoiced", compute="_compute_payment_details", store=True)
    total_paid = fields.Monetary(string="Total Paid", compute="_compute_payment_details", store=True)
    remaining_amount = fields.Monetary(string="Remaining Amount", compute="_compute_payment_details", store=True)
    active_sale_id = fields.Many2one('property.sale', string="Active Sale", compute="_compute_active_sale")
    
    @api.depends('property_price', 'total_sqft')
    def _compute_price_per_sqft(self):
        for record in self:
            record.price_per_sqft = record.property_price / record.total_sqft if record.total_sqft else 0.0
    
    @api.depends('property_offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.property_offer_ids)
    
    @api.depends('property_sale_ids')
    def _compute_sale_count(self):
        for record in self:
            record.sale_count = len(record.property_sale_ids)
    
    @api.depends('property_sale_ids')
    def _compute_active_sale(self):
        for record in self:
            active_sales = record.property_sale_ids.filtered(lambda s: s.state != 'cancelled')
            record.active_sale_id = active_sales[0] if active_sales else False
    
    @api.depends('active_sale_id', 'active_sale_id.property_sale_line_ids', 
                 'active_sale_id.property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        for record in self:
            if record.active_sale_id:
                record.payment_progress = record.active_sale_id.payment_progress
            else:
                record.payment_progress = 0.0
    
    @api.depends('active_sale_id', 'active_sale_id.property_sale_line_ids', 
                 'active_sale_id.property_sale_line_ids.collection_status',
                 'active_sale_id.sale_price')
    def _compute_payment_details(self):
        for record in self:
            if record.active_sale_id:
                record.total_invoiced = sum(record.active_sale_id.property_sale_line_ids.filtered(
                    lambda l: l.invoice_id).mapped('capital_repayment'))
                record.total_paid = sum(record.active_sale_id.property_sale_line_ids.filtered(
                    lambda l: l.collection_status == 'paid').mapped('capital_repayment'))
                record.remaining_amount = record.active_sale_id.sale_price - record.total_paid
            else:
                record.total_invoiced = 0.0
                record.total_paid = 0.0
                record.remaining_amount = 0.0
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('property.property') or _('New')
        return super(Property, self).create(vals)
    
    def action_create_offer(self):
        """Create a new property offer from the property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Offer',
            'res_model': 'property.offer',
            'view_mode': 'form',
            'context': {
                'default_property_id': self.id,
                'default_user_id': self.env.user.id,
            },
            'target': 'current',
        }
    
    def action_view_offers(self):
        """View all offers for this property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Offers',
            'res_model': 'property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
            'target': 'current',
        }
    
    def action_view_sales(self):
        """View all sales for this property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sales',
            'res_model': 'property.sale',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
            'target': 'current',
        }

    def action_view_sales(self):
        """View all sales for this property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sales',
            'res_model': 'property.sale',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
            'target': 'current',
        }
        
    def action_create_sale(self):
        """Create a new property sale directly."""
        self.ensure_one()
        if self.state == self.STATE_SOLD:
            raise UserError(_("This property is already sold."))
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Sale',
            'res_model': 'property.sale',
            'view_mode': 'form',
            'context': {
                'default_property_id': self.id,
                'default_user_id': self.env.user.id,
                'default_property_value': self.property_price,
            },
            'target': 'current',
        }
        
    def action_mark_as_reserved(self):
        """Mark the property as reserved."""
        self.ensure_one()
        if self.state != self.STATE_AVAILABLE:
            raise UserError(_("Only available properties can be reserved."))
        self.state = self.STATE_RESERVED
        self.message_post(body=_("Property marked as reserved."))
        
    def action_mark_as_available(self):
        """Mark the property as available."""
        self.ensure_one()
        if self.state == self.STATE_SOLD:
            raise UserError(_("Sold properties cannot be marked as available."))
        self.state = self.STATE_AVAILABLE
        self.message_post(body=_("Property marked as available."))
        
    def action_mark_as_booked(self):
        """Mark the property as booked."""
        self.ensure_one()
        if self.state == self.STATE_SOLD:
            raise UserError(_("Sold properties cannot be marked as booked."))
        self.state = self.STATE_BOOKED
        self.message_post(body=_("Property marked as booked."))
        
    def action_generate_report(self):
        """Generate property report."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Report',
            'res_model': 'property.report.wizard',
            'view_mode': 'form',
            'context': {'default_property_id': self.id},
            'target': 'new',
        }
        
    @api.constrains('property_price')
    def _check_property_price(self):
        """Ensure property price is positive."""
        for record in self:
            if record.property_price <= 0:
                raise ValidationError(_("Property price must be positive."))
                
    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Update property name when project changes."""
        if self.project_id and not self.name:
            self.name = f"{self.project_id.name} - New Unit"