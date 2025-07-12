from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class PropertySale(models.Model):
    _name = 'property.sale'
    _description = 'Property Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Constants for state values
    STATE_DRAFT = 'draft'
    STATE_CONFIRM = 'confirm'
    STATE_INVOICED = 'invoiced'
    STATE_CANCELLED = 'cancelled'

    name = fields.Char(string='Sale Reference', required=True, tracking=True)
    state = fields.Selection([
        (STATE_DRAFT, 'Draft'),
        (STATE_CONFIRM, 'Confirmed'),
        (STATE_INVOICED, 'Invoiced'),
        (STATE_CANCELLED, 'Cancelled')
    ], string='State', default=STATE_DRAFT, tracking=True)

    # Property and Customer information
    property_id = fields.Many2one('property.property', string='Property', required=True, 
                                 domain="[('state', 'in', ['available', 'reserved', 'booked'])]", tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    property_offer_id = fields.Many2one('property.offer', string='Property Offer', domain="[('state', '=', 'accepted')]")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, 
                                 default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Sale date information
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    sale_date = fields.Date(string="Sale Date", default=fields.Date.today, tracking=True)
    completion_date = fields.Date(string="Expected Completion Date", compute='_compute_completion_date', store=True)
    
    # Financial information
    property_value = fields.Float(string='Property Value', compute='_compute_property_value', 
                                store=True, digits=(16, 2), tracking=True)
    sale_price = fields.Float(string='Sale Price', compute='_compute_total_selling_price', 
                            store=True, digits=(16, 2), tracking=True)
    down_payment_percentage = fields.Float(string='Down Payment (%)', default=20, tracking=True)
    down_payment = fields.Float(string='Down Payment', compute='_compute_down_payment', 
                              store=True, digits=(16, 2), tracking=True)
    dld_fee = fields.Float(string='DLD Fee', compute='_compute_dld_fee', 
                         store=True, tracking=True)
    admin_fee = fields.Float(string='Admin Fee', default=1.0, tracking=True)
    remaining_balance = fields.Float(string='Remaining Balance', compute='_compute_remaining_balance', 
                                    store=True, digits=(16, 2), tracking=True)
    no_of_installments = fields.Integer(string='No. of Installments', default=1, tracking=True)
    amount_per_installment = fields.Float(string='Amount Per Installment', compute='_compute_amount_per_installment', 
                                        store=True, digits=(16, 2), tracking=True)
    total_selling_price = fields.Float(string='Total Selling Price', compute='_compute_total_selling_price', 
                                     store=True, digits=(16, 2), tracking=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', tracking=True)
    desired_years = fields.Integer(string='Desired Years', tracking=True, 
                                 help="Number of years for installment plan")
    payment_progress = fields.Float(string="Payment Progress (%)", compute="_compute_payment_progress", 
                                   store=True, tracking=True)
    
    # Payment schedule
    property_sale_line_ids = fields.One2many('property.sale.line', 'property_sale_id', 
                                           string='Installment Lines')
    installment_count = fields.Integer(string="Installment Count", compute="_compute_installment_count")
    paid_installment_count = fields.Integer(string="Paid Installments", compute="_compute_paid_installments")

    # Broker Commission Fields
    seller_name = fields.Many2one(
        'res.partner', 
        string='Seller/Broker', 
        domain=[('is_company', '=', True)], 
        help="The seller/broker who will receive the commission",
        tracking=True
    )
    broker_commission_percentage = fields.Float(string="Broker Commission (%)", default=5.0, 
                                              digits=(5, 2), tracking=True)
    broker_commission_total_amount = fields.Monetary(
        string="Broker Commission Total Amount", 
        compute='_compute_broker_commission_total_amount', 
        store=True, currency_field='currency_id',
        tracking=True
    )
    
    # Internal Commission Fields
    sales_person_id = fields.Many2one('res.users', string="Sales Person", 
                                     default=lambda self: self.env.user, tracking=True)
    internal_commission_percentage = fields.Float(string="Internal Commission (%)", 
                                               default=2.0, digits=(5, 2), tracking=True)
    internal_commission_amount = fields.Monetary(
        string="Internal Commission Amount",
        compute='_compute_internal_commission_amount',
        store=True, currency_field='currency_id',
        tracking=True
    )
    
    # Invoice tracking
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")
    invoice_ids = fields.One2many('account.move', 'property_order_id', string="Invoices")
    broker_commission_invoice_ids = fields.One2many(
        'broker.commission.invoice', 'property_sale_id', string="Broker Commission Invoices"
    )
    broker_commission_count = fields.Integer(
        string="Commission Count", compute='_compute_broker_commission_count'
    )

    @api.depends('property_id')
    def _compute_property_value(self):
        """Compute the property value based on the property price or from accepted offer."""
        for record in self:
            if record.property_offer_id and record.property_offer_id.price > 0:
                record.property_value = record.property_offer_id.price
            else:
                record.property_value = record.property_id.property_price if record.property_id else 0.0

    @api.depends('property_value', 'dld_fee', 'admin_fee')
    def _compute_total_selling_price(self):
        """Compute the total selling price (property value + DLD fee + admin fee)."""
        for record in self:
            record.total_selling_price = record.property_value + record.dld_fee + record.admin_fee
            record.sale_price = record.total_selling_price

    @api.depends('property_value', 'down_payment_percentage')
    def _compute_down_payment(self):
        """Compute the down payment based on the property value and down payment percentage."""
        for record in self:
            if record.down_payment_percentage < 0 or record.down_payment_percentage > 100:
                raise ValidationError(_("Down payment percentage must be between 0 and 100."))
            record.down_payment = (record.down_payment_percentage / 100) * record.property_value

    @api.depends('property_value')
    def _compute_dld_fee(self):
        """Compute the DLD fee as 4% of the property value."""
        for record in self:
            record.dld_fee = 0.04 * record.property_value

    @api.depends('total_selling_price', 'down_payment', 'dld_fee', 'admin_fee')
    def _compute_remaining_balance(self):
        """Compute the remaining balance after deducting down payment, DLD fee, and admin fee."""
        for record in self:
            record.remaining_balance = record.total_selling_price - record.down_payment - record.dld_fee - record.admin_fee

    @api.depends('remaining_balance', 'no_of_installments')
    def _compute_amount_per_installment(self):
        """Compute the amount per installment based on the remaining balance and number of installments."""
        for record in self:
            if record.no_of_installments <= 0:
                raise ValidationError(_("Number of installments must be greater than 0."))
            record.amount_per_installment = record.remaining_balance / record.no_of_installments
    
    @api.depends('start_date', 'no_of_installments')
    def _compute_completion_date(self):
        """Compute the expected completion date based on start date and number of installments."""
        for record in self:
            if record.start_date and record.no_of_installments > 0:
                record.completion_date = record.start_date + relativedelta(months=record.no_of_installments)
            else:
                record.completion_date = record.start_date
    
    @api.depends('property_sale_line_ids')
    def _compute_installment_count(self):
        """Compute the number of installment lines."""
        for record in self:
            record.installment_count = len(record.property_sale_line_ids)
    
    @api.depends('property_sale_line_ids.collection_status')
    def _compute_paid_installments(self):
        """Compute the number of paid installments."""
        for record in self:
            record.paid_installment_count = len(record.property_sale_line_ids.filtered(lambda l: l.collection_status == 'paid'))
    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        """Compute the number of invoices."""
        for record in self:
            record.invoice_count = len(record.invoice_ids)
    
    @api.depends('property_sale_line_ids', 'property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        """Compute the payment progress based on paid installments."""
        for record in self:
            all_lines = record.property_sale_line_ids
            if all_lines:
                total_amount = sum(all_lines.mapped('capital_repayment'))
                paid_amount = sum(all_lines.filtered(lambda l: l.collection_status == 'paid').mapped('capital_repayment'))
                record.payment_progress = round((paid_amount / total_amount) * 100, 2) if total_amount > 0 else 0.0
            else:
                record.payment_progress = 0.0

    @api.depends('broker_commission_percentage', 'property_value')
    def _compute_broker_commission_total_amount(self):
        """Compute the total broker commission amount based on the commission percentage and property value."""
        for record in self:
            commission_amount = (record.broker_commission_percentage / 100) * record.property_value
            record.broker_commission_total_amount = commission_amount
    
    @api.depends('internal_commission_percentage', 'property_value')
    def _compute_internal_commission_amount(self):
        """Compute the internal commission amount based on the commission percentage and property value."""
        for record in self:
            commission_amount = (record.internal_commission_percentage / 100) * record.property_value
            record.internal_commission_amount = commission_amount
    
    def _compute_broker_commission_count(self):
        """Compute the count of broker commission invoices."""
        for record in self:
            record.broker_commission_count = len(record.broker_commission_invoice_ids)

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Update values when property changes"""
        for record in self:
            if record.property_id:
                # Check if there's an accepted offer
                accepted_offer = self.env['property.offer'].search([
                    ('property_id', '=', record.property_id.id),
                    ('state', '=', 'accepted')
                ], limit=1)
                
                if accepted_offer:
                    record.property_offer_id = accepted_offer.id
                    record.partner_id = accepted_offer.partner_id.id
                    record.down_payment_percentage = accepted_offer.down_payment_percentage
    
    @api.onchange('property_offer_id')
    def _onchange_property_offer(self):
        """Update values when offer changes"""
        for record in self:
            if record.property_offer_id:
                record.partner_id = record.property_offer_id.partner_id.id
                record.down_payment_percentage = record.property_offer_id.down_payment_percentage
    
    def action_confirm(self):
        """Confirm the property sale and create EMI lines."""
        for record in self:
            if record.state != self.STATE_DRAFT:
                raise UserError(_('Only draft sales can be confirmed.'))
            
            # Check if property has a verified offer if for sale
            if record.property_id.sale_rent == 'for_sale' and not record.property_offer_id:
                accepted_offers = self.env['property.offer'].search([
                    ('property_id', '=', record.property_id.id),
                    ('state', '=', 'accepted'),
                    ('document_verified', '=', True)
                ])
                if not accepted_offers:
                    raise UserError(_('This property must have an accepted and verified offer before confirming the sale.'))
            
            record._create_emi_lines()
            if record.property_id:
                record.property_id.write({
                    'state': 'sold',
                    'partner_id': record.partner_id.id
                })
            record.state = self.STATE_CONFIRM
            record.property_id._compute_payment_progress()
            record.property_id._compute_payment_details()
            _logger.info(f"Confirmed property sale {record.name}")

    def _create_emi_lines(self):
        """Create EMI lines for the property sale."""
        self.ensure_one()
        if not self.start_date:
            raise UserError(_('Start date is required to create EMI lines.'))
        if self.no_of_installments <= 0:
            raise UserError(_("Number of installments must be greater than 0."))

        # Clear existing lines
        self.property_sale_line_ids.unlink()

        # Create downpayment, DLD fee, and admin fee lines
        start_date = fields.Date.from_string(self.start_date)
        self._create_line('downpayment', self.down_payment, start_date)
        self._create_line('dld_fee', self.dld_fee, start_date)
        self._create_line('admin_fee', self.admin_fee, start_date)

        # Create EMI lines
        for i in range(self.no_of_installments):
            due_date = self._calculate_due_date(start_date, i + 1)
            self._create_line('emi', self.amount_per_installment, due_date, i + 1)

    def _create_line(self, line_type, amount, collection_date, serial_number=0):
        """Helper method to create a sale line."""
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': serial_number,
            'capital_repayment': amount,
            'remaining_capital': amount,
            'collection_date': collection_date,
            'line_type': line_type
        })

    def _calculate_due_date(self, start_date, installment_number):
        """Calculate the due date for an installment."""
        try:
            due_date = start_date + relativedelta(months=installment_number)
            if due_date.month != (start_date + relativedelta(months=installment_number)).month:
                due_date = (start_date + relativedelta(months=installment_number)).replace(day=1) - relativedelta(days=1)
            return due_date
        except Exception as e:
            raise UserError(_('Error calculating due date: %s') % str(e))

    def action_generate_broker_commission_invoice(self):
        """Generate a broker commission invoice."""
        self.ensure_one()
        
        if not self.seller_name:
            raise UserError(_("Please specify a seller/broker before generating a commission invoice."))

        # Create new commission invoice
        commission = self.env['broker.commission.invoice'].create({
            'property_sale_id': self.id,
            'seller_id': self.seller_name.id,
            'commission_percentage': self.broker_commission_percentage,
            'commission_amount': self.broker_commission_total_amount,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'broker.commission.invoice',
            'res_id': commission.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_generate_internal_commission(self):
        """Generate an internal commission record."""
        self.ensure_one()
        
        if not self.sales_person_id:
            raise UserError(_("Please specify a sales person before generating an internal commission."))
        
        # Create new internal commission
        commission = self.env['internal.commission'].create({
            'property_sale_id': self.id,
            'sales_person_id': self.sales_person_id.id,
            'commission_percentage': self.internal_commission_percentage,
            'commission_amount': self.internal_commission_amount,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'internal.commission',
            'res_id': commission.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_invoices(self):
        """View invoices related to the property sale."""
        self.ensure_one()
        invoices = self.invoice_ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
        }
        return action
    
    def action_view_broker_commissions(self):
        """View broker commissions related to the property sale."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Broker Commissions',
            'res_model': 'broker.commission.invoice',
            'view_mode': 'tree,form',
            'domain': [('property_sale_id', '=', self.id)],
            'context': {'default_property_sale_id': self.id},
        }
    
    def action_view_internal_commissions(self):
        """View internal commissions related to the property sale."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Internal Commissions',
            'res_model': 'internal.commission',
            'view_mode': 'tree,form',
            'domain': [('property_sale_id', '=', self.id)],
            'context': {'default_property_sale_id': self.id},
        }
    
    def action_cancel(self):
        """Cancel the property sale."""
        for record in self:
            # Check if any invoices are confirmed/posted
            confirmed_invoices = record.invoice_ids.filtered(lambda i: i.state == 'posted')
            if confirmed_invoices:
                raise UserError(_("Cannot cancel a sale with posted invoices. Cancel the invoices first."))
            
            # Cancel any draft invoices
            draft_invoices = record.invoice_ids.filtered(lambda i: i.state == 'draft')
            if draft_invoices:
                draft_invoices.button_cancel()
            
            # Update property state if needed
            if record.property_id.state == 'sold':
                record.property_id.write({
                    'state': 'available',
                    'partner_id': False
                })
            
            record.state = self.STATE_CANCELLED
    
    def action_draft(self):
        """Set the property sale to draft state."""
        for record in self:
            if record.invoice_ids:
                raise UserError(_("Cannot reset to draft a sale with existing invoices."))
            record.state = self.STATE_DRAFT
    
    def action_generate_all_invoices(self):
        """Generate invoices for all unpaid installments."""
        self.ensure_one()
        
        if self.state != 'confirm':
            raise UserError(_("Only confirmed sales can have invoices generated."))
        
        # Get all unpaid lines without invoices
        unpaid_lines = self.property_sale_line_ids.filtered(
            lambda l: l.collection_status == 'unpaid' and not l.invoice_id
        )
        
        if not unpaid_lines:
            raise UserError(_("No unpaid installments without invoices found."))
        
        # Group lines by collection date to create one invoice per due date
        lines_by_date = {}
        for line in unpaid_lines:
            if line.collection_date not in lines_by_date:
                lines_by_date[line.collection_date] = []
            lines_by_date[line.collection_date].append(line)
        
        created_invoices = []
        
        # Create invoices for each group
        for date, lines in lines_by_date.items():
            invoice = self._create_invoice_for_lines(lines)
            created_invoices.append(invoice.id)
        
        # Show the created invoices
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_invoices)],
        }
    
    def _create_invoice_for_lines(self, lines):
        """Create an invoice for the provided sale lines."""
        self.ensure_one()
        
        if not self.property_id.revenue_account_id:
            raise UserError(_("No revenue account defined on the property."))
        
        # Prepare invoice lines
        invoice_line_vals = []
        for line in lines:
            line_name = f"{self.property_id.name} - "
            if line.line_type == 'downpayment':
                line_name += "Down Payment"
            elif line.line_type == 'dld_fee':
                line_name += "DLD Fee"
            elif line.line_type == 'admin_fee':
                line_name += "Admin Fee"
            elif line.line_type == 'emi':
                line_name += f"Installment #{line.serial_number}"
            
            invoice_line_vals.append((0, 0, {
                'name': line_name,
                'quantity': 1,
                'price_unit': line.capital_repayment,
                'account_id': self.property_id.revenue_account_id.id,
            }))
        
        # Create the invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': invoice_line_vals,
            'property_order_id': self.id,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        
        # Link the invoice to the sale lines
        for line in lines:
            line.write({
                'invoice_id': invoice.id
            })
        
        # Update sale state if not already invoiced
        if self.state == 'confirm':
            self.state = 'invoiced'
        
        return invoice


class PropertySaleLine(models.Model):
    _name = 'property.sale.line'
    _description = 'Installment Line'
    _order = 'collection_date, serial_number'

    property_sale_id = fields.Many2one('property.sale', string='Property Sale', ondelete='cascade')
    serial_number = fields.Integer(string='Installment Number')
    capital_repayment = fields.Monetary(string='Capital Repayment', digits=(16, 2))
    remaining_capital = fields.Monetary(string='Remaining Capital', digits=(16, 2))
    collection_date = fields.Date(string='Collection Date')
    collection_status = fields.Selection(
        [('unpaid', 'Unpaid'), ('paid', 'Paid')],
        string='Collection Status',
        default='unpaid',
        tracking=True
    )
    line_type = fields.Selection([
        ('downpayment', 'Down Payment'),
        ('dld_fee', 'DLD Fee'),
        ('admin_fee', 'Admin Fee'),
        ('emi', 'EMI')
    ], string='Line Type', required=True, default='emi')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    payment_date = fields.Date(string='Payment Date')
    payment_id = fields.Many2one('account.payment', string='Payment')
    currency_id = fields.Many2one(related='property_sale_id.currency_id', store=True, readonly=True)
    
    def name_get(self):
        """Override name_get to show more descriptive names"""
        result = []
        for line in self:
            name = f"{line.property_sale_id.name} - "
            if line.line_type == 'downpayment':
                name += "Down Payment"
            elif line.line_type == 'dld_fee':
                name += "DLD Fee"
            elif line.line_type == 'admin_fee':
                name += "Admin Fee"
            elif line.line_type == 'emi':
                name += f"Installment #{line.serial_number}"
            
            result.append((line.id, name))
        return result
