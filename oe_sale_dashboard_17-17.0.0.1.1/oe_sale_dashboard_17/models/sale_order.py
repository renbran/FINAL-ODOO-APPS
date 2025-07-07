# -*- coding: utf-8 -*-
# This module is under copyright of 'OdooElevate'

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_date = fields.Datetime(
        string='Booking Date',
        help='Date when the sale order was booked',
        default=fields.Datetime.now,
        required=True,
        index=True
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        help='Alternative amount field for sales reporting',
        compute='_compute_sale_value',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('amount_total')
    def _compute_sale_value(self):
        """
        Compute sale_value based on amount_total.
        This can be customized based on business logic.
        For now, we'll make it equal to amount_total.
        """
        for order in self:
            order.sale_value = order.amount_total

    @api.model
    def create(self, vals):
        """
        Override create to set booking_date if not provided
        """
        if 'booking_date' not in vals:
            vals['booking_date'] = fields.Datetime.now()
        return super(SaleOrder, self).create(vals)

    @api.model
    def _init_booking_date_for_existing_orders(self):
        """
        Initialize booking_date for existing sale orders that don't have it set.
        This method is called during module installation/upgrade.
        """
        orders_without_booking_date = self.search([('booking_date', '=', False)])
        for order in orders_without_booking_date:
            # Set booking_date to date_order if available, otherwise to current time
            booking_date = order.date_order if order.date_order else fields.Datetime.now()
            order.write({'booking_date': booking_date})
