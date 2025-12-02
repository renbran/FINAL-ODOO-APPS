# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PropertySold(models.TransientModel):
    _name = 'property.vendor.wizard'
    _description = 'Wizard For Selecting Customer to sale'

    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    property_id = fields.Many2one('property.details', string='Property')
    customer_id = fields.Many2one('property.vendor', string='Customer')
    final_price = fields.Monetary(string='Final Price')
    sold_invoice_id = fields.Many2one('account.move')
    broker_id = fields.Many2one(related='customer_id.broker_id')
    is_any_broker = fields.Boolean(related='customer_id.is_any_broker')
    quarter = fields.Integer(string="Quarter", default=4)
    
    # Installment Count for bi-annual and annual
    bi_annual_count = fields.Integer(string="Bi-Annual Installments", default=2)
    annual_count = fields.Integer(string="Annual Installments", default=1)

    # Payment Schedule Integration
    use_payment_schedule = fields.Boolean(string="Use Payment Schedule", default=False,
                                          help="Use payment schedule template instead of manual configuration")
    payment_schedule_id = fields.Many2one('payment.schedule', string='Payment Schedule',
                                         domain="[('schedule_type', '=', 'sale'), ('active', '=', True)]",
                                         help='Payment schedule template inherited from property')
    schedule_from_property = fields.Boolean(string='Inherited from Property', default=False)

    # Payment Term (Manual Configuration - hidden when using schedule)
    duration_id = fields.Many2one(
        'contract.duration', string='Duration', domain="[('rent_unit','=','Month')]")
    payment_term = fields.Selection([
        ('monthly', 'Monthly'),
        ('full_payment', 'Full Payment'),
        ('quarterly', 'Quarterly'),
        ('bi_annual', 'Bi-Annual (6 Months)'),
        ('annual', 'Annual')
    ], string='Payment Term', help='Frequency of installment payments')
    start_date = fields.Date(string="Start From", required=True)
    
    # DLD and Admin Fee Settings
    include_dld_fee = fields.Boolean(string="Include DLD Fee", default=True)
    include_admin_fee = fields.Boolean(string="Include Admin Fee", default=True)
    dld_fee_amount = fields.Monetary(string="DLD Fee Amount")
    admin_fee_amount = fields.Monetary(string="Admin Fee Amount")
    dld_due_days = fields.Integer(string="DLD Due Days", default=30)
    admin_due_days = fields.Integer(string="Admin Due Days", default=30)

    # Installment Item
    installment_item_id = fields.Many2one('product.product', string="Installment Item",
                                          default=lambda self: self.env.ref('rental_management.property_product_1',
                                                                            raise_if_not_found=False))
    is_taxes = fields.Boolean(string="Taxes ?")
    taxes_ids = fields.Many2many('account.tax', string="Taxes")

    @api.model
    def default_get(self, fields_list):
        res = super(PropertySold, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        sell_id = self.env['property.vendor'].browse(active_id)
        res['customer_id'] = sell_id.id
        res['final_price'] = sell_id.ask_price
        res['is_taxes'] = sell_id.is_taxes
        res['taxes_ids'] = [(6, 0, sell_id.taxes_ids.ids)]
        res['property_id'] = sell_id.property_id.id
        res['installment_item_id'] = sell_id.installment_item_id.id
        # Get DLD and Admin fee settings from contract
        res['include_dld_fee'] = sell_id.include_dld_in_plan
        res['include_admin_fee'] = sell_id.include_admin_in_plan
        res['dld_fee_amount'] = sell_id.dld_fee
        res['admin_fee_amount'] = sell_id.admin_fee
        res['dld_due_days'] = sell_id.dld_fee_due_days
        res['admin_due_days'] = sell_id.admin_fee_due_days
        
        # Load payment schedule from contract if available
        if sell_id.payment_schedule_id:
            res['use_payment_schedule'] = True
            res['payment_schedule_id'] = sell_id.payment_schedule_id.id
            res['schedule_from_property'] = sell_id.schedule_from_property
        else:
            res['use_payment_schedule'] = False
            res['payment_term'] = sell_id.payment_term or 'monthly'
        
        # Set default start date to contract date
        res['start_date'] = sell_id.date or fields.Date.today()
        
        return res

    @api.onchange('payment_term')
    def _onchange_payment_term(self):
        if self.payment_term == 'quarterly':
            return {'domain': {'duration_id': [('month', '>=', 3)]}}
        elif self.payment_term == 'bi_annual':
            return {'domain': {'duration_id': [('month', '>=', 6)]}}
        elif self.payment_term == 'annual':
            return {'domain': {'duration_id': [('month', '>=', 12)]}}

    def property_sale_action(self):
        # VALIDATION: Check booking requirements before creating installments
        if not self.customer_id.can_create_installments:
            if self.customer_id.stage == 'draft':
                raise ValidationError(_(
                    "⚠️ BOOKING REQUIREMENTS NOT MET\n\n"
                    "Before creating installments, the client must first pay all booking requirements:\n\n"
                    "📋 Required Payments:\n"
                    "   • Booking Fee: %s AED %s\n"
                    "   • DLD Fee: %s AED %s\n"
                    "   • Admin Fee: %s AED %s\n\n"
                    "💡 Next Steps:\n"
                    "   1. Go to contract form\n"
                    "   2. Click 'Generate Booking Invoices' button\n"
                    "   3. Send invoices to client for payment\n"
                    "   4. Mark invoices as 'Paid' once received\n"
                    "   5. Click 'Confirm Booking Paid' button\n"
                    "   6. Then return here to create installments\n\n"
                    "Payment Progress: %.0f%%"
                ) % (
                    f"{abs(self.customer_id.book_price):,.2f}",
                    "✅ PAID" if self.customer_id.booking_invoice_paid else "❌ UNPAID",
                    f"{self.customer_id.dld_fee:,.2f}",
                    "✅ PAID" if self.customer_id.dld_invoice_paid else "❌ UNPAID",
                    f"{self.customer_id.admin_fee:,.2f}",
                    "✅ PAID" if self.customer_id.admin_invoice_paid else "❌ UNPAID",
                    self.customer_id.booking_payment_progress
                ))
            else:
                raise ValidationError(_(
                    "Cannot create installments for this contract.\n\n"
                    "Current Stage: %s\n"
                    "Required Stage: Booked (with all booking requirements paid)"
                ) % dict(self.customer_id._fields['stage'].selection).get(self.customer_id.stage))
        
        # If using payment schedule, delegate to schedule-based generation
        if self.use_payment_schedule and self.payment_schedule_id:
            return self._generate_from_payment_schedule()
        
        # Otherwise, use manual configuration (legacy behavior)
        if self.payment_term == 'quarterly' and self.quarter <= 1:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': _('Quarter'),
                    'message': _("Quarter should be greater than 1."),
                    'sticky': False,
                }
            }
        
        if self.payment_term == 'bi_annual' and self.bi_annual_count <= 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': _('Bi-Annual'),
                    'message': _("Bi-Annual installments should be at least 1."),
                    'sticky': False,
                }
            }
        
        if self.payment_term == 'annual' and self.annual_count <= 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': _('Annual'),
                    'message': _("Annual installments should be at least 1."),
                    'sticky': False,
                }
            }
        
        # Validate start_date is required for installment-based payments
        if self.payment_term != 'full_payment' and not self.start_date:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': _('Start Date Required'),
                    'message': _("Please specify a start date for installment payments."),
                    'sticky': False,
                }
            }

        self.customer_id.write({
            'installment_item_id': self.installment_item_id.id,
            'is_taxes': self.is_taxes,
            'taxes_ids': self.taxes_ids.ids,
            'sale_price': self.final_price,
            'payment_term': self.payment_term,
            'include_dld_in_plan': self.include_dld_fee,
            'include_admin_in_plan': self.include_admin_fee,
        })
        count = 0
        sequence = 1
        booking_date = self.start_date or fields.Date.today()
        
        if self.customer_id.is_any_broker:
            broker_name = 'Commission of %s' % self.customer_id.property_id.name
            broker_bill_id = self.env['account.move'].sudo().create({
                'partner_id': self.customer_id.broker_id.id,
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.customer_id.broker_item_id.id,
                        'name': broker_name,
                        'quantity': 1,
                        'price_unit': self.customer_id.broker_final_commission
                    })]
            })
            self.customer_id.broker_bill_id = broker_bill_id.id
            partner_invoice_id = self.env['account.move'].sudo().create({
                'partner_id': self.customer_id.customer_id.id if self.customer_id.commission_from == 'customer' else self.customer_id.landlord_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.customer_id.broker_item_id.id,
                        'name': broker_name,
                        'quantity': 1,
                        'price_unit': self.customer_id.broker_final_commission
                    })]
            })
            self.customer_id.broker_invoice_id = partner_invoice_id.id
        
        # Create DLD Fee Invoice (Due X days after booking)
        if self.include_dld_fee and self.dld_fee_amount > 0:
            dld_due_date = booking_date + relativedelta(days=self.dld_due_days)
            self.env['sale.invoice'].create({
                'name': _('DLD Fee - Dubai Land Department'),
                'property_sold_id': self.customer_id.id,
                'invoice_date': dld_due_date,
                'amount': self.dld_fee_amount,
                'invoice_type': 'dld_fee',
                'sequence': sequence,
                'desc': _('DLD Fee - Due %s days after booking') % self.dld_due_days,
            })
            sequence += 1
        
        # Create Admin Fee Invoice (Due X days after booking)
        if self.include_admin_fee and self.admin_fee_amount > 0:
            admin_due_date = booking_date + relativedelta(days=self.admin_due_days)
            self.env['sale.invoice'].create({
                'name': _('Admin Fee - Administrative Processing'),
                'property_sold_id': self.customer_id.id,
                'invoice_date': admin_due_date,
                'amount': self.admin_fee_amount,
                'invoice_type': 'admin_fee',
                'sequence': sequence,
                'desc': _('Admin Fee - Due %s days after booking') % self.admin_due_days,
            })
            sequence += 1
        
        for rec in self:
            if rec.payment_term == "monthly":
                if not rec.duration_id:
                    raise ValidationError(_("Please select a duration for monthly payments."))
                amount = round(rec.customer_id.payable_amount / rec.duration_id.month, 2)
                invoice_date = rec.start_date
                for r in range(rec.duration_id.month):
                    count = count + 1
                    sold_invoice_data = {
                        'name': _("Installment : %s") % str(count),
                        'property_sold_id': rec.customer_id.id,
                        'invoice_date': invoice_date,
                        'amount': amount,
                        'invoice_type': 'installment',
                        'sequence': sequence,
                        'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes and self.taxes_ids else False
                    }
                    self.env['sale.invoice'].create(sold_invoice_data)
                    invoice_date = invoice_date + relativedelta(months=1)
                    sequence += 1
            elif rec.payment_term == "quarterly":
                if rec.quarter > 1:
                    amount = round(rec.customer_id.payable_amount / rec.quarter, 2)
                    invoice_date = rec.start_date
                    for r in range(rec.quarter):
                        count = count + 1
                        sold_invoice_data = {
                            'name': _("Quarter Payment : %s") % str(count),
                            'property_sold_id': rec.customer_id.id,
                            'invoice_date': invoice_date,
                            'amount': amount,
                            'invoice_type': 'installment',
                            'sequence': sequence,
                            'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes and self.taxes_ids else False
                        }
                        self.env['sale.invoice'].create(sold_invoice_data)
                        invoice_date = invoice_date + relativedelta(months=3)
                        sequence += 1
            elif rec.payment_term == "bi_annual":
                if rec.bi_annual_count >= 1:
                    amount = round(rec.customer_id.payable_amount / rec.bi_annual_count, 2)
                    invoice_date = rec.start_date
                    for r in range(rec.bi_annual_count):
                        count = count + 1
                        sold_invoice_data = {
                            'name': _("Bi-Annual Payment : %s") % str(count),
                            'property_sold_id': rec.customer_id.id,
                            'invoice_date': invoice_date,
                            'amount': amount,
                            'invoice_type': 'installment',
                            'sequence': sequence,
                            'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes and self.taxes_ids else False
                        }
                        self.env['sale.invoice'].create(sold_invoice_data)
                        invoice_date = invoice_date + relativedelta(months=6)
                        sequence += 1
            elif rec.payment_term == "annual":
                if rec.annual_count >= 1:
                    amount = round(rec.customer_id.payable_amount / rec.annual_count, 2)
                    invoice_date = rec.start_date
                    for r in range(rec.annual_count):
                        count = count + 1
                        sold_invoice_data = {
                            'name': _("Annual Payment : %s") % str(count),
                            'property_sold_id': rec.customer_id.id,
                            'invoice_date': invoice_date,
                            'amount': amount,
                            'invoice_type': 'installment',
                            'sequence': sequence,
                            'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes and self.taxes_ids else False
                        }
                        self.env['sale.invoice'].create(sold_invoice_data)
                        invoice_date = invoice_date + relativedelta(years=1)
                        sequence += 1
            elif rec.payment_term == "full_payment":
                self.env['sale.invoice'].create({
                    'name': _("Full Payment"),
                    'property_sold_id': self.customer_id.id,
                    'invoice_date': fields.Date.today(),
                    'amount': round(rec.customer_id.payable_amount, 2),
                    'invoice_type': 'installment',
                    'sequence': sequence,
                    'tax_ids': [(6, 0, self.taxes_ids.ids)] if self.is_taxes and self.taxes_ids else False,
                    'is_remain_invoice': True
                })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Success'),
                'message': _('Payment installments created successfully!'),
                'sticky': False,
            }
        }
    
    def _generate_from_payment_schedule(self):
        """Generate invoices from payment schedule template (same logic as contract)"""
        self.ensure_one()
        
        if not self.start_date:
            raise ValidationError(_('Start date is required to generate payment schedule.'))
        
        contract_start_date = self.start_date
        property_base_price = self.customer_id.property_id.price if self.customer_id.property_id else self.customer_id.sale_price
        sequence = 1
        
        # Update contract with settings
        self.customer_id.write({
            'installment_item_id': self.installment_item_id.id,
            'is_taxes': self.is_taxes,
            'taxes_ids': self.taxes_ids.ids,
            'sale_price': self.final_price,
            'include_dld_in_plan': self.include_dld_fee,
            'include_admin_in_plan': self.include_admin_fee,
        })
        
        # Handle broker commission if applicable
        if self.customer_id.is_any_broker:
            broker_name = 'Commission of %s' % self.customer_id.property_id.name
            broker_bill_id = self.env['account.move'].sudo().create({
                'partner_id': self.customer_id.broker_id.id,
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.customer_id.broker_item_id.id,
                        'name': broker_name,
                        'quantity': 1,
                        'price_unit': self.customer_id.broker_final_commission
                    })]
            })
            self.customer_id.broker_bill_id = broker_bill_id.id
            partner_invoice_id = self.env['account.move'].sudo().create({
                'partner_id': self.customer_id.customer_id.id if self.customer_id.commission_from == 'customer' else self.customer_id.landlord_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.customer_id.broker_item_id.id,
                        'name': broker_name,
                        'quantity': 1,
                        'price_unit': self.customer_id.broker_final_commission
                    })]
            })
            self.customer_id.broker_invoice_id = partner_invoice_id.id
        
        # 1. Generate DLD Fee Invoice
        if self.include_dld_fee and self.dld_fee_amount > 0:
            dld_due_date = contract_start_date + relativedelta(days=self.dld_due_days)
            self.env['sale.invoice'].create({
                'property_sold_id': self.customer_id.id,
                'name': _('DLD Fee - Dubai Land Department'),
                'amount': self.dld_fee_amount,
                'invoice_date': dld_due_date,
                'invoice_created': False,
                'invoice_type': 'dld_fee',
                'sequence': sequence,
                'desc': _('DLD Fee - Due %s days after start date (%s%% of sale price)') % (
                    self.dld_due_days,
                    self.customer_id.dld_fee_percentage
                ) if self.customer_id.dld_fee_type == 'percentage' else _('DLD Fee - Due %s days after start date') % self.dld_due_days,
                'tax_ids': False
            })
            sequence += 1
        
        # 2. Generate Admin Fee Invoice
        if self.include_admin_fee and self.admin_fee_amount > 0:
            admin_due_date = contract_start_date + relativedelta(days=self.admin_due_days)
            self.env['sale.invoice'].create({
                'property_sold_id': self.customer_id.id,
                'name': _('Admin Fee - Administrative Processing'),
                'amount': self.admin_fee_amount,
                'invoice_date': admin_due_date,
                'invoice_created': False,
                'invoice_type': 'admin_fee',
                'sequence': sequence,
                'desc': _('Admin Fee - Due %s days after start date') % self.admin_due_days,
                'tax_ids': False
            })
            sequence += 1
        
        # 3. Generate Payment Schedule Installments
        # Calculate remaining amount (property price - booking if already paid)
        booking_amount = abs(self.customer_id.book_price) if self.customer_id.book_price else 0
        remaining_amount = property_base_price - booking_amount
        
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
            
            # Generate invoices based on number of installments
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
                    'property_sold_id': self.customer_id.id,
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
                'message': _('Payment schedule generated successfully with %s invoices based on template: %s') % (
                    sequence - 1, 
                    self.payment_schedule_id.name
                ),
                'sticky': False,
            }
        }