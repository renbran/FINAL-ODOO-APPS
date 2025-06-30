from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # External Commission fields
    broker_partner_id = fields.Many2one('res.partner', string="Broker")
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Broker Commission Type", default='percent_unit_price')
    broker_rate = fields.Float(string="Broker Commission Rate", default=0.0)
    broker_amount = fields.Monetary(string="Broker Commission Amount", compute="_compute_external_commissions", store=True)

    referrer_partner_id = fields.Many2one('res.partner', string="Referrer")
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Referrer Commission Type", default='percent_unit_price')
    referrer_rate = fields.Float(string="Referrer Commission Rate", default=0.0)
    referrer_amount = fields.Monetary(string="Referrer Commission Amount", compute="_compute_external_commissions", store=True)

    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Recipient")
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Cashback Type", default='percent_unit_price')
    cashback_rate = fields.Float(string="Cashback Rate", default=0.0)
    cashback_amount = fields.Monetary(string="Cashback Amount", compute="_compute_external_commissions", store=True)

    other_external_partner_id = fields.Many2one('res.partner', string="Other External Party")
    other_external_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Other External Commission Type", default='percent_unit_price')
    other_external_rate = fields.Float(string="Other External Commission Rate", default=0.0)
    other_external_amount = fields.Monetary(string="Other External Commission Amount", compute="_compute_external_commissions", store=True)

    total_external_commission_amount = fields.Monetary(string="Total External Commission", compute="_compute_external_commissions", store=True)

    @api.depends('order_line.price_unit', 'order_line.price_subtotal', 'amount_untaxed',
                 'broker_rate', 'broker_commission_type',
                 'referrer_rate', 'referrer_commission_type',
                 'cashback_rate', 'cashback_commission_type',
                 'other_external_rate', 'other_external_commission_type')
    def _compute_external_commissions(self):
        for order in self:
            order.broker_amount = order._calc_commission(order.broker_commission_type, order.broker_rate, order)
            order.referrer_amount = order._calc_commission(order.referrer_commission_type, order.referrer_rate, order)
            order.cashback_amount = order._calc_commission(order.cashback_commission_type, order.cashback_rate, order)
            order.other_external_amount = order._calc_commission(order.other_external_commission_type, order.other_external_rate, order)
            order.total_external_commission_amount = (
                order.broker_amount + order.referrer_amount + order.cashback_amount + order.other_external_amount
            )

    @api.constrains('order_line')
    def _check_single_order_line(self):
        for order in self:
            if len(order.order_line) > 1:
                raise ValidationError("Only one order line is allowed per sale order for external commission clarity.")

    def _calc_commission(self, comm_type, rate, order):
        if comm_type == 'fixed':
            return rate
        elif comm_type == 'percent_unit_price':
            # With only one order line, this is simplified
            if order.order_line:
                return (rate / 100.0) * order.order_line[0].price_unit
            return 0.0
        elif comm_type == 'percent_untaxed_total':
            return (rate / 100.0) * order.amount_untaxed
        return 0.0
