from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class PropertySale(models.Model):
    _name = 'property.sale'
    _description = 'Property Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sale_date desc'

    # ========== Fields Definition ==========
    name = fields.Char(
        string='Sale Reference', 
        default='New', 
        readonly=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string='Status', 
       default='draft', 
       tracking=True
    )
    
    # Offer Information (now the main link to property)
    offer_id = fields.Many2one(
        'property.sale.offer',
        string='Related Offer',
        required=True,
        ondelete='restrict',
        tracking=True,
        domain="[('state', '=', 'accepted')]"
    )
    
    # Property information via related fields
    property_id = fields.Many2one(
        'property.property',
        string='Property',
        related='offer_id.property_id',
        store=True,
        readonly=True
    )
    
    # Customer Information
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='offer_id.partner_id',
        store=True,
        readonly=True
    )
    
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        related='offer_id.currency_id',
        readonly=True
    )
    
    start_date = fields.Date(
        string='Start Date', 
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    sale_date = fields.Date(
        string='Sale Date', 
        default=fields.Date.today,
        tracking=True
    )
    
    # Seller Information
    seller_id = fields.Many2one(
        'res.partner', 
        string='Broker/Seller',
        domain=[('is_company','=',True)],
        tracking=True
    )
    
    # Payment Plan Configuration
    payment_plan = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Plan',
       default='monthly',
       required=True,
       tracking=True
    )
    
    # Financial Fields
    property_value = fields.Monetary(
        string='Property Value',
        related='offer_id.offer_price',
        readonly=True,
        currency_field='currency_id'
    )
    
    total_selling_price = fields.Monetary(
        string='Total Selling Price', 
        compute='_compute_total_selling_price',
        store=True, 
        currency_field='currency_id'
    )
    
    down_payment_percentage = fields.Float(
        string='Down Payment (%)', 
        default=20.0,
        tracking=True
    )
    
    down_payment = fields.Monetary(
        string='Down Payment', 
        compute='_compute_down_payment',
        store=True, 
        currency_field='currency_id'
    )
    
    dld_fee = fields.Monetary(
        string='DLD Fee', 
        compute='_compute_dld_fee',
        store=True, 
        currency_field='currency_id'
    )
    
    admin_fee = fields.Monetary(
        string='Admin Fee', 
        default=1.0, 
        currency_field='currency_id',
        tracking=True
    )
    
    remaining_balance = fields.Monetary(
        string='Remaining Balance', 
        compute='_compute_remaining_balance',
        store=True, 
        currency_field='currency_id'
    )
    
    no_of_installments = fields.Integer(
        string='No. of Installments', 
        default=1,
        tracking=True
    )
    
    amount_per_installment = fields.Monetary(
        string='Amount Per Installment', 
        compute='_compute_amount_per_installment',
        store=True, 
        currency_field='currency_id'
    )
    
    payment_progress = fields.Float(
        string='Payment Progress %', 
        compute='_compute_payment_progress',
        store=True, 
        group_operator="avg"
    )
    
    # Broker Commission
    broker_commission_percentage = fields.Float(
        string='Broker Commission %', 
        digits=(5,2), 
        default=5.0,
        tracking=True
    )
    
    broker_commission_invoice_ids = fields.One2many(
        'broker.commission.invoice', 
        'property_sale_id',
        string='Broker Commission Invoices'
    )
    
    # Installment Lines
    property_sale_line_ids = fields.One2many(
        'property.sale.line', 
        'property_sale_id',
        string='Installment Lines'
    )

    # ========== Constraints ==========
    _sql_constraints = [
        ('positive_installments', 'CHECK(no_of_installments > 0)', 'Number of installments must be positive.'),
        ('valid_down_payment', 'CHECK(down_payment_percentage > 0 AND down_payment_percentage <= 100)', 
         'Down payment must be between 0-100%.'),
    ]

    # ========== Compute Methods ==========
    @api.depends('property_value', 'dld_fee', 'admin_fee')
    def _compute_total_selling_price(self):
        for record in self:
            record.total_selling_price = record.property_value + record.dld_fee + record.admin_fee

    @api.depends('property_value', 'down_payment_percentage')
    def _compute_down_payment(self):
        for record in self:
            record.down_payment = (record.down_payment_percentage / 100) * record.property_value

    @api.depends('property_value')
    def _compute_dld_fee(self):
        for record in self:
            record.dld_fee = record.property_value * 0.04  # 4% of property value

    @api.depends('total_selling_price', 'down_payment')
    def _compute_remaining_balance(self):
        for record in self:
            record.remaining_balance = record.total_selling_price - record.down_payment

    @api.depends('remaining_balance', 'no_of_installments')
    def _compute_amount_per_installment(self):
        for record in self:
            if record.no_of_installments > 0:
                record.amount_per_installment = record.remaining_balance / record.no_of_installments
            else:
                record.amount_per_installment = 0.0

    @api.depends('property_sale_line_ids.collection_status')
    def _compute_payment_progress(self):
        for record in self:
            total_lines = record.property_sale_line_ids
            if total_lines:
                total_amount = sum(total_lines.mapped('capital_repayment'))
                paid_amount = sum(total_lines.filtered(
                    lambda l: l.collection_status == 'paid'
                ).mapped('capital_repayment'))
                record.payment_progress = (paid_amount / total_amount) * 100 if total_amount else 0
            else:
                record.payment_progress = 0.0

    # ========== Action Methods ==========
    def action_confirm(self):
        """Confirm the property sale and create installment lines"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft sales can be confirmed.'))
            
            # Create installment lines based on payment plan
            record._create_emi_lines()
            
            # Update property status through the offer
            record.offer_id.write({
                'state': 'accepted',
                'property_sale_id': record.id
            })
            
            record.property_id.write({
                'state': 'sold',
                'partner_id': record.partner_id.id
            })
            
            record.state = 'confirm'
        return True

    def action_cancel(self):
        """Cancel the property sale"""
        for record in self:
            if record.state == 'cancelled':
                raise UserError(_('This sale is already cancelled.'))
            
            # Check for active invoices
            active_invoices = self.env['account.move'].search([
                ('property_order_id', '=', record.id),
                ('state', 'not in', ['cancel', 'draft'])
            ])
            if active_invoices:
                raise UserError(_(
                    'Cannot cancel sale with active invoices. Please cancel invoices first: %s'
                ) % ', '.join(active_invoices.mapped('name')))
            
            # Reset property status if this was the active sale
            if record.property_id.active_sale_id.id == record.id:
                record.property_id.write({
                    'state': 'available',
                    'partner_id': False
                })
            
            # Reset installment lines
            record.property_sale_line_ids.write({
                'collection_status': 'unpaid',
                'invoice_id': False
            })
            
            # Reset offer state
            record.offer_id.write({'state': 'rejected'})
            
            record.state = 'cancelled'
        return True

    # ========== Payment Plan Methods ==========
    def _create_emi_lines(self):
        """Create installment lines based on selected payment plan"""
        self.ensure_one()
        if not self.start_date:
            raise UserError(_('Start date is required to create payment schedule.'))
        
        # Clear existing lines
        self.property_sale_line_ids.unlink()

        # Create downpayment line
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': 0,
            'capital_repayment': self.down_payment,
            'remaining_capital': self.down_payment,
            'collection_date': self.start_date,
            'line_type': 'downpayment'
        })

        # Create DLD fee line
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': 0,
            'capital_repayment': self.dld_fee,
            'remaining_capital': self.dld_fee,
            'collection_date': self.start_date,
            'line_type': 'dld_fee'
        })

        # Create admin fee line
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': 0,
            'capital_repayment': self.admin_fee,
            'remaining_capital': self.admin_fee,
            'collection_date': self.start_date,
            'line_type': 'admin_fee'
        })

        # Create EMI lines based on payment plan
        for i in range(1, self.no_of_installments + 1):
            due_date = self._calculate_due_date(self.start_date, i)
            self.env['property.sale.line'].create({
                'property_sale_id': self.id,
                'serial_number': i,
                'capital_repayment': self.amount_per_installment,
                'remaining_capital': self.amount_per_installment,
                'collection_date': due_date,
                'line_type': 'emi'
            })

    def _calculate_due_date(self, start_date, installment_number):
        """Calculate due date based on payment plan"""
        try:
            if self.payment_plan == 'monthly':
                delta = relativedelta(months=installment_number)
            elif self.payment_plan == 'quarterly':
                delta = relativedelta(months=installment_number*3)
            elif self.payment_plan == 'semi_annual':
                delta = relativedelta(months=installment_number*6)
            elif self.payment_plan == 'annual':
                delta = relativedelta(years=installment_number)
            else:
                delta = relativedelta(months=installment_number)  # Default to monthly
            
            due_date = start_date + delta
            
            # Handle end-of-month dates
            if start_date.day > 28 and due_date.month != (start_date + delta).month:
                due_date = (start_date + delta).replace(day=1) - relativedelta(days=1)
            
            return due_date
        except Exception as e:
            raise UserError(_('Error calculating due date: %s') % str(e))

    # ========== Overrides ==========
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('property.sale') or 'New'
        return super().create(vals)

    def write(self, vals):
        """Handle state changes and property updates"""
        res = super().write(vals)
        
        if 'state' in vals:
            for record in self:
                if vals['state'] == 'confirm':
                    if not record.property_sale_line_ids:
                        record._create_emi_lines()
                elif vals['state'] == 'cancelled':
                    # Reset property status if this was the active sale
                    if record.property_id.active_sale_id.id == record.id:
                        record.property_id.write({
                            'state': 'available',
                            'partner_id': False
                        })
        return res


class PropertySaleLine(models.Model):
    _name = 'property.sale.line'
    _description = 'Property Sale Installment Line'
    _order = 'collection_date, serial_number'

    property_sale_id = fields.Many2one(
        'property.sale', 
        string='Property Sale', 
        required=True, 
        ondelete='cascade'
    )
    
    serial_number = fields.Integer(string='Installment #')
    
    line_type = fields.Selection([
        ('downpayment', 'Down Payment'),
        ('dld_fee', 'DLD Fee'),
        ('admin_fee', 'Admin Fee'),
        ('emi', 'EMI')
    ], string='Type', required=True)
    
    capital_repayment = fields.Monetary(
        string='Amount', 
        currency_field='currency_id'
    )
    
    remaining_capital = fields.Monetary(
        string='Remaining', 
        currency_field='currency_id'
    )
    
    collection_date = fields.Date(
        string='Due Date', 
        required=True
    )
    
    collection_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Status', 
       default='unpaid'
    )
    
    invoice_id = fields.Many2one(
        'account.move', 
        string='Invoice'
    )
    
    currency_id = fields.Many2one(
        related='property_sale_id.currency_id', 
        store=True
    )

    def write(self, vals):
        """Update payment progress when status changes"""
        res = super().write(vals)
        if 'collection_status' in vals:
            for line in self:
                line.property_sale_id._compute_payment_progress()
                if line.property_sale_id.property_id:
                    line.property_sale_id.property_id._compute_payment_progress()
        return res