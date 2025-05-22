# pylint: disable=import-error
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PropertyOffer(models.Model):
    """Model for property offers before converting to sales"""
    _name = 'property.offer'
    _description = 'Property Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, price desc'
    
    name = fields.Char(string="Offer Reference", required=True, copy=False,
                      readonly=True, default=lambda self: _('New'))
    
    # Offer details
    property_id = fields.Many2one('property.property', string="Property", required=True, 
                                 domain="[('state', '=', 'available')]", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True, tracking=True)
    
    price = fields.Float(string="Offered Price", required=True, tracking=True)
    property_price = fields.Float(related='property_id.property_price', string="Property Price")
    price_difference = fields.Float(string="Difference", compute='_compute_price_difference', store=True)
    price_difference_percent = fields.Float(string="Difference (%)", compute='_compute_price_difference', store=True)
    
    # Dates
    date = fields.Date(string="Offer Date", default=fields.Date.today, required=True, tracking=True)
    validity = fields.Integer(string="Validity (days)", default=7, tracking=True)
    date_deadline = fields.Date(string="Deadline", compute='_compute_date_deadline', store=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', required=True, tracking=True)
    
    # Document verification
    document_verified = fields.Boolean(string="Documents Verified", default=False, tracking=True,
                                     help="Check this box when all required documents are verified")
    document_verification_date = fields.Date(string="Verification Date")
    document_verified_by = fields.Many2one('res.users', string="Verified By")
    
    # Payment plan
    down_payment_percentage = fields.Float(string="Down Payment (%)", default=20, tracking=True)
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms")
    note = fields.Text(string="Notes")
    
    # Related sale
    property_sale_id = fields.Many2one('property.sale', string="Related Sale")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='property_id.currency_id')
    
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'Offer price must be strictly positive!')
    ]
    
    @api.model
    def create(self, vals):
        """Override create to set sequence for offer reference"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('property.offer') or _('New')
        return super(PropertyOffer, self).create(vals)
    
    @api.depends('price', 'property_price')
    def _compute_price_difference(self):
        """Compute the difference between offered price and property price"""
        for offer in self:
            if offer.property_price:
                offer.price_difference = offer.price - offer.property_price
                offer.price_difference_percent = (offer.price_difference / offer.property_price) * 100
            else:
                offer.price_difference = 0
                offer.price_difference_percent = 0
    
    @api.depends('date', 'validity')
    def _compute_date_deadline(self):
        """Compute the deadline date based on offer date and validity"""
        for offer in self:
            if offer.date and offer.validity:
                offer.date_deadline = offer.date + timedelta(days=offer.validity)
            else:
                offer.date_deadline = offer.date
    
    @api.constrains('property_id')
    def _check_property_availability(self):
        """Ensure property is available for offers"""
        for offer in self:
            if offer.property_id.state != 'available' and offer.state == 'draft':
                raise ValidationError(_("You cannot make an offer on a property that is not available."))
    
    def action_draft(self):
        """Set the offer to draft state"""
        for offer in self:
            if offer.property_sale_id:
                raise UserError(_("You cannot set to draft an offer that is already linked to a sale."))
            offer.state = 'draft'
    
    def action_open(self):
        """Set the offer to open state"""
        for offer in self:
            offer.state = 'open'
            # Mark property as reserved when offer is opened
            if offer.property_id.state == 'available':
                offer.property_id.state = 'reserved'
    
    def action_accept(self):
        """Accept the offer and refuse other offers for the same property"""
        for offer in self:
            # Check document verification
            if not offer.document_verified:
                raise UserError(_("You cannot accept an offer without document verification."))
            
            # Set this offer as accepted
            offer.write({
                'state': 'accepted',
                'document_verification_date': fields.Date.today(),
                'document_verified_by': self.env.user.id,
            })
            
            # Refuse other offers for the same property
            other_offers = self.env['property.offer'].search([
                ('property_id', '=', offer.property_id.id),
                ('id', '!=', offer.id),
                ('state', 'in', ['draft', 'open'])
            ])
            if other_offers:
                other_offers.write({'state': 'refused'})
                
            # Update property state to 'booked'
            offer.property_id.write({'state': 'booked'})
    
    def action_refuse(self):
        """Refuse the offer"""
        for offer in self:
            offer.state = 'refused'
            
            # If this was the only open/accepted offer for the property, 
            # set property back to available if it was reserved because of this offer
            open_offers = self.env['property.offer'].search_count([
                ('property_id', '=', offer.property_id.id),
                ('state', 'in', ['open', 'accepted']),
                ('id', '!=', offer.id)
            ])
            if open_offers == 0 and offer.property_id.state == 'reserved':
                offer.property_id.state = 'available'
    
    def action_cancel(self):
        """Cancel the offer"""
        for offer in self:
            if offer.property_sale_id:
                raise UserError(_("You cannot cancel an offer that is already linked to a sale."))
            offer.state = 'cancelled'
            
            # If no other open offers, set property back to available
            open_offers = self.env['property.offer'].search_count([
                ('property_id', '=', offer.property_id.id),
                ('state', 'in', ['open', 'accepted']),
                ('id', '!=', offer.id)
            ])
            if open_offers == 0 and offer.property_id.state in ['reserved', 'booked']:
                offer.property_id.state = 'available'
    
    def action_verify_documents(self):
        """Mark the offer documents as verified"""
        for offer in self:
            offer.write({
                'document_verified': True,
                'document_verification_date': fields.Date.today(),
                'document_verified_by': self.env.user.id,
            })
    
    def action_create_sale(self):
        """Create a sale order from this offer"""
        self.ensure_one()
        
        # Check if offer is accepted
        if self.state != 'accepted':
            raise UserError(_("Only accepted offers can be converted to sales."))
            
        # Check if documents are verified
        if not self.document_verified:
            raise UserError(_("You cannot create a sale without document verification."))
            
        # Create the sale
        sale = self.env['property.sale'].create({
            'name': f"{self.property_id.name} - Sale",
            'property_id': self.property_id.id,
            'partner_id': self.partner_id.id,
            'property_offer_id': self.id,
            'property_value': self.price,
            'down_payment_percentage': self.down_payment_percentage,
            'start_date': fields.Date.today(),
            'sale_date': fields.Date.today(),
            'state': 'draft'
        })
        
        # Link the sale to this offer
        self.property_sale_id = sale.id
        
        # Mark the property as booked if not already
        if self.property_id.state == 'available' or self.property_id.state == 'reserved':
            self.property_id.state = 'booked'
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sale',
            'res_model': 'property.sale',
            'view_mode': 'form',
            'res_id': sale.id,
            'target': 'current',
        }
        
    @api.model
    def _cron_check_offer_validity(self):
        """Cron job to check offer validity and mark expired offers"""
        today = fields.Date.today()
        expired_offers = self.search([
            ('state', 'in', ['draft', 'open']),
            ('date_deadline', '<', today)
        ])
        if expired_offers:
            expired_offers.write({'state': 'expired'})
