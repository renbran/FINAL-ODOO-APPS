# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime


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

    # Payment Term
    duration_id = fields.Many2one(
        'contract.duration', string='Duration', domain="[('rent_unit','=','Month')]")
    payment_term = fields.Selection([
        ('monthly', 'Monthly'),
        ('full_payment', 'Full Payment'),
        ('quarterly', 'Quarterly'),
        ('bi_annual', 'Bi-Annual (6 Months)'),
        ('annual', 'Annual')
    ], string='Payment Term', help='Frequency of installment payments')
    start_date = fields.Date(string="Start From")
    
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
                amount = rec.customer_id.payable_amount / rec.duration_id.month
                invoice_date = rec.start_date
                for r in range(rec.duration_id.month):
                    count = count + 1
                    sold_invoice_data = {
                        'name': f"Installment : {str(count)}",
                        'property_sold_id': rec.customer_id.id,
                        'invoice_date': invoice_date,
                        'amount': amount,
                        'invoice_type': 'installment',
                        'sequence': sequence,
                        'tax_ids': self.taxes_ids.ids if self.is_taxes else False
                    }
                    self.env['sale.invoice'].create(sold_invoice_data)
                    invoice_date = invoice_date + relativedelta(months=1)
                    sequence += 1
            elif rec.payment_term == "quarterly":
                if rec.quarter > 1:
                    amount = rec.customer_id.payable_amount / rec.quarter
                    invoice_date = rec.start_date
                    for r in range(rec.quarter):
                        count = count + 1
                        sold_invoice_data = {
                            'name': f"Quarter Payment : {str(count)}",
                            'property_sold_id': rec.customer_id.id,
                            'invoice_date': invoice_date,
                            'amount': amount,
                            'invoice_type': 'installment',
                            'sequence': sequence,
                            'tax_ids': self.taxes_ids.ids if self.is_taxes else False
                        }
                        self.env['sale.invoice'].create(sold_invoice_data)
                        invoice_date = invoice_date + relativedelta(months=3)
                        sequence += 1
            elif rec.payment_term == "bi_annual":
                if rec.bi_annual_count >= 1:
                    amount = rec.customer_id.payable_amount / rec.bi_annual_count
                    invoice_date = rec.start_date
                    for r in range(rec.bi_annual_count):
                        count = count + 1
                        sold_invoice_data = {
                            'name': f"Bi-Annual Payment : {str(count)}",
                            'property_sold_id': rec.customer_id.id,
                            'invoice_date': invoice_date,
                            'amount': amount,
                            'invoice_type': 'installment',
                            'sequence': sequence,
                            'tax_ids': self.taxes_ids.ids if self.is_taxes else False
                        }
                        self.env['sale.invoice'].create(sold_invoice_data)
                        invoice_date = invoice_date + relativedelta(months=6)
                        sequence += 1
            elif rec.payment_term == "annual":
                if rec.annual_count >= 1:
                    amount = rec.customer_id.payable_amount / rec.annual_count
                    invoice_date = rec.start_date
                    for r in range(rec.annual_count):
                        count = count + 1
                        sold_invoice_data = {
                            'name': f"Annual Payment : {str(count)}",
                            'property_sold_id': rec.customer_id.id,
                            'invoice_date': invoice_date,
                            'amount': amount,
                            'invoice_type': 'installment',
                            'sequence': sequence,
                            'tax_ids': self.taxes_ids.ids if self.is_taxes else False
                        }
                        self.env['sale.invoice'].create(sold_invoice_data)
                        invoice_date = invoice_date + relativedelta(years=1)
                        sequence += 1
            elif rec.payment_term == "full_payment":
                self.env['sale.invoice'].create({
                    'name': "Full Payment",
                    'property_sold_id': self.customer_id.id,
                    'invoice_date': fields.Date.today(),
                    'amount': rec.customer_id.payable_amount,
                    'invoice_type': 'installment',
                    'sequence': sequence,
                    'tax_ids': self.taxes_ids.ids if self.is_taxes else False,
                    'is_remain_invoice': True
                })