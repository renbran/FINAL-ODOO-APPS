# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    deal_id = fields.Float(string='Deal ID', copy=False, help="Related Sale Order Deal ID")
    booking_date = fields.Date(string='Booking Date', copy=False, help="Related Sale Order Booking Date")
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False, help="Related Sale Order Buyer")
    project_id = fields.Many2one(
        'product.template',
        string='Project',
        copy=False,
        help="Related Sale Order Project",
        ondelete='set null',
        domain=[],
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        copy=False,
        help="Related Sale Order Unit",
        ondelete='set null',
        domain=[],
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        copy=False,
        help="Related Sale Order Sale Value"
    )
    broker_commission = fields.Float(string='Broker Commission', readonly=True, copy=False, help="Broker commission from related Sale Order")
    deal_id_display = fields.Char(string='Deal ID (Display)', compute='_compute_deal_id_display', store=False)

    @api.depends('deal_id')
    def _compute_deal_id_display(self):
        for rec in self:
            if rec.deal_id is not None:
                # Remove trailing zeros and decimal if not needed
                if float(rec.deal_id).is_integer():
                    rec.deal_id_display = str(int(rec.deal_id))
                else:
                    rec.deal_id_display = str(rec.deal_id).rstrip('0').rstrip('.')
            else:
                rec.deal_id_display = ''

    @api.model
    def create(self, vals):
        if vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                vals['deal_id'] = sale_order.deal_id
                vals['booking_date'] = sale_order.booking_date
                vals['buyer_id'] = sale_order.buyer_id.id
                vals['project_id'] = sale_order.project_id.id
                vals['unit_id'] = sale_order.unit_id.id
                vals['sale_value'] = sale_order.sale_value
                # Use the calculated broker commission
                vals['broker_commission'] = sale_order.broker_agency_total
        return super().create(vals)

    def write(self, vals):
        for move in self:
            if move.invoice_origin and not any(f in vals for f in ['deal_id', 'booking_date', 'buyer_id', 'project_id', 'unit_id', 'sale_value', 'broker_commission']):
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    vals.update({
                        'deal_id': sale_order.deal_id,
                        'booking_date': sale_order.booking_date,
                        'buyer_id': sale_order.buyer_id.id,
                        'project_id': sale_order.project_id.id,
                        'unit_id': sale_order.unit_id.id,
                        'sale_value': sale_order.sale_value,
                        # Use the calculated broker commission
                        'broker_commission': sale_order.broker_agency_total,
                    })
        return super().write(vals)
