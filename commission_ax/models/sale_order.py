from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # External Commission Fields
    broker_agency_name = fields.Char(string="Broker/Agency Name")
    broker_agency_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Broker/Agency Commission Type")
    broker_agency_rate = fields.Float(string="Broker/Agency Rate (%)")
    broker_agency_total = fields.Monetary(string="Broker/Agency Total", compute='_compute_commission_totals', store=True)

    referral_name = fields.Char(string="Referral Name")
    referral_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Referral Commission Type")
    referral_rate = fields.Float(string="Referral Rate (%)")
    referral_total = fields.Monetary(string="Referral Total", compute='_compute_commission_totals', store=True)

    cashback_name = fields.Char(string="Cashback Name")
    cashback_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Cashback Commission Type")
    cashback_rate = fields.Float(string="Cashback Rate (%)")
    cashback_total = fields.Monetary(string="Cashback Total", compute='_compute_commission_totals', store=True)

    other_name = fields.Char(string="Other Name")
    other_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Other Commission Type")
    other_rate = fields.Float(string="Other Rate (%)")
    other_total = fields.Monetary(string="Other Total", compute='_compute_commission_totals', store=True)

    # Internal Commission Fields
    agent1_name = fields.Char(string="Agent 1 Name")
    agent1_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Agent 1 Commission Type")
    agent1_rate = fields.Float(string="Agent 1 Rate (%)")
    agent1_total = fields.Monetary(string="Agent 1 Total", compute='_compute_commission_totals', store=True)

    agent2_name = fields.Char(string="Agent 2 Name")
    agent2_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Agent 2 Commission Type")
    agent2_rate = fields.Float(string="Agent 2 Rate (%)")
    agent2_total = fields.Monetary(string="Agent 2 Total", compute='_compute_commission_totals', store=True)

    manager_name = fields.Char(string="Manager Name")
    manager_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Manager Commission Type")
    manager_rate = fields.Float(string="Manager Rate (%)")
    manager_total = fields.Monetary(string="Manager Total", compute='_compute_commission_totals', store=True)

    director_name = fields.Char(string="Director Name")
    director_commission_type = fields.Selection([
        ('sale_value', 'As per Sale Value Percentage'),
        ('gross_commission', 'As per Gross Commission Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Director Commission Type")
    director_rate = fields.Float(string="Director Rate (%)")
    director_total = fields.Monetary(string="Director Total", compute='_compute_commission_totals', store=True)

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

    def _get_commission_fields(self):
        return [
            ('broker_agency', 'Broker/Agency'),
            ('referral', 'Referral'),
            ('cashback', 'Cashback'),
            ('other', 'Other'),
            ('agent1', 'Agent 1'),
            ('agent2', 'Agent 2'),
            ('manager', 'Manager'),
            ('director', 'Director'),
        ]