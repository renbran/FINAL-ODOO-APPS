from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class PropertyOffer(models.Model):
    _name = 'property.offer'
    _description = 'Property Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Constants for state values
    STATE_DRAFT = 'draft'
    STATE_SENT = 'sent'
    STATE_NEGOTIATION = 'negotiation'
    STATE_ACCEPTED = 'accepted'
    STATE_REJECTED = 'rejected'
    STATE_CANCELLED = 'cancelled'
    
    name = fields.Char(string='Reference', readonly=True, copy=False, default=lambda self: _('New'))
    property_id = fields.Many2one('property.property', string='Property', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, tracking=True)
    offer_date = fields.Date(string='Offer Date', default=fields.Date.today, tracking=True)
    validity_date = fields.Date(string='Validity Date', compute='_compute_validity_date', store=True, tracking=True)
    validity_days = fields.Integer(string='Validity (Days)', default=7, tracking=True)
    
    # Financial details
    property_price = fields.Monetary(related='property_id.property_price', string='Property Listed Price', readonly=True)
    offer_price = fields.Monetary(string='Offer Price', required=True, tracking=True)
    currency_id = fields.Many2one(related='property_id.currency_id', string='Currency', readonly=True)
    
    # Payment plan details
    payment_option = fields.Selection([
        ('cash', 'Cash Payment'),
        ('installment', 'Installment Plan')
    ], string='Payment Option', default='installment', required=True, tracking=True)
    down_payment_percentage = fields.Float(string='Down Payment (%)', default=20.0, tracking=True)
    dld_fee_percentage = fields.Float(string='DLD Fee (%)', default=4.0, tracking=True)
    admin_fee = fields.Monetary(string='Admin Fee', default=5000.0, tracking=True)
    no_of_installments = fields.Integer(string='Number of Installments', default=12, tracking=True)
    installment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Installment Frequency', default='monthly', tracking=True)
    
    # Computed fields
    down_payment = fields.Monetary(string='Down Payment Amount', compute='_compute_payment_details', store=True)
    dld_fee = fields.Monetary(string='DLD Fee Amount', compute='_compute_payment_details', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_payment_details', store=True)
    remaining_balance = fields.Monetary(string='Remaining Balance', compute='_compute_payment_details', store=True)
    amount_per_installment = fields.Monetary(string='Amount Per Installment', compute='_compute_payment_details', store=True)
    
    # Status tracking
    state = fields.Selection([
        (STATE_DRAFT, 'Draft'),
        (STATE_SENT, 'Sent'),
        (STATE_NEGOTIATION, 'In Negotiation'),
        (STATE_ACCEPTED, 'Accepted'),
        (STATE_REJECTED, 'Rejected'),
        (STATE_CANCELLED, 'Cancelled')
    ], string='Status', default=STATE_DRAFT, tracking=True)
    
    # Related sale
    sale_id = fields.Many2one('property.sale', string='Related Sale', readonly=True)
    
    @api.depends('offer_date', 'validity_days')
    def _compute_validity_date(self):
        for record in self:
            if record.offer_date and record.validity_days:
                record.validity_date = record.offer_date + timedelta(days=record.validity_days)
            else:
                record.validity_date = False
    
    @api.depends('offer_price', 'down_payment_percentage', 'dld_fee_percentage', 'admin_fee', 'no_of_installments')
    def _compute_payment_details(self):
        for record in self:
            record.down_payment = (record.down_payment_percentage / 100) * record.offer_price
            record.dld_fee = (record.dld_fee_percentage / 100) * record.offer_price
            record.total_amount = record.offer_price + record.dld_fee + record.admin_fee
            record.remaining_balance = record.total_amount - record.down_payment - record.dld_fee
            
            if record.payment_option == 'installment' and record.no_of_installments > 0:
                record.amount_per_installment = record.remaining_balance / record.no_of_installments
            else:
                record.amount_per_installment = 0.0
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('property.offer') or _('New')
        return super(PropertyOffer, self).create(vals)
    
    def action_send(self):
        """Send the offer to the customer."""
        self.ensure_one()
        if self.state != self.STATE_DRAFT:
            raise UserError(_("Only draft offers can be sent."))
        self.state = self.STATE_SENT
        self.message_post(body=_("Offer sent to customer."))
        return True
    
    def action_negotiate(self):
        """Mark the offer as in negotiation."""
        self.ensure_one()
        if self.state not in [self.STATE_DRAFT, self.STATE_SENT]:
            raise UserError(_("Only draft or sent offers can be marked as in negotiation."))
        self.state = self.STATE_NEGOTIATION
        self.message_post(body=_("Offer is now in negotiation."))
        return True

    def action_accept(self):
        """Accept the offer and create a property sale."""
        self.ensure_one()
        if self.state not in [self.STATE_SENT, self.STATE_NEGOTIATION]:
            raise UserError(_("Only sent or in-negotiation offers can be accepted."))
            
        # Check if property is available
        if self.property_id.state != self.property_id.STATE_AVAILABLE:
            raise UserError(_("This property is not available for sale."))
            
        # Create property sale
        sale_vals = {
            'property_id': self.property_id.id,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'offer_id': self.id,
            'sale_price': self.offer_price,
            'payment_option': self.payment_option,
            'down_payment_percentage': self.down_payment_percentage,
            'dld_fee_percentage': self.dld_fee_percentage,
            'admin_fee': self.admin_fee,
            'no_of_installments': self.no_of_installments,
            'installment_frequency': self.installment_frequency,
        }
        sale = self.env['property.sale'].create(sale_vals)
        self.sale_id = sale.id
        
        # Update offer state
        self.state = self.STATE_ACCEPTED
        self.message_post(body=_("Offer accepted and sale created."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sale',
            'res_model': 'property.sale',
            'res_id': sale.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_reject(self):
        """Reject the offer."""
        for record in self:
            if record.state not in [record.STATE_SENT, record.STATE_NEGOTIATION]:
                raise UserError(_("Only sent or in-negotiation offers can be rejected."))
            record.state = record.STATE_REJECTED
            record.message_post(body=_("Offer rejected."))
        return True

    def action_cancel(self):
        """Cancel the offer."""
        for record in self:
            if record.state in [record.STATE_ACCEPTED, record.STATE_REJECTED]:
                raise UserError(_("Cannot cancel offers that are already accepted or rejected."))
            record.state = record.STATE_CANCELLED
            record.message_post(body=_("Offer cancelled."))
        return True

    def action_reset_to_draft(self):
        """Reset offer to draft state."""
        for record in self:
            if record.state != record.STATE_CANCELLED:
                raise UserError(_("Only cancelled offers can be reset to draft."))
            record.state = record.STATE_DRAFT
            record.message_post(body=_("Offer reset to draft."))
        return True

    @api.constrains('offer_price')
    def _check_offer_price(self):
        """Ensure offer price is positive."""
        for record in self:
            if record.offer_price <= 0:
                raise ValidationError(_("Offer price must be positive."))

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Update offer price based on selected property."""
        if self.property_id:
            self.offer_price = self.property_id.property_price
            self.currency_id = self.property_id.currency_id
        else:
            self.offer_price = 0.0
            self.currency_id = False
    @api.onchange('payment_option')
    def _onchange_payment_option(self):
        """Reset installment-related fields if payment option is changed to cash."""
        if self.payment_option == 'cash':
            self.no_of_installments = 0
            self.installment_frequency = None
        else:
            # Default values for installment plan
            self.no_of_installments = 12
            self.installment_frequency = 'monthly'
    @api.onchange('down_payment_percentage', 'dld_fee_percentage', 'admin_fee')
    def _onchange_payment_details(self):
        """Recompute payment details when down payment, DLD fee, or admin fee changes."""
        self._compute_payment_details()
        if self.payment_option == 'installment':
            self._compute_payment_details()
        else:
            self.amount_per_installment = 0.0
    def _default_payment_option(self):
        """Default payment option for new offers."""
        return 'installment'
    @api.model
    def _default_down_payment_percentage(self):
        """Default down payment percentage for new offers."""
        return 20.0 # Default 20% down payment      
    @api.model
    def _default_dld_fee_percentage(self):
        """Default DLD fee percentage for new offers."""
        return 4.0
    @api.model
    def _default_admin_fee(self):
        """Default admin fee for new offers."""
        return 5000.0
    @api.model
    def _default_no_of_installments(self):
        """Default number of installments for new offers."""
        return 12
    @api.model
    def _default_installment_frequency(self):
        """Default installment frequency for new offers."""
        return 'monthly'
    @api.model
    def _default_validity_days(self):
        """Default validity days for new offers."""
        return 365
    @api.model
    def _default_offer_date(self):
        """Default offer date for new offers."""
        return fields.Date.today()