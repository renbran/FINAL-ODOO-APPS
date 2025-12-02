# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class PropertyVendor(models.Model):
    _name = 'property.vendor'
    _description = 'Stored Data About Sold Property'
    _rec_name = 'sold_seq'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Sale Contract Details
    sold_seq = fields.Char(string='Sequence', required=True,
                           readonly=True, copy=False, default=lambda self: _('New'))
    stage = fields.Selection([
        ('draft', 'Draft - Awaiting Booking Payment'),
        ('booked', 'Booked - Ready for Installments'),
        ('refund', 'Refund'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),
        ('locked', 'Locked')
    ], string='Stage', default='draft', tracking=True,
       help='Draft: Booking fees not paid yet | Booked: Can create installments | Sold: Fully paid')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    date = fields.Date(string='Create Date', default=fields.Date.today())

    # Property Detail
    property_id = fields.Many2one('property.details', string='Property', domain=[
                                  ('stage', '=', 'sale')])
    price = fields.Monetary(related="property_id.price", string="Price")
    type = fields.Selection(related="property_id.type", store=True)
    property_subtype_id = fields.Many2one(
        store=True, related="property_id.property_subtype_id")
    property_project_id = fields.Many2one(
        related="property_id.property_project_id", string="Project", store=True)
    subproject_id = fields.Many2one(
        related="property_id.subproject_id", string="Sub Project", store=True)
    total_area = fields.Float(related="property_id.total_area")
    usable_area = fields.Float(related="property_id.usable_area")
    measure_unit = fields.Selection(related="property_id.measure_unit")
    region_id = fields.Many2one(related="property_id.region_id")
    zip = fields.Char(related="property_id.zip")
    street = fields.Char(related="property_id.street", translate=True)
    street2 = fields.Char(related="property_id.street2", translate=True)
    city_id = fields.Many2one(related="property_id.city_id", string='City')
    country_id = fields.Many2one(
        related="property_id.country_id", string='Country')
    state_id = fields.Many2one(related="property_id.state_id")

    # Broker Details
    is_any_broker = fields.Boolean(string='Any Broker')
    broker_id = fields.Many2one('res.partner', string='Broker', domain=[
                                ('user_type', '=', 'broker')])
    broker_final_commission = fields.Monetary(
        string='Commission', compute="_compute_broker_final_commission")
    broker_commission = fields.Monetary(string='Commission ')
    commission_type = fields.Selection(
        [('f', 'Fix'), ('p', 'Percentage')], string="Commission Type")
    broker_commission_percentage = fields.Float(string='Percentage')
    commission_from = fields.Selection(
        [('customer', 'Customer'), ('landlord', 'Landlord',)], string="Commission From")
    broker_bill_id = fields.Many2one(
        'account.move', string='Broker Bill', readonly=True)
    broker_bill_payment_state = fields.Selection(
        related='broker_bill_id.payment_state', string="Payment Status ")
    broker_invoice_id = fields.Many2one(
        'account.move', string="Broker Invoice")
    broker_invoice_payment_state = fields.Selection(string="Broker Invoice Payment State",
                                                    related="broker_invoice_id.payment_state")

    # Customer Detail
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[
                                  ('user_type', '=', 'customer')])
    customer_phone = fields.Char(string="Phone", related="customer_id.phone")
    customer_email = fields.Char(string="Email", related="customer_id.email")

    # Landlord Details
    landlord_id = fields.Many2one(
        related="property_id.landlord_id", store=True)
    landlord_phone = fields.Char(
        related="landlord_id.phone", string="Landlord Phone")
    landlord_email = fields.Char(
        related="landlord_id.email", string="Landlord Email")

    # Payment Details & Remaining Payment
    payment_schedule_id = fields.Many2one('payment.schedule',
                                         string='Payment Schedule',
                                         domain=[('schedule_type', '=', 'sale'), ('active', '=', True)],
                                         help='Select payment schedule to auto-generate invoices')
    use_schedule = fields.Boolean(string='Use Payment Schedule', default=False)
    schedule_from_property = fields.Boolean(
        string='Inherited from Property',
        default=False,
        help='True if payment schedule was automatically inherited from property')
    payment_term = fields.Selection([
        ('monthly', 'Monthly'),
        ('full_payment', 'Full Payment'),
        ('quarterly', 'Quarterly'),
        ('bi_annual', 'Bi-Annual (6 Months)'),
        ('annual', 'Annual')
    ], string='Payment Term', help='Frequency of installment payments')
    sale_invoice_ids = fields.One2many(
        'sale.invoice', 'property_sold_id', string="Invoices")
    book_price = fields.Monetary(string='Booking Amount',
                                 compute='_compute_booking_amount',
                                 store=True,
                                 readonly=False,
                                 help='Booking/Reservation payment amount')
    sale_price = fields.Monetary(string='Confirmed Sale Price', store=True)
    ask_price = fields.Monetary(string='Customer Ask Price')
    book_invoice_id = fields.Many2one(
        'account.move', string='Advance', readonly=True)
    book_invoice_payment_state = fields.Selection(
        related='book_invoice_id.payment_state', string="Payment Status")
    book_invoice_state = fields.Boolean(string='Invoice State')
    remain_invoice_id = fields.Many2one('account.move', string="Invoice")
    remain_check = fields.Boolean(compute="_compute_remain_check")
    # Maintenance and utility Service
    is_any_maintenance = fields.Boolean(
        related="property_id.is_maintenance_service")
    total_maintenance = fields.Monetary(
        related="property_id.total_maintenance")
    is_utility_service = fields.Boolean(related="property_id.is_extra_service")
    total_service = fields.Monetary(related="property_id.extra_service_cost")
    # Total Amount Calculation
    total_sell_amount = fields.Monetary(
        string="Total Amount", compute="compute_sell_price")
    payable_amount = fields.Monetary(
        string="Installment Total Amount", compute="compute_sell_price")

    # Invoice Payment Calculation
    total_untaxed_amount = fields.Monetary(
        string="Untaxed Amount", compute="_compute_remain_amount")
    tax_amount = fields.Monetary(
        string="Tax Amount", compute="_compute_remain_amount")
    total_amount = fields.Monetary(
        string="Total Amount ", compute="_compute_remain_amount")
    remaining_amount = fields.Monetary(
        string="Remaining Amount", compute="_compute_remain_amount")
    paid_amount = fields.Monetary(
        string="Paid", compute="_compute_remain_amount")

    # Documents
    sold_document = fields.Binary(string='Sold Document')
    file_name = fields.Char('File Name', translate=True)

    # Additional Fees (Not included in property price)
    dld_fee = fields.Monetary(string='DLD Fee',
                              compute='_compute_dld_fee',
                              store=True,
                              readonly=False,
                              help='Dubai Land Department registration fee (separate from property price)')
    dld_fee_percentage = fields.Float(string='DLD Fee %', default=4.0,
                                      help='DLD Fee as percentage of sale price (default 4%)')
    dld_fee_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Sale Price')
    ], string='DLD Fee Type', default='percentage',
       help='Calculate DLD fee as fixed amount or percentage')
    dld_fee_due_days = fields.Integer(string='DLD Due Days', default=30,
                                      help='Number of days after booking when DLD fee is due')
    
    admin_fee = fields.Monetary(string='Admin Fee',
                                compute='_compute_admin_fee',
                                store=True,
                                readonly=False,
                                help='Administrative processing fee (separate from property price)')
    admin_fee_percentage = fields.Float(string='Admin Fee %', default=2.0,
                                        help='Admin Fee as percentage of sale price (default 2%)')
    admin_fee_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Sale Price')
    ], string='Admin Fee Type', default='fixed',
       help='Calculate admin fee as fixed amount or percentage')
    admin_fee_due_days = fields.Integer(string='Admin Due Days', default=30,
                                        help='Number of days after booking when admin fee is due')
    
    total_additional_fees = fields.Monetary(string='Total Additional Fees',
                                           compute='_compute_total_additional_fees',
                                           store=True,
                                           help='DLD Fee + Admin Fee')
    
    # Booking/Reservation Payment Settings
    booking_percentage = fields.Float(
        string='Booking %',
        help='Booking amount as percentage of sale price. '
             'Inherited from property (which may inherit from project), or set manually.')
    booking_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Sale Price')
    ], string='Booking Type',
       help='How booking amount is calculated. Inherited from property/project or set manually.')
    
    # Booking Requirements & Payment Status
    booking_requirements_met = fields.Boolean(
        string='Booking Requirements Met',
        compute='_compute_booking_requirements_met',
        store=True,
        help='True when booking fee + DLD fee + Admin fee are fully paid')
    booking_invoice_paid = fields.Boolean(
        string='Booking Invoice Paid',
        compute='_compute_booking_requirements_met',
        store=True)
    dld_invoice_paid = fields.Boolean(
        string='DLD Invoice Paid',
        compute='_compute_booking_requirements_met',
        store=True)
    admin_invoice_paid = fields.Boolean(
        string='Admin Invoice Paid',
        compute='_compute_booking_requirements_met',
        store=True)
    can_create_installments = fields.Boolean(
        string='Can Create Installments',
        compute='_compute_booking_requirements_met',
        store=True,
        help='True when all booking requirements are met and contract is booked')
    booking_payment_progress = fields.Float(
        string='Booking Payment Progress',
        compute='_compute_booking_requirements_met',
        store=True,
        help='Percentage of required booking payments completed (0-100%)')
    
    # DLD and Admin Fee Product Items
    dld_fee_item_id = fields.Many2one('product.product',
                                      string="DLD Fee Item",
                                      default=lambda self: self.env.ref('rental_management.property_product_dld_fee',
                                                                        raise_if_not_found=False))
    admin_fee_item_id = fields.Many2one('product.product',
                                        string="Admin Fee Item",
                                        default=lambda self: self.env.ref('rental_management.property_product_admin_fee',
                                                                          raise_if_not_found=False))
    
    # Include fees in payment plan
    include_dld_in_plan = fields.Boolean(string='Include DLD in Payment Plan', default=True,
                                         help='Automatically add DLD fee invoice to payment schedule')
    include_admin_in_plan = fields.Boolean(string='Include Admin in Payment Plan', default=True,
                                           help='Automatically add admin fee invoice to payment schedule')

    # Bank Account Details for Payment Instructions
    payment_bank_name = fields.Char(string='Payment Bank Name',
                                    help='Bank name for booking/installment payments')
    payment_account_name = fields.Char(string='Payment Account Name',
                                       help='Account holder name for payments')
    payment_account_number = fields.Char(string='Payment Account Number',
                                         help='Bank account number for payments')
    payment_iban = fields.Char(string='Payment IBAN',
                               help='International Bank Account Number for payments')
    payment_swift = fields.Char(string='Payment SWIFT Code',
                                help='SWIFT code for international transfers')
    payment_currency = fields.Char(string='Payment Currency', default='AED',
                                   help='Currency for payment account')
    
    dld_bank_name = fields.Char(string='DLD Bank Name',
                                help='Bank name for DLD fee payments')
    dld_account_name = fields.Char(string='DLD Account Name',
                                   help='Account holder name for DLD fees')
    dld_account_number = fields.Char(string='DLD Account Number',
                                     help='Bank account number for DLD fees')
    dld_iban = fields.Char(string='DLD IBAN',
                           help='International Bank Account Number for DLD payments')
    dld_swift = fields.Char(string='DLD SWIFT Code',
                            help='SWIFT code for DLD transfers')
    dld_currency = fields.Char(string='DLD Currency', default='AED',
                               help='Currency for DLD account')
    
    admin_bank_name = fields.Char(string='Admin Bank Name',
                                  help='Bank name for admin fee payments')
    admin_account_name = fields.Char(string='Admin Account Name',
                                     help='Account holder name for admin fees')
    admin_account_number = fields.Char(string='Admin Account Number',
                                       help='Bank account number for admin fees')
    admin_iban = fields.Char(string='Admin IBAN',
                             help='International Bank Account Number for admin payments')
    admin_swift = fields.Char(string='Admin SWIFT Code',
                              help='SWIFT code for admin transfers')
    admin_currency = fields.Char(string='Admin Currency', default='AED',
                                 help='Currency for admin account')

    # Terms & Conditions
    term_condition = fields.Html(string='Term and Condition')

    # Item & Taxes
    booking_item_id = fields.Many2one('product.product',
                                      string="Booking Item",
                                      default=lambda self: self.env.ref('rental_management.property_product_2',
                                                                        raise_if_not_found=False))
    broker_item_id = fields.Many2one('product.product',
                                     string="Broker Item",
                                     default=lambda self: self.env.ref('rental_management.property_product_3',
                                                                       raise_if_not_found=False))
    installment_item_id = fields.Many2one('product.product',
                                          string="Installment Item",
                                          default=lambda self: self.env.ref('rental_management.property_product_1',
                                                                            raise_if_not_found=False))
    is_taxes = fields.Boolean(string="Taxes ?")
    taxes_ids = fields.Many2many('account.tax', string="Taxes")

    maintenance_request_count = fields.Integer(string="Maintenance Request Count",
                                               compute="_compute_maintenance_request_count")

    # DEPRECATED START---------------------------------------------------
    sold_invoice_id = fields.Many2one('account.move',
                                      string='Sold Invoice',
                                      readonly=True)
    sold_invoice_state = fields.Boolean(string='Sold Invoice State')
    sold_invoice_payment_state = fields.Selection(related='sold_invoice_id.payment_state',
                                                  string="Payment Status  ")

    # --------------------------------------------------------DEPRECATED END

    # Create Write, Scheduler, Name-get
    # Create
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sold_seq', _('New')) == _('New'):
                vals['sold_seq'] = self.env['ir.sequence'].next_by_code(
                    'property.vendor') or _('New')
        res = super(PropertyVendor, self).create(vals_list)
        return res

    # Default Get
    @api.model
    def default_get(self, fields_list):
        res = super(PropertyVendor, self).default_get(fields_list)
        default_installment_item = self.env['ir.config_parameter'].sudo().get_param(
            'rental_management.account_installment_item_id')
        res['installment_item_id'] = int(default_installment_item) if default_installment_item else self.env.ref(
            'rental_management.property_product_1').id
        return res

    # Name Get
    def name_get(self):
        data = []
        for rec in self:
            data.append((rec.id, '%s - %s' %
                         (rec.sold_seq, rec.customer_id.name)))
        return data
    
    # Onchange Methods
    @api.onchange('payment_schedule_id')
    def _onchange_payment_schedule(self):
        """Update use_schedule when payment schedule is selected"""
        if self.payment_schedule_id:
            self.use_schedule = True
            total_invoices = sum(self.payment_schedule_id.schedule_line_ids.mapped('number_of_installments'))
            return {
                'warning': {
                    'title': _('Payment Schedule Selected'),
                    'message': _('Payment schedule "%s" will generate %d invoice(s). '
                               'Click "Generate from Schedule" button after saving.') % (
                        self.payment_schedule_id.name, total_invoices
                    )
                }
            }
        else:
            self.use_schedule = False

    # Scheduler
    @api.model
    def sale_recurring_invoice(self):
        reminder_days = self.env['ir.config_parameter'].sudo(
        ).get_param('rental_management.sale_reminder_days')
        today_date = fields.Date.today()
        # today_date = datetime.date(2023, 7, 29)
        sale_invoice = self.env['sale.invoice'].sudo().search(
            [('invoice_created', '=', False)])
        for data in sale_invoice:
            reminder_date = data.invoice_date - \
                relativedelta(days=int(reminder_days))
            invoice_post_type = self.env['ir.config_parameter'].sudo(
            ).get_param('rental_management.invoice_post_type')
            if today_date == reminder_date:
                record = {
                    'product_id': data.property_sold_id.installment_item_id.id,
                    'name': data.name + "\n" + (data.desc if data.desc else ""),
                    'quantity': 1,
                    'price_unit': data.amount,
                    'tax_ids': data.tax_ids.ids if data.tax_ids else False,
                }
                invoice_lines = [(0, 0, record)]
                sold_data = {
                    'partner_id': data.property_sold_id.customer_id.id,
                    'move_type': 'out_invoice',
                    'sold_id': data.property_sold_id.id,
                    'invoice_date': data.invoice_date,
                    'invoice_line_ids': invoice_lines
                }
                invoice_id = self.env['account.move'].sudo().create(sold_data)
                if invoice_post_type == 'automatically':
                    invoice_id.action_post()
                data.invoice_id = invoice_id.id
                data.invoice_created = True

    # Compute
    # Total amount paid amount, remaining amount
    @api.depends('sale_invoice_ids')
    def _compute_remain_amount(self):
        for rec in self:
            paid_amount = 0.0
            tax_amount = 0.0
            total_untaxed_amount = 0.0
            if rec.sale_invoice_ids:
                for data in rec.sale_invoice_ids:
                    total_untaxed_amount = total_untaxed_amount + data.amount
                    tax_amount = tax_amount + data.tax_amount
                    paid_amount = paid_amount + data.paid_amount
            rec.tax_amount = tax_amount
            rec.total_untaxed_amount = total_untaxed_amount
            rec.total_amount = tax_amount + total_untaxed_amount
            rec.paid_amount = paid_amount
            rec.remaining_amount = tax_amount + total_untaxed_amount - paid_amount

    # Remain Check
    @api.depends('sale_invoice_ids')
    def _compute_remain_check(self):
        for rec in self:
            if rec.sale_invoice_ids:
                for data in rec.sale_invoice_ids:
                    if data.is_remain_invoice:
                        rec.remain_check = True
                    else:
                        rec.remain_check = False
            else:
                rec.remain_check = False

    # Broker Commission
    @api.depends('is_any_broker', 'broker_id', 'commission_type', 'sale_price', 'broker_commission_percentage',
                 'sale_price', 'broker_commission')
    def _compute_broker_final_commission(self):
        for rec in self:
            if rec.is_any_broker:
                if rec.commission_type == 'p':
                    rec.broker_final_commission = rec.sale_price * \
                        rec.broker_commission_percentage / 100
                else:
                    rec.broker_final_commission = rec.broker_commission
            else:
                rec.broker_final_commission = 0.0

    # Count
    def _compute_maintenance_request_count(self):
        for rec in self:
            request_count = self.env['maintenance.request'].search_count(
                [('sell_contract_id', 'in', [rec.id])])
            rec.maintenance_request_count = request_count

    # DLD Fee Calculation
    @api.depends('sale_price', 'ask_price', 'dld_fee_percentage', 'dld_fee_type')
    def _compute_dld_fee(self):
        """Calculate DLD fee based on type and percentage"""
        for rec in self:
            if rec.dld_fee_type == 'percentage':
                # Use sale_price, fallback to ask_price if not set
                base_price = rec.sale_price if rec.sale_price else rec.ask_price
                if base_price:
                    rec.dld_fee = round((base_price * rec.dld_fee_percentage) / 100, 2)
                else:
                    rec.dld_fee = 0.0
            # If fixed type, preserve the manually set amount (readonly=False allows user input)
    
    @api.onchange('sale_price', 'ask_price', 'dld_fee_percentage', 'dld_fee_type')
    def _onchange_dld_fee(self):
        """Trigger DLD fee recalculation on field changes"""
        if self.dld_fee_type == 'percentage':
            base_price = self.sale_price if self.sale_price else self.ask_price
            if base_price:
                self.dld_fee = round((base_price * self.dld_fee_percentage) / 100, 2)
    
    # Admin Fee Calculation
    @api.depends('sale_price', 'ask_price', 'admin_fee_percentage', 'admin_fee_type')
    def _compute_admin_fee(self):
        """Calculate Admin fee based on type and percentage"""
        for rec in self:
            if rec.admin_fee_type == 'percentage':
                # Use sale_price, fallback to ask_price if not set
                base_price = rec.sale_price if rec.sale_price else rec.ask_price
                if base_price:
                    rec.admin_fee = round((base_price * rec.admin_fee_percentage) / 100, 2)
                else:
                    rec.admin_fee = 0.0
            # If fixed type, preserve the manually set amount (readonly=False allows user input)
    
    @api.onchange('sale_price', 'ask_price', 'admin_fee_percentage', 'admin_fee_type')
    def _onchange_admin_fee(self):
        """Trigger Admin fee recalculation on field changes"""
        if self.admin_fee_type == 'percentage':
            base_price = self.sale_price if self.sale_price else self.ask_price
            if base_price:
                self.admin_fee = round((base_price * self.admin_fee_percentage) / 100, 2)
    
    # Payment Schedule Inheritance from Property
    @api.onchange('property_id')
    def _onchange_property_id_payment_schedule(self):
        """Auto-inherit payment schedule from property when property is selected.
        This enables UAE real estate sector payment plan integration where 
        payment plans are defined at property level and inherited by contracts.
        """
        if self.property_id:
            # Check if property has a sale payment plan configured
            if self.property_id.is_payment_plan and self.property_id.payment_schedule_id:
                self.payment_schedule_id = self.property_id.payment_schedule_id
                self.use_schedule = True
                self.schedule_from_property = True
                
                # Calculate total invoices from schedule
                total_invoices = sum(
                    line.number_of_installments 
                    for line in self.payment_schedule_id.schedule_line_ids
                )
                
                # Add booking invoice count if not in schedule
                has_booking = any(line.payment_type == 'booking' 
                                for line in self.payment_schedule_id.schedule_line_ids)
                if not has_booking:
                    total_invoices += 1  # Add booking invoice
                
                return {
                    'warning': {
                        'title': _('Payment Schedule Inherited'),
                        'message': _(
                            'Payment schedule "%s" has been automatically applied from property. '
                            'This schedule will generate %d sale invoices based on the UAE payment plan structure. '
                            'You can change this schedule if needed.'
                        ) % (self.payment_schedule_id.name, total_invoices)
                    }
                }
            else:
                # No sale payment schedule on property, reset if previously inherited
                if self.schedule_from_property:
                    self.payment_schedule_id = False
                    self.use_schedule = False
                    self.schedule_from_property = False
    
    @api.onchange('payment_schedule_id')
    def _onchange_payment_schedule(self):
        """Preview invoice count when payment schedule is selected"""
        if self.payment_schedule_id:
            self.use_schedule = True
            total_invoices = sum(line.number_of_installments 
                               for line in self.payment_schedule_id.schedule_line_ids)
            
            # Add booking, DLD, admin invoices if they will be generated
            has_booking = any(line.payment_type == 'booking' 
                            for line in self.payment_schedule_id.schedule_line_ids)
            if not has_booking:
                total_invoices += 1  # Booking invoice
            
            if self.include_dld_in_plan and self.dld_fee > 0:
                total_invoices += 1  # DLD fee invoice
            
            if self.include_admin_in_plan and self.admin_fee > 0:
                total_invoices += 1  # Admin fee invoice
            
            return {
                'warning': {
                    'title': _('Payment Schedule Selected'),
                    'message': _(
                        'This schedule will generate approximately %d sale invoices '
                        '(including booking, DLD, admin fees, and installments) based on the defined payment plan.'
                    ) % total_invoices
                }
            }
        else:
            self.use_schedule = False
    
    # Booking Requirements Check
    @api.depends('sale_invoice_ids', 'sale_invoice_ids.invoice_created', 
                 'sale_invoice_ids.payment_status', 'sale_invoice_ids.invoice_type',
                 'stage', 'dld_fee', 'admin_fee', 'book_price')
    def _compute_booking_requirements_met(self):
        """Check if all required booking payments (booking + DLD + admin) are completed"""
        for rec in self:
            # Find invoices by type
            booking_invoices = rec.sale_invoice_ids.filtered(lambda inv: inv.invoice_type == 'booking')
            dld_invoices = rec.sale_invoice_ids.filtered(lambda inv: inv.invoice_type == 'dld_fee')
            admin_invoices = rec.sale_invoice_ids.filtered(lambda inv: inv.invoice_type == 'admin_fee')
            
            # Check payment status for each required invoice
            rec.booking_invoice_paid = any(
                inv.invoice_created and inv.payment_status == 'paid' 
                for inv in booking_invoices
            ) if booking_invoices else (rec.book_price == 0)
            
            rec.dld_invoice_paid = any(
                inv.invoice_created and inv.payment_status == 'paid' 
                for inv in dld_invoices
            ) if dld_invoices else (rec.dld_fee == 0)
            
            rec.admin_invoice_paid = any(
                inv.invoice_created and inv.payment_status == 'paid' 
                for inv in admin_invoices
            ) if admin_invoices else (rec.admin_fee == 0)
            
            # All requirements met when all required invoices are paid
            rec.booking_requirements_met = (
                rec.booking_invoice_paid and 
                rec.dld_invoice_paid and 
                rec.admin_invoice_paid
            )
            
            # Can create installments only when requirements met AND stage is booked
            rec.can_create_installments = (
                rec.booking_requirements_met and 
                rec.stage == 'booked'
            )
            
            # Calculate payment progress (0-100%)
            total_required = 0
            total_paid = 0
            
            if rec.book_price > 0:
                total_required += 1
                if rec.booking_invoice_paid:
                    total_paid += 1
            
            if rec.dld_fee > 0:
                total_required += 1
                if rec.dld_invoice_paid:
                    total_paid += 1
            
            if rec.admin_fee > 0:
                total_required += 1
                if rec.admin_invoice_paid:
                    total_paid += 1
            
            rec.booking_payment_progress = (
                (total_paid / total_required * 100) if total_required > 0 else 100.0
            )
    
    # Booking Amount Calculation
    @api.depends('sale_price', 'booking_percentage', 'booking_type')
    def _compute_booking_amount(self):
        """Calculate booking amount based on type and percentage"""
        for rec in self:
            if rec.booking_type == 'percentage':
                if rec.sale_price:
                    rec.book_price = round((rec.sale_price * rec.booking_percentage) / 100, 2)
                else:
                    rec.book_price = 0.0
            # If fixed type, preserve the manually set amount (readonly=False allows user input)

    # Additional Fees Calculation
    @api.depends('dld_fee', 'admin_fee')
    def _compute_total_additional_fees(self):
        """Calculate total additional fees (DLD + Admin)"""
        for rec in self:
            rec.total_additional_fees = rec.dld_fee + rec.admin_fee

    # Sell Price Calculation
    @api.depends('sale_price',
                 'ask_price',
                 'book_price',
                 'total_service',
                 'is_utility_service',
                 'total_maintenance',
                 'is_any_maintenance',
                 'dld_fee',
                 'admin_fee')
    def compute_sell_price(self):
        for rec in self:
            tax_amount = 0.0
            total_sell_amount = 0.0
            if rec.is_any_maintenance:
                total_sell_amount = total_sell_amount + rec.total_maintenance
            if rec.is_utility_service:
                total_sell_amount = total_sell_amount + rec.total_service
            
            # Use sale_price if set, otherwise use ask_price (customer price)
            base_price = rec.sale_price if rec.sale_price else rec.ask_price
            total_sell_amount = total_sell_amount + base_price
            
            # Payable amount = Base Price + Booking + DLD + Admin (Total Customer Obligation)
            rec.payable_amount = total_sell_amount + abs(rec.book_price) + rec.dld_fee + rec.admin_fee
            rec.tax_amount = tax_amount
            rec.total_sell_amount = total_sell_amount

    # Mail Template
    # Sold Mail
    def send_sold_mail(self):
        mail_template = self.env.ref(
            'rental_management.property_sold_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)

    # Button
    # Advance Payment Invoice
    def action_book_invoice(self):
        mail_template = self.env.ref(
            'rental_management.property_book_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        record = {
            'product_id': self.env.ref('rental_management.property_product_1').id,
            'name': 'Booked Amount of   ' + self.property_id.name,
            'quantity': 1,
            'price_unit': self.book_price
        }
        invoice_lines = [(0, 0, record)]
        data = {
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines
        }
        book_invoice_id = self.env['account.move'].sudo().create(data)
        book_invoice_id.sold_id = self.id
        invoice_post_type = self.env['ir.config_parameter'].sudo(
        ).get_param('rental_management.invoice_post_type')
        if invoice_post_type == 'automatically':
            book_invoice_id.action_post()
        self.book_invoice_id = book_invoice_id.id
        self.book_invoice_state = True
        self.property_id.stage = 'booked'
        self.stage = 'booked'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Booked Invoice',
            'res_model': 'account.move',
            'res_id': book_invoice_id.id,
            'view_mode': 'form,tree',
            'target': 'current'
        }

    # Refund Amount
    def action_refund_amount(self):
        for rec in self:
            rec.stage = 'refund'
            rec.property_id.stage = "available"
            rec.property_id.sold_booking_id = None

    # Cancel Contract
    def action_cancel_contract(self):
        for rec in self:
            rec.stage = 'cancel'
            rec.property_id.stage = "available"
            rec.property_id.sold_booking_id = None

    # Lock Contract
    def action_locked_contract(self):
        for rec in self:
            rec.stage = 'locked'

    # Receive Remain Payment and Create Invoice
    def action_receive_remaining(self):
        amount = 0.0
        for rec in self.sale_invoice_ids:
            if not rec.invoice_created:
                amount = amount + rec.amount
        sold_invoice_data = {
            'name': "Remaining Invoice Payment",
            'property_sold_id': self.id,
            'invoice_date': fields.Date.today(),
            'amount': amount,
            'is_remain_invoice': True
        }
        self.env['sale.invoice'].create(sold_invoice_data)
        for data in self.sale_invoice_ids:
            if not data.invoice_created and (not data.is_remain_invoice):
                data.unlink()

    def action_reset_installments(self):
        """Reset Installments"""
        self.sale_invoice_ids = [(6, 0, 0)]
    
    def action_generate_booking_invoices(self):
        """
        Generate initial booking invoices ONLY (booking + DLD + admin fees).
        This must be done before creating installment plan.
        Called automatically when contract is created, or manually via button.
        """
        self.ensure_one()
        
        if self.stage != 'draft':
            raise UserError(_(
                "Booking invoices can only be generated for contracts in Draft stage.\n\n"
                "Current stage: %s\n"
                "Please ensure the contract is in Draft stage before generating booking invoices."
            ) % dict(self._fields['stage'].selection).get(self.stage))
        
        # Clear any existing invoices (in case of regeneration)
        self.sale_invoice_ids.unlink()
        
        invoice_lines = []
        invoice_date = self.date or fields.Date.today()
        
        # 1. Generate Booking Invoice (if booking amount > 0)
        if self.book_price > 0:
            booking_data = {
                'property_sold_id': self.id,
                'invoice_date': invoice_date,
                'amount': abs(self.book_price),
                'invoice_type': 'booking',
                'desc': _('Booking Fee - %s%% of sale price') % self.booking_percentage 
                        if self.booking_type == 'percentage' 
                        else _('Booking Fee'),
                'invoice_created': False,
                'payment_status': 'unpaid',
            }
            invoice_lines.append((0, 0, booking_data))
        
        # 2. Generate DLD Fee Invoice (if DLD fee > 0)
        if self.include_dld_in_plan and self.dld_fee > 0:
            dld_due_date = invoice_date + relativedelta(days=self.dld_fee_due_days)
            dld_data = {
                'property_sold_id': self.id,
                'invoice_date': dld_due_date,
                'amount': self.dld_fee,
                'invoice_type': 'dld_fee',
                'desc': _('DLD Fee - Dubai Land Department (Due %d days after booking - 4%% of sale price)') % self.dld_fee_due_days,
                'invoice_created': False,
                'payment_status': 'unpaid',
            }
            invoice_lines.append((0, 0, dld_data))
        
        # 3. Generate Admin Fee Invoice (if admin fee > 0)
        if self.include_admin_in_plan and self.admin_fee > 0:
            admin_due_date = invoice_date + relativedelta(days=self.admin_fee_due_days)
            admin_data = {
                'property_sold_id': self.id,
                'invoice_date': admin_due_date,
                'amount': self.admin_fee,
                'invoice_type': 'admin_fee',
                'desc': _('Admin Fee - Administrative Processing (Due %d days after booking)') % self.admin_fee_due_days,
                'invoice_created': False,
                'payment_status': 'unpaid',
            }
            invoice_lines.append((0, 0, admin_data))
        
        # Create all booking invoices in one transaction
        if invoice_lines:
            self.write({'sale_invoice_ids': invoice_lines})
        
        # Update property and contract stage
        self.property_id.stage = 'booked'
        # Keep contract in 'draft' stage until booking requirements are paid
        # Stage will be updated to 'booked' when all invoices are paid
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Booking Invoices Generated'),
                'message': _(
                    'Generated %d booking invoices:\n\n'
                    '%s\n\n'
                    'Contract will move to "Booked" stage once all booking invoices are paid.\n'
                    'Then you can create the installment plan for remaining balance.'
                ) % (
                    len(invoice_lines),
                    '\n'.join([
                        f"• {line[2]['desc']}: {line[2]['amount']:,.2f} AED"
                        for line in invoice_lines
                    ])
                ),
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
    
    def action_confirm_booking_paid(self):
        """
        Manual confirmation that all booking requirements are paid.
        Moves contract from 'draft' to 'booked' stage.
        After this, user can create installment plan.
        """
        self.ensure_one()
        
        if self.stage != 'draft':
            raise UserError(_(
                "This action is only available for contracts in Draft stage.\n\n"
                "Current stage: %s"
            ) % dict(self._fields['stage'].selection).get(self.stage))
        
        if not self.booking_requirements_met:
            unpaid_items = []
            if not self.booking_invoice_paid:
                unpaid_items.append(f"• Booking Fee ({abs(self.book_price):,.2f} AED)")
            if not self.dld_invoice_paid:
                unpaid_items.append(f"• DLD Fee ({self.dld_fee:,.2f} AED)")
            if not self.admin_invoice_paid:
                unpaid_items.append(f"• Admin Fee ({self.admin_fee:,.2f} AED)")
            
            raise UserError(_(
                "Cannot confirm booking - Not all required payments are completed.\n\n"
                "Unpaid invoices:\n%s\n\n"
                "Please ensure all booking invoices are marked as 'Paid' before confirming."
            ) % '\n'.join(unpaid_items))
        
        # Move to booked stage
        self.write({'stage': 'booked'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Booking Confirmed'),
                'message': _(
                    'Contract has been moved to "Booked" stage.\n\n'
                    'You can now create the installment plan for remaining property payments.\n\n'
                    'Remaining balance to be paid via installments:\n'
                    '%s AED'
                ) % f"{(self.sale_price - abs(self.book_price)):,.2f}",
                'sticky': False,
            }
        }
    
    def action_generate_from_schedule(self):
        """Generate sale invoices from payment schedule including DLD and Admin fees"""
        self.ensure_one()
        
        # VALIDATION: Check booking requirements are met before creating installments
        if not self.can_create_installments:
            if self.stage == 'draft':
                raise UserError(_(
                    "⚠️ BOOKING REQUIREMENTS NOT MET\n\n"
                    "Before creating the installment plan, the client must first pay:\n\n"
                    "📋 Required Payments:\n"
                    "   • Booking Fee: %s AED %s\n"
                    "   • DLD Fee: %s AED %s\n"
                    "   • Admin Fee: %s AED %s\n\n"
                    "💡 WORKFLOW:\n"
                    "   1. Generate booking invoices (if not done)\n"
                    "   2. Client pays all booking requirements\n"
                    "   3. Mark invoices as 'Paid' in the Invoices tab\n"
                    "   4. Click 'Confirm Booking Paid' button\n"
                    "   5. Then you can create installments\n\n"
                    "Current Payment Progress: %.0f%%"
                ) % (
                    f"{abs(self.book_price):,.2f}",
                    "✅ PAID" if self.booking_invoice_paid else "❌ UNPAID",
                    f"{self.dld_fee:,.2f}",
                    "✅ PAID" if self.dld_invoice_paid else "❌ UNPAID",
                    f"{self.admin_fee:,.2f}",
                    "✅ PAID" if self.admin_invoice_paid else "❌ UNPAID",
                    self.booking_payment_progress
                ))
            else:
                raise UserError(_(
                    "Cannot create installments.\n\n"
                    "Current stage: %s\n"
                    "Contract must be in 'Booked' stage with all booking requirements paid."
                ) % dict(self._fields['stage'].selection).get(self.stage))
        
        if not self.use_schedule or not self.payment_schedule_id:
            raise UserError(_('Please select a payment schedule first.'))
        
        if not self.date:
            raise UserError(_('Contract date is required to generate invoice schedule.'))
        
        # Clear existing invoices
        self.sale_invoice_ids.unlink()
        
        contract_start_date = self.date
        total_amount = self.sale_price
        sequence = 1
        booking_date = None
        
        # 1. Generate Booking/Reservation Payment (First invoice)
        if self.book_price > 0:
            booking_date = contract_start_date
            self.env['sale.invoice'].create({
                'property_sold_id': self.id,
                'name': _('Booking/Reservation Payment'),
                'amount': self.book_price,
                'invoice_date': booking_date,
                'invoice_created': False,
                'invoice_type': 'booking',
                'sequence': sequence,
                'desc': _('Booking deposit - %s%% of sale price') % self.booking_percentage if self.booking_type == 'percentage' else _('Booking deposit'),
                'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes else False
            })
            sequence += 1
        
        # 2. Generate DLD Fee (Due X days after booking)
        if self.include_dld_in_plan and self.dld_fee > 0:
            dld_due_date = (booking_date or contract_start_date) + relativedelta(days=self.dld_fee_due_days)
            self.env['sale.invoice'].create({
                'property_sold_id': self.id,
                'name': _('DLD Fee - Dubai Land Department'),
                'amount': self.dld_fee,
                'invoice_date': dld_due_date,
                'invoice_created': False,
                'invoice_type': 'dld_fee',
                'sequence': sequence,
                'desc': _('DLD Fee - Due %s days after booking (%s%% of sale price)') % (
                    self.dld_fee_due_days, 
                    self.dld_fee_percentage
                ) if self.dld_fee_type == 'percentage' else _('DLD Fee - Due %s days after booking') % self.dld_fee_due_days,
                'tax_ids': False  # DLD fees typically not taxed
            })
            sequence += 1
        
        # 3. Generate Admin Fee (Due X days after booking)
        if self.include_admin_in_plan and self.admin_fee > 0:
            admin_due_date = (booking_date or contract_start_date) + relativedelta(days=self.admin_fee_due_days)
            self.env['sale.invoice'].create({
                'property_sold_id': self.id,
                'name': _('Admin Fee - Administrative Processing'),
                'amount': self.admin_fee,
                'invoice_date': admin_due_date,
                'invoice_created': False,
                'invoice_type': 'admin_fee',
                'sequence': sequence,
                'desc': _('Admin Fee - Due %s days after booking') % self.admin_fee_due_days,
                'tax_ids': False  # Admin fees typically not taxed
            })
            sequence += 1
        
        # 4. Generate Payment Schedule Installments
        # Calculate remaining amount (after booking) - NOTE: Only property price, NOT including DLD/Admin
        # DLD and Admin are separate invoices, not part of installment calculations
        property_base_price = self.property_id.price if self.property_id else self.sale_price
        remaining_amount = property_base_price - abs(self.book_price)
        
        for line in self.payment_schedule_id.schedule_line_ids.sorted('days_after'):
            # Calculate amount for this line based on remaining amount
            line_amount = (remaining_amount * line.percentage) / 100
            
            # Calculate frequency in days
            frequency_days = {
                'one_time': 0,
                'monthly': 30,
                'quarterly': 90,
                'bi_annual': 180,
                'annual': 365
            }.get(line.installment_frequency, 0)
            
            # Generate invoices based on number of installments (safeguard against division by zero)
            num_installments = max(line.number_of_installments, 1)
            amount_per_invoice = round(line_amount / num_installments, 2)
            
            for installment_num in range(num_installments):
                # Calculate invoice date
                days_offset = line.days_after + (installment_num * frequency_days)
                invoice_date = contract_start_date + relativedelta(days=days_offset)
                
                # Create invoice line
                invoice_name = line.name
                if line.number_of_installments > 1:
                    invoice_name = f"{line.name} ({installment_num + 1}/{line.number_of_installments})"
                
                self.env['sale.invoice'].create({
                    'property_sold_id': self.id,
                    'name': invoice_name,
                    'amount': amount_per_invoice,
                    'invoice_date': invoice_date,
                    'invoice_created': False,
                    'invoice_type': 'installment',
                    'sequence': sequence,
                    'desc': line.note or '',
                    'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes else False
                })
                sequence += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('Payment schedule generated successfully with %s invoices!') % (sequence - 1),
                'sticky': False,
            }
        }

    # Confirm Sale
    def action_confirm_sale(self):
        """Confirm Sale and Update Status to SOLD"""
        if not self.sale_invoice_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'message': _("Please create installments to confirm sale."),
                    'sticky': False,
                }
            }
        self.write({
            "stage": "sold"
        })
        self.customer_id.write({
            "is_sold_customer": True
        })
        self.property_id.write({
            "stage": "sold"
        })
        # Send Confirmation Mail
        self.send_sold_mail()

    # Smart Button
    def action_maintenance_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request',
            'res_model': 'maintenance.request',
            'domain': [('sell_contract_id', '=', self.id)],
            'context': {'create': False},
            'view_mode': 'kanban,list,form',
            'target': 'current'
        }


