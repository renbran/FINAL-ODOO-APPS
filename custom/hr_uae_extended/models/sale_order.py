# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('internal_commission', 'lead_source')
    def _onchange_commission_details(self):
        if self.internal_commission and self.internal_commission.is_agent:
            if self.lead_source == 'personal':
                self.commission_percentage = self.internal_commission.personal_lead_commission
            else:
                self.commission_percentage = self.internal_commission.business_lead_commission

            # Add additional commissions for managers if applicable
            if self.internal_commission.is_sales_manager:
                self.commission_percentage += self.internal_commission.sales_manager_commission
            if self.internal_commission.is_relationship_manager:
                self.commission_percentage += self.internal_commission.relationship_manager_commission
