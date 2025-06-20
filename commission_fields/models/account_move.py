# -*- coding: utf-8 -*-
from odoo import models, fields, api  # Ensure Odoo is installed and run this code inside the Odoo server environment

class AccountMove(models.Model):
    _inherit = 'account.move'

    deal_id = fields.Char(
        string='Deal ID',
        copy=False,
        help="Related Sale Order Deal ID",
        index=True
    )
    
    booking_date = fields.Date(
        string='Booking Date',
        copy=False,
        help="Related Sale Order Booking Date"
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        copy=False,
        help="Related Sale Order Buyer"
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project',
        copy=False,
        help="Related Sale Order Project",
        ondelete='set null',  # Valid Odoo field argument, no change needed if running inside Odoo
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
        currency_field='currency_id',
        help="Related Sale Order Sale Value"
    )
    
    broker_commission = fields.Monetary(
        string='Broker Commission',
        readonly=True,
        copy=False,
        currency_field='currency_id',
        help="Broker commission from related Sale Order"
    )

    @api.depends('deal_id')
    def _compute_deal_id_display(self):
        """Display deal_id as string, removing trailing zeros if integer."""
        for rec in self:
            if rec.deal_id is not None:
                if float(rec.deal_id).is_integer():
                    rec.deal_id_display = str(int(rec.deal_id))
                else:
                    rec.deal_id_display = str(rec.deal_id).rstrip('0').rstrip('.')
            else:
                rec.deal_id_display = ''

    @api.model_create_multi
    def create(self, vals_list):
        """Set commission and related fields from sale order on invoice creation."""
        for vals in vals_list:
            if vals.get('invoice_origin'):
                sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
                if sale_order:
                    vals['deal_id'] = sale_order.deal_id
                    vals['booking_date'] = sale_order.booking_date
                    vals['buyer_id'] = sale_order.buyer_id.id
                    vals['project_id'] = sale_order.project_id.id
                    vals['unit_id'] = sale_order.unit_id.id
                    vals['sale_value'] = sale_order.sale_value
                    # Use broker_agency_total for broker_commission (Odoo 17 best practice)
                    vals['broker_commission'] = sale_order.broker_agency_total
        return super().create(vals_list)

    def write(self, vals):
        """Update commission and related fields from sale order if invoice_origin changes."""
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
                        'broker_commission': sale_order.broker_agency_total,
                    })
        return super().write(vals)