class SaleInvoice(models.Model):
    _name = 'sale.invoice'
    _description = "Sale Invoice"
    _order = 'invoice_date, sequence, id'

    name = fields.Char(string="Title", translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    property_sold_id = fields.Many2one('property.vendor',
                                       string="Property Sold",
                                       ondelete='cascade')
    invoice_id = fields.Many2one('account.move', string="Invoice")
    invoice_date = fields.Date(string="Date")
    payment_state = fields.Selection(related="invoice_id.payment_state")
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  string='Currency')
    amount = fields.Monetary(string="Amount")
    invoice_created = fields.Boolean()
    desc = fields.Text(string="Description", translate=True)
    is_remain_invoice = fields.Boolean()
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    tax_amount = fields.Monetary(string="Tax Amount",
                                 compute="compute_tax_amount")
    
    # Invoice Type for categorization
    invoice_type = fields.Selection([
        ('booking', 'Booking/Reservation'),
        ('dld_fee', 'DLD Fee'),
        ('admin_fee', 'Admin Fee'),
        ('installment', 'Installment'),
        ('handover', 'Handover Payment'),
        ('completion', 'Completion Payment'),
        ('other', 'Other')
    ], string='Invoice Type', default='installment',
       help='Type of payment for categorization and reporting')

    # Payment Status (Required for booking workflow validation)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], string='Payment Status', 
       compute='_compute_payment_status',
       store=True,
       help='Payment status of the invoice based on related account.move')

    total_amount = fields.Monetary(
        string="Total Amount", compute="_compute_amount")
    paid_amount = fields.Monetary(compute="_compute_amount")
    remaining_amount = fields.Monetary(compute="_compute_amount")

    @api.depends('tax_ids', 'amount', )
    def compute_tax_amount(self):
        for rec in self:
            total_tax = 0.0
            for data in rec.tax_ids:
                total_tax = total_tax + data.amount
            rec.tax_amount = rec.amount * total_tax / 100

    @api.depends('invoice_id', 'invoice_id.payment_state', 'invoice_id.amount_residual', 'invoice_created')
    def _compute_payment_status(self):
        """Compute payment status based on related account.move payment state"""
        for rec in self:
            if not rec.invoice_created or not rec.invoice_id:
                rec.payment_status = 'unpaid'
            elif rec.invoice_id.payment_state == 'paid':
                rec.payment_status = 'paid'
            elif rec.invoice_id.payment_state in ['partial', 'in_payment']:
                rec.payment_status = 'partial'
            else:
                rec.payment_status = 'unpaid'

    @api.depends("invoice_id")
    def _compute_amount(self):
        for rec in self:
            total_amount = 0.0
            remaining_amount = 0.0
            paid_amount = 0.0
            if rec.invoice_id:
                total_amount = rec.invoice_id.amount_total
                remaining_amount = rec.invoice_id.amount_residual
                paid_amount = rec.invoice_id.amount_total - rec.invoice_id.amount_residual 
            rec.total_amount = total_amount
            rec.remaining_amount = remaining_amount
            rec.paid_amount = paid_amount

    def action_create_invoice(self):
        invoice_post_type = self.env['ir.config_parameter'].sudo(
        ).get_param('rental_management.invoice_post_type')
        invoice_id = self.env['account.move'].sudo().create({
            'partner_id': self.property_sold_id.customer_id.id,
            'move_type': 'out_invoice',
            'sold_id': self.property_sold_id.id,
            'invoice_date': self.invoice_date,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.property_sold_id.installment_item_id.id,
                'name': self.name + "\n" + (self.desc if self.desc else ""),
                'quantity': 1,
                'price_unit': self.amount,
                'tax_ids': self.tax_ids.ids if self.tax_ids else False
            })]
        })
        if invoice_post_type == 'automatically':
            invoice_id.action_post()
        self.invoice_id = invoice_id.id
        self.invoice_created = True
        self.action_send_sale_invoice(invoice_id.id)

    def action_send_sale_invoice(self, invoice_id):
        mail_template = self.env.ref(
            'rental_management.sale_invoice_payment_mail_template')
        if mail_template:
            mail_template.send_mail(invoice_id, force_send=True)
