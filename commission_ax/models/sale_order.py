from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add all missing commission total fields
    director_total = fields.Monetary(
        string="Director Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    manager_total = fields.Monetary(
        string="Manager Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    agent1_total = fields.Monetary(
        string="Agent 1 Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    agent2_total = fields.Monetary(
        string="Agent 2 Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    broker_agency_total = fields.Monetary(
        string="Broker/Agency Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    referral_total = fields.Monetary(
        string="Referral Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    cashback_total = fields.Monetary(
        string="Cashback Total", 
        compute='_compute_commission_totals', 
        store=True
    )
    other_total = fields.Monetary(
        string="Other Total", 
        compute='_compute_commission_totals', 
        store=True
    )

    # Add the missing purchase_order_count field
    purchase_order_count = fields.Integer(
        string='Purchase Count',
        compute='_compute_purchase_order_count',
        store=False,
        help="Count of purchase orders linked to this sale order"
    )

    def _compute_purchase_order_count(self):
        """Compute the number of purchase orders linked to this sale order"""
        for order in self:
            order.purchase_order_count = self.env['purchase.order'].search_count([
                ('origin', '=', order.name)
            ])

    @api.depends('amount_total', 'broker_agency_rate', 'referral_rate', 'cashback_rate', 'other_rate',
                 'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate',
                 'broker_agency_commission_type', 'referral_commission_type', 'cashback_commission_type', 'other_commission_type',
                 'agent1_commission_type', 'agent2_commission_type', 'manager_commission_type', 'director_commission_type')
    def _compute_commission_totals(self):
        for order in self:
            # Compute totals for each commission type
            order.broker_agency_total = order._compute_commission(order.broker_agency_commission_type, order.broker_agency_rate)
            order.referral_total = order._compute_commission(order.referral_commission_type, order.referral_rate)
            order.cashback_total = order._compute_commission(order.cashback_commission_type, order.cashback_rate)
            order.other_total = order._compute_commission(order.other_commission_type, order.other_rate)
            order.agent1_total = order._compute_commission(order.agent1_commission_type, order.agent1_rate)
            order.agent2_total = order._compute_commission(order.agent2_commission_type, order.agent2_rate)
            order.manager_total = order._compute_commission(order.manager_commission_type, order.manager_rate)
            order.director_total = order._compute_commission(order.director_commission_type, order.director_rate)

    def _compute_commission(self, commission_type, rate):
        self.ensure_one()
        if not rate:
            return 0.0
            
        if commission_type == 'sale_value':
            return (self.amount_total * rate) / 100
        elif commission_type == 'gross_commission':
            # Using amount_total as the gross commission base
            return (self.amount_total * rate) / 100
        elif commission_type == 'fixed':
            return rate
        return 0.0