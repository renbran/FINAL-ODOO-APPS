# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_id = fields.Many2one(
        'crm.lead',
        string='Opportunity/Lead',
        tracking=True
    )

    deal_stage = fields.Selection([
        ('new', 'New'),
        ('attempt', 'Attempt'),
        ('contacted', 'Contacted'),
        ('option_sent', 'Option Sent'),
        ('hot', 'Hot'),
        ('idle', 'Idle'),
        ('junk', 'Junk'),
        ('unsuccessful', 'Unsuccessful'),
        ('won', 'Customer'),
    ], string='Deal Stage', tracking=True)

    deal_stage_updated = fields.Datetime(
        string='Deal Stage Updated',
        readonly=True
    )

    def action_print_commission_report(self):
        """Generate and return commission payout report."""
        self.ensure_one()
        
        # Generate report directly using QWeb template
        report = self.env['ir.actions.report']
        
        # Try to find existing report action first
        try:
            report_action = self.env.ref('commission_ax.action_report_commission_payout_professional', raise_if_not_found=False)
            if report_action:
                return report_action.report_action(self)
        except ValueError:
            pass
        
        # Fallback: Generate report directly using the template name
        return report._render_qweb_pdf('commission_ax.commission_payout_report_template_professional', self.ids)[0]
