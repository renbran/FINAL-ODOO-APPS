from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class PropertyType(models.Model):
    """Property type such as Apartment, Villa, Office, etc."""
    _name = 'property.type'
    _description = 'Property Type'
    _order = 'name'

    name = fields.Char(string="Type", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description")
    property_ids = fields.One2many('property.property', 'property_type_id', string="Properties")
    property_count = fields.Integer(compute='_compute_property_count', string="Property Count")
    
    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)
            
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Property type code must be unique!')
    ]


class PropertyTag(models.Model):
    """Tags for properties such as New, Exclusive, etc."""
    _name = 'property.tag'
    _description = 'Property Tag'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color Index")
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Property tag name must be unique!')
    ]


class Property(models.Model):
    """Main property model with all property details"""
    _name = 'property.property'
    _description = 'Property Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Constants for state values
    STATE_AVAILABLE = 'available'
    STATE_RESERVED = 'reserved'
    STATE_BOOKED = 'booked'
    STATE_SOLD = 'sold'
    STATE_CANCELLED = 'cancelled'

    # Basic property information
    name = fields.Char(string="Property Name", required=True, tracking=True)
    property_reference = fields.Char(string="Property Reference", readonly=True, copy=False, 
                                    default=lambda self: _('New'))
    description = fields.Text(string="Description", tracking=True)
    
    # Property images
    property_image = fields.Image("Property Image", max_width=1024, max_height=1024)
    floor_plan = fields.Image("Floor Plan", max_width=1024, max_height=1024)
    
    # Property metrics
    total_sqft = fields.Float(string="Total Sqft", tracking=True)
    price_per_sqft = fields.Float(string="Price / Sqft", tracking=True, 
                                 compute='_compute_price_per_sqft', store=True)
    
    # Property pricing
    property_price = fields.Monetary(string="Property Price", required=True, tracking=True)
    expected_revenue = fields.Monetary(string="Expected Revenue", tracking=True)
    selling_price = fields.Monetary(string="Selling Price", compute='_compute_selling_price', store=True)
    
    # Property financial accounting
    revenue_account_id = fields.Many2one('account.account', string="Revenue Account", required=True,
                                        domain=[('deprecated', '=', False)],
                                        default=lambda self: self._default_revenue_account())
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, 
                                 default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string="Company", 
                                default=lambda self: self.env.company)
    
    # Property type and characteristics
    property_type_id = fields.Many2one('property.type', string="Property Type", tracking=True)
    tag_ids = fields.Many2many('property.tag', string="Tags")
    sale_rent = fields.Selection([
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    ], string="Sale or Rent", required=True, tracking=True)
    
    # Property details
    tower = fields.Char(string="Tower", tracking=True)
    level = fields.Char(string="Level", tracking=True)
    project_name = fields.Char(string="Project Name", default="Sky Hills Astra", tracking=True)
    unit_no = fields.Char(string="Unit No", tracking=True)
    unit_view = fields.Char(string="Unit View", tracking=True)
    
    # Property location
    address = fields.Text(string="Address", tracking=True)
    city = fields.Char(string="City", tracking=True)
    state_id = fields.Many2one('res.country.state', string="State", tracking=True)
    country_id = fields.Many2one('res.country', string="Country", tracking=True)
    zip_code = fields.Char(string="ZIP Code", tracking=True)
    
    # Property status and ownership
    state = fields.Selection([
        (STATE_AVAILABLE, 'Available'),
        (STATE_RESERVED, 'Reserved'),
        (STATE_BOOKED, 'Booked'),
        (STATE_SOLD, 'Sold'),
        (STATE_CANCELLED, 'Cancelled')
    ], string="State", default=STATE_AVAILABLE, required=True, tracking=True)
    status = fields.Char(string="Status", compute='_compute_status', store=True)
    partner_id = fields.Many2one('res.partner', string="Owner/Customer", tracking=True)
    
    # Computed fields for sales and payment tracking
    property_offer_ids = fields.One2many('property.offer', 'property_id', string="Property Offers")
    offer_count = fields.Integer(string="Offer Count", compute='_compute_offer_count')
    best_offer = fields.Float(string="Best Offer", compute='_compute_best_offer')
    
    property_sale_ids = fields.One2many('property.sale', 'property_id', string="Related Sales")
    sale_count = fields.Integer(string="Sale Count", compute='_compute_sale_count')
    active_sale_id = fields.Many2one('property.sale', string="Active Sale", compute='_compute_active_sale')
    
    # Payment tracking fields
    payment_progress = fields.Float(string="Payment Progress (%)", compute='_compute_payment_progress', store=True)
    total_invoiced = fields.Monetary(string="Total Invoiced", compute='_compute_payment_details', store=True)
    total_paid = fields.Monetary(string="Total Paid", compute='_compute_payment_details', store=True)
    remaining_amount = fields.Monetary(string="Remaining Amount", compute='_compute_payment_details', store=True)
    
    _sql_constraints = [
        ('check_property_price', 'CHECK(property_price > 0)',
         'Property price must be strictly positive!'),
        ('check_total_sqft', 'CHECK(total_sqft > 0)',
         'Total square feet must be strictly positive!')
    ]

    @api.model
    def _default_revenue_account(self):
        """Default revenue account for properties"""
        revenue_account = self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('deprecated', '=', False),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        return revenue_account.id if revenue_account else False
    
    @api.model
    def create(self, vals):
        """Override create to generate property reference automatically"""
        if vals.get('property_reference', _('New')) == _('New'):
            vals['property_reference'] = self.env['ir.sequence'].next_by_code('property.property') or _('New')
        return super(Property, self).create(vals)
    
    def write(self, vals):
        """Override write to update property state and partner when sold"""
        res = super(Property, self).write(vals)
        if 'state' in vals and vals['state'] == self.STATE_SOLD:
            # If property is marked as sold, get the confirmed sale and update owner
            property_sale = self.env['property.sale'].search([
                ('property_id', '=', self.id), 
                ('state', '=', 'confirm')
            ], limit=1)
            if property_sale and property_sale.partner_id:
                self.write({'partner_id': property_sale.partner_id.id})
        return res
    
    @api.depends('state')
    def _compute_status(self):
        """Compute the status based on the state."""
        for record in self:
            if record.state == self.STATE_AVAILABLE:
                record.status = 'Available'
            elif record.state == self.STATE_RESERVED:
                record.status = 'Reserved'
            elif record.state == self.STATE_BOOKED:
                record.status = 'Booked'
            elif record.state == self.STATE_SOLD:
                record.status = 'Sold'
            elif record.state == self.STATE_CANCELLED:
                record.status = 'Cancelled'
            else:
                record.status = 'Unknown'
    
    @api.depends('property_price', 'total_sqft')
    def _compute_price_per_sqft(self):
        """Compute price per square foot"""
        for record in self:
            record.price_per_sqft = record.property_price / record.total_sqft if record.total_sqft else 0.0
    
    @api.depends('property_price', 'expected_revenue')
    def _compute_selling_price(self):
        """Compute the selling price based on expected revenue or property price"""
        for record in self:
            record.selling_price = record.expected_revenue or record.property_price
    
    @api.depends('property_sale_ids')
    def _compute_sale_count(self):
        """Compute the number of sales related to this property."""
        for record in self:
            record.sale_count = len(record.property_sale_ids)
    
    @api.depends('property_offer_ids')
    def _compute_offer_count(self):
        """Compute the number of offers for this property"""
        for record in self:
            record.offer_count = len(record.property_offer_ids)
    
    @api.depends('property_offer_ids.price', 'property_offer_ids.state')
    def _compute_best_offer(self):
        """Compute the best offer for this property"""
        for record in self:
            valid_offers = record.property_offer_ids.filtered(lambda o: o.state in ['open', 'accepted'])
            record.best_offer = max(valid_offers.mapped('price')) if valid_offers else 0.0
    
    @api.depends('property_sale_ids')
    def _compute_active_sale(self):
        """Compute the active sale for this property."""
        for record in self:
            active_sales = record.property_sale_ids.filtered(lambda s: s.state in ['confirm', 'invoiced'])
            record.active_sale_id = active_sales[0] if active_sales else False
    
    @api.depends('active_sale_id', 'active_sale_id.property_sale_line_ids', 
                 'active_sale_id.property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        """Compute the payment progress based on paid installments."""
        for record in self:
            if record.active_sale_id:
                all_lines = record.active_sale_id.property_sale_line_ids
                if all_lines:
                    total_amount = sum(all_lines.mapped('capital_repayment'))
                    paid_amount = sum(all_lines.filtered(lambda l: l.collection_status == 'paid').mapped('capital_repayment'))
                    record.payment_progress = round((paid_amount / total_amount) * 100, 2) if total_amount > 0 else 0.0
                else:
                    record.payment_progress = 0.0
            else:
                record.payment_progress = 0.0
    
    @api.depends('active_sale_id', 'active_sale_id.property_sale_line_ids', 
                 'active_sale_id.property_sale_line_ids.collection_status',
                 'active_sale_id.sale_price')
    def _compute_payment_details(self):
        """Compute payment details (total invoiced, total paid, remaining amount)."""
        for record in self:
            if record.active_sale_id:
                all_lines = record.active_sale_id.property_sale_line_ids
                paid_amount = sum(all_lines.filtered(lambda l: l.collection_status == 'paid').mapped('capital_repayment'))
                record.total_invoiced = sum(all_lines.mapped('capital_repayment'))
                record.total_paid = paid_amount
                record.remaining_amount = record.active_sale_id.sale_price - paid_amount
            else:
                record.total_invoiced = 0.0
                record.total_paid = 0.0
                record.remaining_amount = 0.0
    
    def action_create_sale(self):
        """Create a new property sale from the property."""
        self.ensure_one()
        
        # Check if property has validated offers
        validated_offers = self.property_offer_ids.filtered(lambda o: o.state == 'accepted')
        if not validated_offers and self.sale_rent == 'for_sale':
            raise UserError(_("You must have an accepted offer before creating a sale!"))
        
        # Get the accepted offer if available
        accepted_offer = validated_offers[0] if validated_offers else False
        
        # Create a new sale
        sale = self.env['property.sale'].create({
            'name': f"{self.name} - Sale",
            'property_id': self.id,
            'partner_id': accepted_offer.partner_id.id if accepted_offer else self.partner_id.id,
            'property_offer_id': accepted_offer.id if accepted_offer else False,
            'start_date': fields.Date.today(),
            'sale_date': fields.Date.today(),
            'property_value': accepted_offer.price if accepted_offer else self.property_price,
            'state': 'draft'
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sale',
            'res_model': 'property.sale',
            'view_mode': 'form',
            'res_id': sale.id,
            'target': 'current',
        }

    def action_view_sales(self):
        """View all sales related to this property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sales',
            'res_model': 'property.sale',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
        
    def action_view_offers(self):
        """View all offers related to this property."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Offers',
            'res_model': 'property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
        
    def action_mark_as_available(self):
        """Mark the property as available"""
        self.write({'state': 'available'})
        
    def action_mark_as_reserved(self):
        """Mark the property as reserved"""
        self.write({'state': 'reserved'})
        
    def action_mark_as_sold(self):
        """Mark the property as sold"""
        # Check if there's a confirmed sale
        if not self.active_sale_id:
            raise UserError(_("No confirmed sale found for this property. Create a sale first."))
        self.write({'state': 'sold'})
        
    def action_mark_as_cancelled(self):
        """Mark the property as cancelled"""
        self.write({'state': 'cancelled'})
