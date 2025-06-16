# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    deal_id = fields.Many2one('sale.order', string='Deal ID', readonly=False, copy=False, help="Related Sale Order Deal ID")
    booking_date = fields.Date(string='Booking Date', readonly=False, copy=False, help="Related Sale Order Booking Date")
    buyer_id = fields.Many2one('res.partner', string='Buyer', readonly=False, copy=False, help="Related Sale Order Buyer")
    project_id = fields.Many2one(
        'product.template',
        string='Project',
        readonly=False,
        copy=False,
        help="Related Sale Order Project"
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        readonly=False,
        copy=False,
        help="Related Sale Order Unit"
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        readonly=False,
        copy=False,
        help="Related Sale Order Sale Value"
    )
    # Add a Char field for deal_id search convenience
    deal_id_char = fields.Char(string='Deal ID (String)', compute='_compute_deal_id_char', store=True, index=True, help="Deal string for search/filter")

    @api.depends('deal_id')
    def _compute_deal_id_char(self):
        for rec in self:
            rec.deal_id_char = rec.deal_id.deal_id if rec.deal_id and hasattr(rec.deal_id, 'deal_id') else False

    @api.model
    def search_by_deal_id(self, deal_id_str):
        """Search account.move by deal string (deal_id from sale.order)"""
        return self.search([('deal_id_char', '=', deal_id_str)])

    @api.model
    def create(self, vals):
        # Map deal information from sale.order to account.move (customer invoice) if invoice_origin is set
        if vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                # Only map if this is a customer invoice
                move_type = vals.get('move_type') or self._context.get('default_move_type')
                if move_type == 'out_invoice':
                    if sale_order.deal_id and hasattr(sale_order.deal_id, 'id'):
                        vals['deal_id'] = sale_order.deal_id.id
                    vals['booking_date'] = sale_order.booking_date
                    vals['buyer_id'] = sale_order.buyer_id.id
                    vals['project_id'] = sale_order.project_id.id
                    vals['unit_id'] = sale_order.unit_id.id
                    vals['sale_value'] = sale_order.sale_value
        return super().create(vals)

    def write(self, vals):
        for move in self:
            # Only update deal info for customer invoices
            if move.move_type == 'out_invoice' and move.invoice_origin and not any(f in vals for f in ['deal_id', 'booking_date', 'buyer_id', 'project_id', 'unit_id', 'sale_value']):
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    if sale_order.deal_id and hasattr(sale_order.deal_id, 'id'):
                        vals['deal_id'] = sale_order.deal_id.id
                    vals['booking_date'] = sale_order.booking_date
                    vals['buyer_id'] = sale_order.buyer_id.id
                    vals['project_id'] = sale_order.project_id.id
                    vals['unit_id'] = sale_order.unit_id.id
                    vals['sale_value'] = sale_order.sale_value
        return super().write(vals)
