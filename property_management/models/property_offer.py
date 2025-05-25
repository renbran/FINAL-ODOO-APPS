from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class PropertySaleOffer(models.Model):
    _name = 'property.sale.offer'
    _description = 'Property Sale Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'offer_date desc'

    # ========== Fields Definition ==========
    name = fields.Char(
        string='Offer Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True
    )
    
    property_id = fields.Many2one(
        'property.property',
        string='Property',
        required=True,
        ondelete='cascade',
        tracking=True,
        domain="[('state', 'in', ['available', 'reserved'])]"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    offer_price = fields.Monetary(
        string='Offer Price',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    offer_date = fields.Date(
        string='Offer Date',
        default=fields.Date.today,
        tracking=True
    )
    
    property_sale_id = fields.Many2one(
        'property.sale',
        string='Related Sale',
        ondelete='set null',
        readonly=True,
        tracking=True
    )
    
    expiration_date = fields.Date(
        string='Expiration Date',
        required=True,
        default=lambda self: (datetime.now() + timedelta(days=14)).date(),
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status',
        default='draft',
        required=True,
        tracking=True
    )
    
    # Report-specific fields
    down_payment = fields.Monetary(
        string='Down Payment',
        currency_field='currency_id',
        default=0.0,
        tracking=True
    )
    
    dld_fee = fields.Monetary(
        string='DLD Fee',
        currency_field='currency_id',
        default=0.0,
        tracking=True
    )
    
    admin_fee = fields.Monetary(
        string='Admin Fee',
        currency_field='currency_id',
        default=0.0,
        tracking=True
    )
    
    total_offer_amount = fields.Monetary(
        string='Total Offer Amount',
        compute='_compute_total_offer_amount',
        currency_field='currency_id',
        store=True
    )
    
    payment_terms = fields.Html(
        string='Payment Terms',
        default=lambda self: self._default_payment_terms(),
        tracking=True
    )
    
    terms_conditions = fields.Html(
        string='Terms & Conditions',
        default=lambda self: self._default_terms_conditions(),
        tracking=True
    )

    # Computed fields
    property_price = fields.Monetary(
        string='Property Price',
        related='property_id.property_price',
        currency_field='currency_id',
        readonly=True
    )
    
    price_difference = fields.Monetary(
        string='Price Difference',
        compute='_compute_price_difference',
        currency_field='currency_id',
        store=True
    )
    
    price_difference_percent = fields.Float(
        string='Price Difference (%)',
        compute='_compute_price_difference',
        store=True,
        digits='(5, 2)'
    )
    
    days_to_expire = fields.Integer(
        string='Days to Expire',
        compute='_compute_days_to_expire',
        store=True
    )
    
    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_days_to_expire',
        store=True
    )
    
    partner_phone = fields.Char(
        string='Customer Phone',
        related='partner_id.phone',
        readonly=True
    )
    
    partner_email = fields.Char(
        string='Customer Email',
        related='partner_id.email',
        readonly=True
    )
    
    # Broker Commission Fields
    seller_id = fields.Many2one(
        'res.partner', 
        string='Seller/Broker', 
        domain=[('is_company', '=', True)],
        tracking=True,
        help="The broker who facilitated this offer"
    )
    
    broker_commission_percentage = fields.Float(
        string="Commission Percentage", 
        digits=(5, 2),
        default=5.0,
        tracking=True
    )
    
    broker_commission_amount = fields.Monetary(
        string="Commission Amount", 
        compute='_compute_broker_commission_amount',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    
    broker_commission_ids = fields.One2many(
        'broker.commission.invoice', 
        'property_offer_id', 
        string="Broker Commission Invoices",
        readonly=True
    )
    
    broker_commission_count = fields.Integer(
        string="Commission Count", 
        compute='_compute_broker_commission_count'
    )
    
    # ========== Default Methods ==========
    def _default_payment_terms(self):
        return """
        <ol>
            <li>Down payment required upon acceptance</li>
            <li>Balance due by expiration date</li>
            <li>Payment can be made via bank transfer or certified check</li>
        </ol>
        """
    
    def _default_terms_conditions(self):
        return """
        <ol>
            <li>This offer is valid until the expiration date</li>
            <li>The property will remain on the market until a signed agreement and deposit are received</li>
            <li>Prices are subject to change without notice</li>
            <li>All measurements are approximate</li>
            <li>The buyer is responsible for all applicable government fees and taxes</li>
        </ol>
        """

    # ========== Constraints and Validations ==========
    _sql_constraints = [
        ('offer_price_positive', 'CHECK(offer_price > 0)', 'Offer price must be positive.'),
        ('expiration_after_offer', 'CHECK(expiration_date >= offer_date)', 'Expiration date must be after offer date.'),
    ]

    @api.constrains('offer_price', 'property_id')
    def _check_offer_price(self):
        for offer in self:
            if offer.property_id and offer.offer_price <= 0:
                raise ValidationError(_("Offer price must be greater than zero."))
            if offer.property_id and offer.offer_price > (offer.property_id.property_price * 2):
                raise ValidationError(_("Offer price cannot be more than double the property price."))

    # ========== Compute Methods ==========
    @api.depends('offer_price', 'property_id.property_price')
    def _compute_price_difference(self):
        for offer in self:
            if offer.property_id and offer.property_id.property_price > 0:
                offer.price_difference = offer.offer_price - offer.property_id.property_price
                offer.price_difference_percent = (
                    (offer.offer_price - offer.property_id.property_price) / 
                    offer.property_id.property_price * 100
                )
            else:
                offer.price_difference = 0
                offer.price_difference_percent = 0

    @api.depends('expiration_date')
    def _compute_days_to_expire(self):
        today = fields.Date.today()
        for offer in self:
            if offer.expiration_date:
                delta = offer.expiration_date - today
                offer.days_to_expire = delta.days
                offer.is_expired = delta.days < 0
            else:
                offer.days_to_expire = 0
                offer.is_expired = False

    @api.depends('offer_price', 'down_payment', 'dld_fee', 'admin_fee')
    def _compute_total_offer_amount(self):
        for offer in self:
            offer.total_offer_amount = offer.offer_price + offer.down_payment + offer.dld_fee + offer.admin_fee
            
    @api.depends('broker_commission_percentage', 'offer_price')
    def _compute_broker_commission_amount(self):
        for offer in self:
            offer.broker_commission_amount = (offer.broker_commission_percentage / 100) * offer.offer_price
    
    @api.depends('broker_commission_ids')
    def _compute_broker_commission_count(self):
        for offer in self:
            offer.broker_commission_count = len(offer.broker_commission_ids)

    # ========== CRUD Methods ==========
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('property.sale.offer') or 'New'
        return super(PropertySaleOffer, self).create(vals)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'accepted':
            self._validate_acceptance()
        return super(PropertySaleOffer, self).write(vals)

    # ========== Action Methods ==========
    def action_send_offer(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft offers can be sent."))
        
        # Generate and send the report
        report_action = self.env.ref('property_sale_management.action_report_sale_offer').report_action(self)
        self.write({'state': 'sent'})
        
        # Return both the report action and a notification
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property.sale.offer',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'report_sent': True},
        }

    def action_accept(self):
        self.ensure_one()
        if self.state not in ('draft', 'sent'):
            raise UserError(_("Only draft or sent offers can be accepted."))
        self._validate_acceptance()
        self.write({'state': 'accepted'})
        self._create_property_sale()
        return True

    def action_reject(self):
        self.ensure_one()
        if self.state == 'accepted':
            raise UserError(_("Cannot reject an already accepted offer."))
        self.write({'state': 'rejected'})
        return True

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state != 'rejected':
            raise UserError(_("Only rejected offers can be reset to draft."))
        self.write({'state': 'draft'})

     # ========== Smart Button and Views ==========
    def action_view_property(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property',
            'res_model': 'property.property',
            'res_id': self.property_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_sale(self):
        self.ensure_one()
        if not self.property_sale_id:
            raise UserError(_("No sale created from this offer yet."))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property Sale',
            'res_model': 'property.sale',
            'res_id': self.property_sale_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
        
    def action_generate_broker_commission(self):
        """Generate a broker commission invoice from the offer"""
        self.ensure_one()
        if not self.seller_id:
            raise UserError(_("Please select a broker/seller first."))
        
        if not self.property_sale_id:
            raise UserError(_("A property sale must be created first."))
        
        commission = self.env['broker.commission.invoice'].create({
            'property_sale_id': self.property_sale_id.id,
            'property_offer_id': self.id,
            'seller_id': self.seller_id.id,
            'commission_percentage': self.broker_commission_percentage,
            'commission_amount': self.broker_commission_amount,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Broker Commission'),
            'res_model': 'broker.commission.invoice',
            'res_id': commission.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_broker_commissions(self):
        """View broker commissions related to this offer"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Broker Commissions'),
            'res_model': 'broker.commission.invoice',
            'domain': [('property_offer_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {'default_property_offer_id': self.id, 
                       'default_property_sale_id': self.property_sale_id.id,
                       'default_seller_id': self.seller_id.id,
                       'default_commission_percentage': self.broker_commission_percentage,
                       'default_commission_amount': self.broker_commission_amount},
        }
        
    def _create_property_sale(self):
        """Create a property sale from the accepted offer"""
        sale = self.env['property.sale'].create({
            'name': self.env['ir.sequence'].next_by_code('property.sale') or 'New',
            'property_id': self.property_id.id,
            'partner_id': self.partner_id.id,
            'start_date': fields.Date.today(),
            'state': 'draft',
            'property_value': self.offer_price,
            'down_payment': self.down_payment,
            'dld_fee': self.dld_fee,
            'admin_fee': self.admin_fee,
            # Add broker information to the sale
            'seller_name': self.seller_id.id if self.seller_id else False,
            'broker_commission_percentage': self.broker_commission_percentage,
        })
        
        # Link the offer to the sale
        self.property_sale_id = sale.id
        
        # Update property state
        self.property_id.write({
            'state': 'reserved',
            'partner_id': self.partner_id.id
        })
        
        return sale