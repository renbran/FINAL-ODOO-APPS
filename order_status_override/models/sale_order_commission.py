# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrderCommission(models.Model):
    """Extension of sale.order to add commission report visibility logic"""
    _inherit = 'sale.order'
    
    # Computed field to check if any commission data exists
    has_commission_data = fields.Boolean(
        string='Has Commission Data',
        compute='_compute_has_commission_data',
        store=False,
        help="True if any commission partner or amount is set"
    )
    
    # Commission button visibility
    show_commission_report_button = fields.Boolean(
        string='Show Commission Report Button',
        compute='_compute_show_commission_report_button',
        help="Determines if commission report button should be visible"
    )
    
    @api.depends(
        'broker_partner_id', 'broker_amount', 'broker_rate',
        'referrer_partner_id', 'referrer_amount', 'referrer_rate',
        'cashback_partner_id', 'cashback_amount', 'cashback_rate',
        'agent1_partner_id', 'agent1_amount', 'agent1_rate',
        'agent2_partner_id', 'agent2_amount', 'agent2_rate',
        'manager_partner_id', 'manager_amount', 'manager_rate',
        'director_partner_id', 'director_amount', 'director_rate',
        'other_external_partner_id', 'other_external_amount', 'other_external_rate'
    )
    def _compute_has_commission_data(self):
        """Check if order has any commission data configured"""
        for order in self:
            has_data = False
            
            # Check external commissions
            if order.broker_partner_id or (order.broker_amount or 0) > 0:
                has_data = True
            elif order.referrer_partner_id or (order.referrer_amount or 0) > 0:
                has_data = True
            elif order.cashback_partner_id or (order.cashback_amount or 0) > 0:
                has_data = True
            elif hasattr(order, 'other_external_partner_id') and (
                order.other_external_partner_id or (getattr(order, 'other_external_amount', 0) or 0) > 0
            ):
                has_data = True
            
            # Check internal commissions
            elif order.agent1_partner_id or (order.agent1_amount or 0) > 0:
                has_data = True
            elif order.agent2_partner_id or (order.agent2_amount or 0) > 0:
                has_data = True
            elif order.manager_partner_id or (order.manager_amount or 0) > 0:
                has_data = True
            elif order.director_partner_id or (order.director_amount or 0) > 0:
                has_data = True
            
            order.has_commission_data = has_data
    
    @api.depends('has_commission_data', 'state')
    def _compute_show_commission_report_button(self):
        """Show commission report button only when commission data exists and order is confirmed"""
        for order in self:
            # Button visible if:
            # 1. Has commission data
            # 2. Order is in sale state or beyond
            order.show_commission_report_button = (
                order.has_commission_data and
                order.state in ['sale', 'done']
            )
