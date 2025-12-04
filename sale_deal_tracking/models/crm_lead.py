# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    deal_stage = fields.Selection([
        ('new', 'New'),
        ('attempt', 'Attempt'),
        ('contacted', 'Contacted'),
        ('option_sent', 'Option Sent'),
        ('hot', 'Hot'),
        ('idle', 'Idle'),
        ('junk', 'Junk'),
        ('unsuccessful', 'Unsuccessful'),
        ('won', 'Customer (Won)'),
    ], string='Deal Stage', tracking=True, help="Current stage of the deal")

    deal_stage_updated = fields.Datetime(
        string='Deal Stage Updated',
        readonly=True,
        help="Timestamp of last deal stage update"
    )

    sale_order_count = fields.Integer(
        string='Sale Orders',
        compute='_compute_sale_order_count',
        help="Number of sale orders linked to this opportunity"
    )

    def _compute_sale_order_count(self):
        """Compute number of sale orders linked to this opportunity"""
        for lead in self:
            # Use search instead of order_ids to avoid dependency on sale_crm module
            sale_orders = self.env['sale.order'].search([
                ('opportunity_id', '=', lead.id)
            ])
            lead.sale_order_count = len(sale_orders)

    @api.onchange('deal_stage')
    def _onchange_deal_stage(self):
        """Update timestamp when deal stage changes"""
        if self.deal_stage:
            self.deal_stage_updated = fields.Datetime.now()

    def write(self, vals):
        """Sync deal stage to related sale orders if configured"""
        if 'deal_stage' in vals:
            vals['deal_stage_updated'] = fields.Datetime.now()

            # Sync to related sale orders
            if self.env.context.get('sync_deal_stage_to_sale', True):
                for lead in self:
                    sale_orders = self.env['sale.order'].search([
                        ('opportunity_id', '=', lead.id)
                    ])
                    if sale_orders:
                        sale_orders.with_context(sync_deal_stage_to_crm=False).write({
                            'deal_stage': vals['deal_stage']
                        })

        return super(CrmLead, self).write(vals)
