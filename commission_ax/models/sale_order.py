from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ===========================================
    # COMMISSION CALCULATION METHODS
    # ===========================================
    
    # Commission calculation method (global)
    commission_calculation_method = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Default Commission Method', default='untaxed_total',
       help="Default method for commission calculation")
    
    # Individual commission type for each party
    broker_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Broker Commission Type', default='untaxed_total')
    
    referrer_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Referrer Commission Type', default='untaxed_total')
    
    cashback_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Cashback Commission Type', default='untaxed_total')
    
    other_external_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Other External Commission Type', default='untaxed_total')
    
    agent1_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Agent 1 Commission Type', default='untaxed_total')
    
    agent2_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Agent 2 Commission Type', default='untaxed_total')
    
    manager_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Manager Commission Type', default='untaxed_total')
    
    director_commission_type = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Director Commission Type', default='untaxed_total')
    
    commission_base_amount = fields.Monetary(
        string='Commission Base Amount',
        currency_field='currency_id',
        compute='_compute_commission_base_amount',
        store=True,
        help="Base amount used for commission calculations"
    )

    # ===========================================
    # GROUP A - EXTERNAL COMMISSIONS
    # ===========================================
    
    # External commission totals
    total_external_commission_rate = fields.Float(
        string='Total External Rate (%)',
        compute='_compute_commission_totals',
        store=True,
        digits=(5, 2),
        help="Sum of all external commission rates"
    )
    
    total_external_commission_amount = fields.Monetary(
        string='Total External Amount',
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True,
        help="Sum of all external commission amounts"
    )
    
    # Broker Commission
    broker_partner_id = fields.Many2one(
        'res.partner',
        string="Broker",
        tracking=True,
        help="Select the broker partner"
    )
    
    broker_rate = fields.Float(
        string="Broker Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    broker_amount = fields.Monetary(
        string="Broker Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Commission amount for broker"
    )

    # Referrer Commission
    referrer_partner_id = fields.Many2one(
        'res.partner',
        string="Referrer",
        tracking=True,
        help="Select the referrer partner"
    )
    
    referrer_rate = fields.Float(
        string="Referrer Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    referrer_amount = fields.Monetary(
        string="Referrer Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Commission amount for referrer"
    )

    # Cashback Commission
    cashback_partner_id = fields.Many2one(
        'res.partner',
        string="Cashback Recipient",
        tracking=True,
        help="Select the cashback recipient"
    )
    
    cashback_rate = fields.Float(
        string="Cashback Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Cashback rate as percentage"
    )
    
    cashback_amount = fields.Monetary(
        string="Cashback Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Cashback amount"
    )

    # Other External Party
    other_external_partner_id = fields.Many2one(
        'res.partner',
        string="Other External Party",
        tracking=True,
        help="Select other external commission recipient"
    )
    
    other_external_rate = fields.Float(
        string="Other External Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    other_external_amount = fields.Monetary(
        string="Other External Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Commission amount for other external party"
    )

    # ===========================================
    # GROUP B - INTERNAL COMMISSIONS
    # ===========================================
    
    # Internal commission totals
    total_internal_commission_rate = fields.Float(
        string='Total Internal Rate (%)',
        compute='_compute_commission_totals',
        store=True,
        digits=(5, 2),
        help="Sum of all internal commission rates"
    )
    
    total_internal_commission_amount = fields.Monetary(
        string='Total Internal Amount',
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True,
        help="Sum of all internal commission amounts"
    )
    
    # Agent 1
    agent1_partner_id = fields.Many2one(
        'res.partner',
        string='Agent 1',
        tracking=True,
        help="Select Agent 1 for internal commission"
    )
    
    agent1_rate = fields.Float(
        string='Agent 1 Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    agent1_amount = fields.Monetary(
        string='Agent 1 Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Commission amount for Agent 1"
    )

    # Agent 2
    agent2_partner_id = fields.Many2one(
        'res.partner',
        string='Agent 2',
        tracking=True,
        help="Select Agent 2 for internal commission"
    )
    
    agent2_rate = fields.Float(
        string='Agent 2 Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    agent2_amount = fields.Monetary(
        string='Agent 2 Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Commission amount for Agent 2"
    )

    # Manager
    manager_partner_id = fields.Many2one(
        'res.partner',
        string='Manager',
        tracking=True,
        help="Select Manager for internal commission"
    )
    
    manager_rate = fields.Float(
        string='Manager Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    manager_amount = fields.Monetary(
        string='Manager Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Commission amount for Manager"
    )

    # Director
    director_partner_id = fields.Many2one(
        'res.partner',
        string='Director',
        tracking=True,
        help="Select Director for internal commission"
    )
    
    director_rate = fields.Float(
        string='Director Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage"
    )
    
    director_amount = fields.Monetary(
        string='Director Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Commission amount for Director"
    )

    # ===========================================
    # COMMISSION SUMMARY FIELDS
    # ===========================================
    
    total_commission_rate = fields.Float(
        string='Total Commission Rate (%)',
        compute='_compute_commission_totals',
        store=True,
        digits=(5, 2),
        help="Sum of all commission rates"
    )
    
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True,
        help="Sum of all commission amounts"
    )
    
    company_share = fields.Monetary(
        string="Company Share", 
        compute='_compute_commission_totals', 
        store=True,
        help="Amount remaining for company after all commissions"
    )
    
    net_company_share = fields.Monetary(
        string="Net Company Share", 
        compute='_compute_commission_totals', 
        store=True,
        help="Final company share after all deductions"
    )

    # Commission status and control
    commission_status = fields.Selection([
        ('draft', 'Draft'),  
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Commission Status', default='draft', tracking=True)
    
    commission_processed = fields.Boolean(
        string="Commission Processed", 
        default=False,
        help="Indicates if commission purchase orders have been generated"
    )

    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    
    # Smart button count
    purchase_order_count = fields.Integer(
        string='Purchase Orders Count',
        compute='_compute_purchase_order_count'
    )

    # ===========================================
    # COMPUTE METHODS
    # ===========================================
    
    @api.depends('commission_calculation_method', 'amount_untaxed', 'amount_total', 'order_line.price_unit')
    def _compute_commission_base_amount(self):
        """Compute the base amount for commission calculations"""
        for order in self:
            if order.commission_calculation_method == 'price_unit':
                # Sum of all line price units
                order.commission_base_amount = sum(line.price_unit * line.product_uom_qty for line in order.order_line)
            elif order.commission_calculation_method == 'untaxed_total':
                order.commission_base_amount = order.amount_untaxed
            elif order.commission_calculation_method == 'fixed_amount':
                # For fixed amount, base amount is just 1 (percentages will be treated as fixed amounts)
                order.commission_base_amount = 1.0
            else:
                order.commission_base_amount = order.amount_untaxed

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        """Compute count of related purchase orders"""
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)

    @api.depends(
        'commission_base_amount', 'commission_calculation_method',
        # External fields
        'broker_rate', 'broker_amount', 'broker_commission_type',
        'referrer_rate', 'referrer_amount', 'referrer_commission_type',
        'cashback_rate', 'cashback_amount', 'cashback_commission_type',
        'other_external_rate', 'other_external_amount', 'other_external_commission_type',
        # Internal fields  
        'agent1_rate', 'agent1_amount', 'agent1_commission_type',
        'agent2_rate', 'agent2_amount', 'agent2_commission_type',
        'manager_rate', 'manager_amount', 'manager_commission_type',
        'director_rate', 'director_amount', 'director_commission_type'
    )
    def _compute_commission_totals(self):
        """Compute all commission totals and company shares"""
        for order in self:
            # Calculate individual commission amounts based on each party's method
            base_amount_untaxed = order.amount_untaxed
            base_amount_price_unit = sum(line.price_unit * line.product_uom_qty for line in order.order_line)
            
            # Helper function to calculate commission based on individual type
            def calculate_commission(rate, amount, commission_type):
                if commission_type == 'fixed_amount':
                    return amount or 0
                elif commission_type == 'price_unit':
                    return (rate / 100.0 * base_amount_price_unit) if rate else (amount or 0)
                else:  # untaxed_total
                    return (rate / 100.0 * base_amount_untaxed) if rate else (amount or 0)
            
            # External commissions - each with its own calculation type
            external_amounts = [
                calculate_commission(order.broker_rate, order.broker_amount, order.broker_commission_type),
                calculate_commission(order.referrer_rate, order.referrer_amount, order.referrer_commission_type),
                calculate_commission(order.cashback_rate, order.cashback_amount, order.cashback_commission_type),
                calculate_commission(order.other_external_rate, order.other_external_amount, order.other_external_commission_type)
            ]
            
            # Internal commissions - each with its own calculation type
            internal_amounts = [
                calculate_commission(order.agent1_rate, order.agent1_amount, order.agent1_commission_type),
                calculate_commission(order.agent2_rate, order.agent2_amount, order.agent2_commission_type),
                calculate_commission(order.manager_rate, order.manager_amount, order.manager_commission_type),
                calculate_commission(order.director_rate, order.director_amount, order.director_commission_type)
            ]
            
            # Calculate rates (for fixed amounts, we show the amount as rate for consistency)
            external_rates = [
                order.broker_rate if order.broker_commission_type != 'fixed_amount' else 0,
                order.referrer_rate if order.referrer_commission_type != 'fixed_amount' else 0,
                order.cashback_rate if order.cashback_commission_type != 'fixed_amount' else 0,
                order.other_external_rate if order.other_external_commission_type != 'fixed_amount' else 0
            ]
            
            internal_rates = [
                order.agent1_rate if order.agent1_commission_type != 'fixed_amount' else 0,
                order.agent2_rate if order.agent2_commission_type != 'fixed_amount' else 0,
                order.manager_rate if order.manager_commission_type != 'fixed_amount' else 0,
                order.director_rate if order.director_commission_type != 'fixed_amount' else 0
            ]

            # Update totals
            order.total_external_commission_rate = sum(external_rates)
            order.total_external_commission_amount = sum(external_amounts)
            order.total_internal_commission_rate = sum(internal_rates)
            order.total_internal_commission_amount = sum(internal_amounts)
            
            order.total_commission_rate = order.total_external_commission_rate + order.total_internal_commission_rate
            order.total_commission_amount = order.total_external_commission_amount + order.total_internal_commission_amount
            
            # Company shares
            order.company_share = base_amount_untaxed - order.total_commission_amount
            order.net_company_share = order.company_share

    # ===========================================
    # ONCHANGE METHODS FOR AUTO-CALCULATION
    # ===========================================
    
    # External Commission Onchanges
    @api.onchange('broker_rate', 'broker_commission_type')
    def _onchange_broker_rate(self):
        if self.broker_rate and self.broker_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.broker_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.broker_amount = (self.broker_rate / 100.0) * base_amount

    @api.onchange('broker_amount', 'broker_commission_type')
    def _onchange_broker_amount(self):
        if self.broker_amount and self.broker_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.broker_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.broker_rate = (self.broker_amount / base_amount) * 100.0

    @api.onchange('referrer_rate', 'referrer_commission_type')
    def _onchange_referrer_rate(self):
        if self.referrer_rate and self.referrer_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.referrer_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.referrer_amount = (self.referrer_rate / 100.0) * base_amount

    @api.onchange('referrer_amount', 'referrer_commission_type')
    def _onchange_referrer_amount(self):
        if self.referrer_amount and self.referrer_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.referrer_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.referrer_rate = (self.referrer_amount / base_amount) * 100.0

    @api.onchange('cashback_rate', 'cashback_commission_type')
    def _onchange_cashback_rate(self):
        if self.cashback_rate and self.cashback_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.cashback_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.cashback_amount = (self.cashback_rate / 100.0) * base_amount

    @api.onchange('cashback_amount', 'cashback_commission_type')
    def _onchange_cashback_amount(self):
        if self.cashback_amount and self.cashback_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.cashback_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.cashback_rate = (self.cashback_amount / base_amount) * 100.0

    @api.onchange('other_external_rate', 'other_external_commission_type')
    def _onchange_other_external_rate(self):
        if self.other_external_rate and self.other_external_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.other_external_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.other_external_amount = (self.other_external_rate / 100.0) * base_amount

    @api.onchange('other_external_amount', 'other_external_commission_type')
    def _onchange_other_external_amount(self):
        if self.other_external_amount and self.other_external_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.other_external_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.other_external_rate = (self.other_external_amount / base_amount) * 100.0

    # Internal Commission Onchanges
    @api.onchange('agent1_rate', 'agent1_commission_type')
    def _onchange_agent1_rate(self):
        if self.agent1_rate and self.agent1_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.agent1_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.agent1_amount = (self.agent1_rate / 100.0) * base_amount

    @api.onchange('agent1_amount', 'agent1_commission_type')
    def _onchange_agent1_amount(self):
        if self.agent1_amount and self.agent1_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.agent1_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.agent1_rate = (self.agent1_amount / base_amount) * 100.0

    @api.onchange('agent2_rate', 'agent2_commission_type')
    def _onchange_agent2_rate(self):
        if self.agent2_rate and self.agent2_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.agent2_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.agent2_amount = (self.agent2_rate / 100.0) * base_amount

    @api.onchange('agent2_amount', 'agent2_commission_type')
    def _onchange_agent2_amount(self):
        if self.agent2_amount and self.agent2_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.agent2_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.agent2_rate = (self.agent2_amount / base_amount) * 100.0

    @api.onchange('manager_rate', 'manager_commission_type')
    def _onchange_manager_rate(self):
        if self.manager_rate and self.manager_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.manager_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.manager_amount = (self.manager_rate / 100.0) * base_amount

    @api.onchange('manager_amount', 'manager_commission_type')
    def _onchange_manager_amount(self):
        if self.manager_amount and self.manager_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.manager_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.manager_rate = (self.manager_amount / base_amount) * 100.0

    @api.onchange('director_rate', 'director_commission_type')
    def _onchange_director_rate(self):
        if self.director_rate and self.director_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.director_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            self.director_amount = (self.director_rate / 100.0) * base_amount

    @api.onchange('director_amount', 'director_commission_type')
    def _onchange_director_amount(self):
        if self.director_amount and self.director_commission_type != 'fixed_amount':
            base_amount = self.amount_untaxed if self.director_commission_type == 'untaxed_total' else sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            if base_amount:
                self.director_rate = (self.director_amount / base_amount) * 100.0

    # ===========================================
    # ACTION METHODS
    # ============================================
    
    def action_calculate_commissions(self):
        """Calculate all commissions based on current settings"""
        self.ensure_one()
        self._compute_commission_base_amount()
        self._compute_commission_totals()
        self.commission_status = 'calculated'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Commission Calculated'),
                'message': _('All commissions have been calculated successfully.'),
                'type': 'success',
            }
        }

    def action_confirm_commissions(self):
        """Confirm commission calculations"""
        self.ensure_one()
        if self.commission_status != 'calculated':
            raise UserError(_('Please calculate commissions first.'))
        self.commission_status = 'confirmed'
        return True

    def action_reset_commissions(self):
        """Reset commission status to draft"""
        self.ensure_one()
        self.commission_status = 'draft'
        return True

    def action_view_purchase_orders(self):
        """Smart button action to view related purchase orders"""
        self.ensure_one()
        if len(self.purchase_order_ids) > 1:
            return {
                'name': _('Commission Purchase Orders'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'domain': [('id', 'in', self.purchase_order_ids.ids)],
                'target': 'current',
            }
        elif len(self.purchase_order_ids) == 1:
            return {
                'name': _('Commission Purchase Order'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                'res_id': self.purchase_order_ids.ids[0],
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Purchase Orders'),
                    'message': _('No commission purchase orders have been generated yet.'),
                    'type': 'info',
                }
            }

    def action_confirm(self):
        """Extend Sale Order Confirmation"""
        res = super(SaleOrder, self).action_confirm()
        # Auto-calculate commissions when order is confirmed
        if self.commission_status == 'draft':
            self.action_calculate_commissions()
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    origin_so_id = fields.Many2one('sale.order', string="Source Sale Order", readonly=True)
    commission_type = fields.Char(string="Commission Type", readonly=True)
    
    def action_view_source_sale_order(self):
        """Action to view the source sale order"""
        self.ensure_one()
        if self.origin_so_id:
            return {
                'name': _('Source Sale Order'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.origin_so_id.id,
                'target': 'current',
            }
        return False

    # ===========================================
    # VALIDATION AND CONSTRAINTS
    # ===========================================
    
    @api.constrains('total_commission_rate')
    def _check_total_commission_rate(self):
        """Validate that total commission rate doesn't exceed 100%"""
        for order in self:
            if order.total_commission_rate > 100:
                raise ValidationError(_('Total commission rate cannot exceed 100%. Current total: %.2f%%') % order.total_commission_rate)
    
    @api.constrains('broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate', 
                    'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _check_individual_commission_rates(self):
        """Validate individual commission rates"""
        for order in self:
            rates = [
                order.broker_rate, order.referrer_rate, order.cashback_rate, order.other_external_rate,
                order.agent1_rate, order.agent2_rate, order.manager_rate, order.director_rate
            ]
            for rate in rates:
                if rate < 0:
                    raise ValidationError(_('Commission rates cannot be negative.'))
                if rate > 50:  # Warning for high individual rates
                    _logger.warning(f'High commission rate detected: {rate}% in order {order.name}')

    @api.constrains('broker_amount', 'referrer_amount', 'cashback_amount', 'other_external_amount',
                    'agent1_amount', 'agent2_amount', 'manager_amount', 'director_amount')
    def _check_commission_amounts(self):
        """Validate commission amounts"""
        for order in self:
            amounts = [
                order.broker_amount, order.referrer_amount, order.cashback_amount, order.other_external_amount,
                order.agent1_amount, order.agent2_amount, order.manager_amount, order.director_amount
            ]
            for amount in amounts:
                if amount < 0:
                    raise ValidationError(_('Commission amounts cannot be negative.'))

    # ===========================================
    # HELPER METHODS
    # ===========================================
    
    def _prepare_purchase_order_vals(self, partner, product, amount, description):
        """Prepare values for auto-creation of Purchase Orders."""
        return {
            'partner_id': partner.id,
            'date_order': fields.Date.today(),
            'order_line': [
                (0, 0, {
                    'product_id': product.id,
                    'name': description,
                    'product_qty': 1.0,
                    'product_uom': product.uom_id.id,
                    'price_unit': amount,
                })
            ],
            'origin_so_id': self.id,
            'origin': self.name,
        }

    def _get_commission_product(self, commission_type='general'):
        """Helper method to get commission product or create one if not found."""
        product_name = f"{commission_type.title()} Commission"
        
        # Try to find existing product
        product = self.env['product.product'].search([
            ('name', '=', product_name),
            ('type', '=', 'service')
        ], limit=1)
        
        if not product:
            # Create new commission product
            product = self.env['product.product'].create({
                'name': product_name,
                'type': 'service',
                'list_price': 0.0,
                'purchase_ok': True,
                'sale_ok': False,
                'categ_id': self.env.ref('product.product_category_all').id,
            })
        
        return product

    def action_generate_commission_purchase_orders(self):
        """Generate Purchase Orders for all commissions"""
        self.ensure_one()
        
        if self.commission_status != 'confirmed':
            raise UserError(_('Please confirm commissions before generating purchase orders.'))
        
        if self.commission_processed:
            raise UserError(_('Commission purchase orders have already been generated.'))
        
        purchase_orders_created = []

        # External Commissions
        external_commissions = [
            (self.broker_partner_id, self.broker_amount, 'Broker'),
            (self.referrer_partner_id, self.referrer_amount, 'Referrer'),
            (self.cashback_partner_id, self.cashback_amount, 'Cashback'),
            (self.other_external_partner_id, self.other_external_amount, 'Other External'),
        ]

        for partner, amount, comm_type in external_commissions:
            if partner and amount > 0:
                product = self._get_commission_product(comm_type.lower())
                po_vals = self._prepare_purchase_order_vals(
                    partner=partner,
                    product=product,
                    amount=amount,
                    description=f"{comm_type} Commission for SO: {self.name}",
                )
                po_vals['commission_type'] = comm_type
                po = self.env['purchase.order'].create(po_vals)
                purchase_orders_created.append(po)

        # Internal Commissions
        internal_commissions = [
            (self.agent1_partner_id, self.agent1_amount, 'Agent 1'),
            (self.agent2_partner_id, self.agent2_amount, 'Agent 2'),
            (self.manager_partner_id, self.manager_amount, 'Manager'),
            (self.director_partner_id, self.director_amount, 'Director'),
        ]

        for partner, amount, comm_type in internal_commissions:
            if partner and amount > 0:
                product = self._get_commission_product(comm_type.lower().replace(' ', '_'))
                po_vals = self._prepare_purchase_order_vals(
                    partner=partner,
                    product=product,
                    amount=amount,
                    description=f"{comm_type} Commission for SO: {self.name}",
                )
                po_vals['commission_type'] = comm_type
                po = self.env['purchase.order'].create(po_vals)
                purchase_orders_created.append(po)

        if purchase_orders_created:
            self.commission_processed = True
            self.commission_status = 'paid'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Purchase Orders Created'),
                    'message': _('%d purchase orders have been created for commissions.') % len(purchase_orders_created),
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client', 
                'tag': 'display_notification',
                'params': {
                    'title': _('No Purchase Orders'),
                    'message': _('No commission recipients found or commission amounts are zero.'),
                    'type': 'warning',
                }
            }

    def _auto_generate_purchase_orders(self):
        """Auto-generate Purchase Orders for commissions - Legacy method for backward compatibility"""
        return self.action_generate_commission_purchase_orders()

    # ===========================================
