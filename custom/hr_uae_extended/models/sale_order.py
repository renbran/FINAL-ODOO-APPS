# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('agent1', 'agent2', 'source_id', 'origin', 'sale_type')
    def _onchange_agent_commission(self):
        for order in self:
            # Reset commissions
            order.commission_agent1 = 0.0
            order.commission_agent2 = 0.0
            order.commission_sales_manager = 0.0

            # Determine if it's a personal lead
            is_personal_lead = False
            if order.source_id:  # Check source_id first
                is_personal_lead = order.source_id.name.lower().find('personal') >= 0
            elif order.origin:  # If no source_id, check origin field
                is_personal_lead = order.origin.lower().find('personal') >= 0

            # Check if it's an exclusive sale
            is_exclusive = order.sale_type and order.sale_type.name.lower().find('exclusive') >= 0

            if is_exclusive and order.agent2:  # Exclusive sale with exclusive agent
                # Base commission rate depends on lead type
                total_commission = 45.0 if is_personal_lead else 55.0
                
                # Distribution for exclusive sales:
                order.commission_agent2 = 5.0  # RM gets 5%
                order.commission_sales_manager = 2.0  # SM gets 2%
                order.commission_agent1 = total_commission - 7.0  # Primary agent gets remaining
                
            else:  # Non-exclusive sale or no exclusive agent
                # Only primary agent gets commission
                if order.agent1:
                    order.commission_agent1 = 45.0 if is_personal_lead else 55.0

    def action_confirm(self):
        # Before confirming the sale order, validate the commissions
        for order in self:
            # Ensure primary agent (agent1) is set
            if not order.agent1:
                raise models.ValidationError(_('Primary Agent (Agent 1) must be set before confirming the order.'))
                
            # If agent2 is set, ensure it's different from agent1
            if order.agent2 and order.agent2 == order.agent1:
                raise models.ValidationError(_('Primary Agent and Exclusive Agent must be different.'))

        return super(SaleOrder, self).action_confirm()
