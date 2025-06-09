# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    deal_id = fields.Many2one('sale.order', string='Deal ID', readonly=True, copy=False, help="Related Sale Order Deal ID")
    booking_date = fields.Date(string='Booking Date', readonly=True, copy=False, help="Related Sale Order Booking Date")
    buyer_id = fields.Many2one('res.partner', string='Buyer', readonly=True, copy=False, help="Related Sale Order Buyer")
    project_id = fields.Many2one('your.project.model', string='Project', readonly=True, copy=False, help="Related Sale Order Project")
    unit_id = fields.Many2one('your.unit.model', string='Unit', readonly=True, copy=False, help="Related Sale Order Unit")
    sale_value = fields.Monetary(string='Sale Value', readonly=True, copy=False, help="Related Sale Order Sale Value")

    @api.model
    def create(self, vals):
        if vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                vals['deal_id'] = sale_order.id
                vals['booking_date'] = sale_order.booking_date
                vals['buyer_id'] = sale_order.buyer_id.id
                vals['project_id'] = sale_order.project_id.id
                vals['unit_id'] = sale_order.unit_id.id
                vals['sale_value'] = sale_order.sale_value
        return super().create(vals)

    def write(self, vals):
        for move in self:
            if move.invoice_origin and not any(f in vals for f in ['deal_id', 'booking_date', 'buyer_id', 'project_id', 'unit_id', 'sale_value']):
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    vals.update({
                        'deal_id': sale_order.id,
                        'booking_date': sale_order.booking_date,
                        'buyer_id': sale_order.buyer_id.id,
                        'project_id': sale_order.project_id.id,
                        'unit_id': sale_order.unit_id.id,
                        'sale_value': sale_order.sale_value,
                    })
        return super().write(vals)
