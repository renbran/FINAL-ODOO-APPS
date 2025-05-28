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
    
    # Payment details
    down_payment_percentage = fields.Float(
        string='Down Payment (%)',
        default=20.0,
        tracking=True
    )
    
    down_payment = fields.Monetary(
        string='Down Payment',
        compute='_compute_payment_breakdown',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    
    dld_fee_percentage = fields.Float(
        string='DLD Fee (%)',
        default=4.0,
        tracking=True
    )
    
    dld_fee = fields.Monetary(
        string='DLD Fee',
        compute='_compute_payment_breakdown',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    
    admin_fee = fields.Monetary(
        string='Admin Fee',
        default=5000.0,
        currency_field='currency_id',
        tracking=True
    )
    
    remaining_balance = fields.Monetary(
        string='Remaining Balance',
        compute='_compute_payment_breakdown',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    
    total_offer_amount = fields.Monetary(
        string='Total Offer Amount',
        compute='_compute_total_offer_amount',
        currency_field='currency_id',
        store=True
    )
    
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Frequency', default='monthly', required=True, tracking=True)
    
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
        digits=(5, 2)
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
        'property_sale_offer_id', 
        string="Broker Commission Invoices",
        readonly=True
    )
    
    broker_commission_count = fields.Integer(
        string="Commission Count", 
        compute='_compute_broker_commission_count'
    )
    
    # ========== Compute Methods ==========

    @api.depends('offer_price', 'down_payment_percentage', 'dld_fee_percentage', 'admin_fee')
    def _compute_payment_breakdown(self):
        for offer in self:
            offer.down_payment = offer.offer_price * (offer.down_payment_percentage / 100)
            offer.dld_fee = offer.offer_price * (offer.dld_fee_percentage / 100)
            offer.remaining_balance = offer.offer_price - offer.down_payment - offer.dld_fee - offer.admin_fee

    @api.depends('offer_price', 'down_payment', 'dld_fee', 'admin_fee')
    def _compute_total_offer_amount(self):
        for offer in self:
            offer.total_offer_amount = offer.offer_price + offer.dld_fee + offer.admin_fee

    @api.depends('offer_price', 'property_price')
    def _compute_price_difference(self):
        for offer in self:
            offer.price_difference = offer.offer_price - offer.property_price
            if offer.property_price:
                offer.price_difference_percent = (offer.price_difference / offer.property_price) * 100
            else:
                offer.price_difference_percent = 0

    @api.depends('expiration_date')
    def _compute_days_to_expire(self):
        today = fields.Date.today()
        for offer in self:
            if offer.expiration_date:
                offer.days_to_expire = (offer.expiration_date - today).days
                offer.is_expired = offer.days_to_expire < 0
            else:
                offer.days_to_expire = 0
                offer.is_expired = False

    @api.depends('offer_price', 'broker_commission_percentage')
    def _compute_broker_commission_amount(self):
        for offer in self:
            offer.broker_commission_amount = offer.offer_price * (offer.broker_commission_percentage / 100)

    @api.depends('broker_commission_ids')
    def _compute_broker_commission_count(self):
        for offer in self:
            offer.broker_commission_count = len(offer.broker_commission_ids)

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
            if offer.offer_price < offer.property_id.property_price:
                raise ValidationError(
                    _('Offer price must be greater than or equal to the property price.')
                )

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
        
        self.env.ref('property_sale_management.action_report_sale_offer').report_action(self)
        self.write({'state': 'sent'})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'property.sale.offer',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def action_accept(self):
        self.ensure_one()
        if self.state not in ['draft', 'sent']:
            raise UserError(_("Only draft or sent offers can be accepted."))
        self.write({'state': 'accepted'})

    def action_reject(self):
        self.ensure_one()
        if self.state not in ['draft', 'sent']:
            raise UserError(_("Only draft or sent offers can be rejected."))
        self.write({'state': 'rejected'})

    # ========== Onchange Methods ==========

    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id:
            self.offer_price = self.property_id.property_price

    @api.onchange('offer_price')
    def _onchange_offer_price(self):
        if self.offer_price and self.property_id:
            if self.offer_price < self.property_id.property_price:
                return {
                    'warning': {
                        'title': _("Warning"),
                        'message': _("The offer price is lower than the property price. Are you sure you want to proceed?")
                    }
                }

    # ========== Additional Methods ==========

    def extend_expiration(self, days=7):
        """Extend the expiration date of the offer"""
        for offer in self:
            if offer.state not in ['draft', 'sent']:
                raise UserError(_("Can only extend expiration for draft or sent offers."))
            offer.expiration_date = offer.expiration_date + timedelta(days=days)

    def send_reminder_email(self):
        """Send a reminder email to the customer about the offer"""
        self.ensure_one()
        template = self.env.ref('real_estate_management_v2.email_template_property_offer_reminder', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

    # ========== Cron Job ==========

    @api.model
    def _cron_check_expired_offers(self):
        """Cron job to check and update expired offers"""
        expired_offers = self.search([
            ('state', 'in', ['draft', 'sent']),
            ('expiration_date', '<', fields.Date.today())
        ])
        expired_offers.write({'state': 'rejected'})

    # ========== Reporting Methods ==========

    def get_offer_report_values(self):
        """Get values for the offer report"""
        self.ensure_one()
        return {
            'offer': self,
            'company': self.env.company,
            'total_amount': self.total_offer_amount,
            'payment_schedule': self._get_payment_schedule(),
        }

    def _get_payment_schedule(self):
        """Generate a payment schedule based on the offer details"""
        schedule = []
        if self.down_payment:
            schedule.append((_("Down Payment"), self.down_payment, self.offer_date))
        if self.remaining_balance:
            schedule.append((_("Remaining Balance"), self.remaining_balance, self.expiration_date))
        return schedule

    # ========== Security Methods ==========

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('property_id.name', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        result = []
        for offer in self:
            name = f"{offer.name} - {offer.property_id.name}"
            result.append((offer.id, name))
        return result