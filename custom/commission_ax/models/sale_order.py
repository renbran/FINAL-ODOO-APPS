from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_ids = fields.One2many('purchase.order', 'sale_order_id', string="Purchase Orders")

    sale_value = fields.Float(string="Sale Value")
    commission_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], default='pending', string="Commission Status")
    commission_processed = fields.Boolean(string="Commission Processed")

    # Total and shares
    total_commission_amount = fields.Float(string="Total Commission Amount")
    company_share = fields.Float(string="Company Share")
    net_company_share = fields.Float(string="Net Company Share")

    # External Party
    external_party_id = fields.Many2one('res.partner', string="External Party")
    external_party_role = fields.Char(string="Role")
    external_party_calculation_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], default='percentage')
    external_party_percentage = fields.Float(string="% Commission")
    external_party_fixed_amount = fields.Float(string="Fixed Commission")
    external_party_commission = fields.Float(string="Commission Amount")

    # Consultant
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_role = fields.Char(string="Role")
    consultant_calculation_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], default='percentage')
    consultant_percentage = fields.Float(string="% Commission")
    consultant_fixed_amount = fields.Float(string="Fixed Commission")
    consultant_commission = fields.Float(string="Commission Amount")

    # Second Agent
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    second_agent_role = fields.Char(string="Role")
    second_agent_calculation_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], default='percentage')
    second_agent_percentage = fields.Float(string="% Commission")
    second_agent_fixed_amount = fields.Float(string="Fixed Commission")
    second_agent_commission = fields.Float(string="Commission Amount")

    # Manager
    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_role = fields.Char(string="Role")
    manager_calculation_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], default='percentage')
    manager_percentage = fields.Float(string="% Commission")
    manager_fixed_amount = fields.Float(string="Fixed Commission")
    manager_commission = fields.Float(string="Commission Amount")

    # Director
    director_id = fields.Many2one('res.partner', string="Director")
    director_role = fields.Char(string="Role")
    director_calculation_type = fields.Selection([('percentage', 'Percentage'), ('fixed', 'Fixed')], default='percentage')
    director_percentage = fields.Float(string="% Commission")
    director_fixed_amount = fields.Float(string="Fixed Commission")
    director_commission = fields.Float(string="Commission Amount")

    def action_process_commissions(self):
        for order in self:
            # Sample logic for commission calculation (expand as needed)
            total = order.x_sale_value or 0.0

            order.external_party_commission = order._calculate_commission(order.external_party_calculation_type, total, order.external_party_percentage, order.external_party_fixed_amount)
            order.consultant_commission = order._calculate_commission(order.consultant_calculation_type, total, order.consultant_percentage, order.consultant_fixed_amount)
            order.second_agent_commission = order._calculate_commission(order.second_agent_calculation_type, total, order.second_agent_percentage, order.second_agent_fixed_amount)
            order.manager_commission = order._calculate_commission(order.manager_calculation_type, total, order.manager_percentage, order.manager_fixed_amount)
            order.director_commission = order._calculate_commission(order.director_calculation_type, total, order.director_percentage, order.director_fixed_amount)

            total_commission = sum([
                order.external_party_commission,
                order.consultant_commission,
                order.second_agent_commission,
                order.manager_commission,
                order.director_commission
            ])
            order.total_commission_amount = total_commission
            order.company_share = total - total_commission
            order.net_company_share = order.company_share  # Modify if needed

            order.commission_status = 'completed'
            order.commission_processed = True

    def _calculate_commission(self, calc_type, base_amount, percentage, fixed_amount):
        if calc_type == 'percentage':
            return base_amount * (percentage / 100.0)
        elif calc_type == 'fixed':
            return fixed_amount or 0.0
        return 0.0