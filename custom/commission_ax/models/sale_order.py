from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ===========================================
    # COMMISSION CALCULATION METHODS
    # ===========================================
    
    commission_calculation_method = fields.Selection([
        ('price_unit', 'Based on Price Unit'),
        ('untaxed_total', 'Based on Untaxed Total'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Default Commission Method', default='untaxed_total',
       help="Default method for commission calculation")
    
    # Commission types for each party
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
    # EXTERNAL COMMISSIONS (GROUP A)
    # ===========================================
    
    total_external_commission_rate = fields.Float(
        string='Total External Rate (%)',
        compute='_compute_commission_totals',
        store=True,
        digits='Commission Rate',
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
        domain="[('is_company', '=', True), ('supplier_rank', '>', 0)]",
        help="Select the broker partner"
    )
    
    broker_rate = fields.Float(
        string="Broker Rate (%)",
        tracking=True,
        digits='Commission Rate',
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
        domain="[('supplier_rank', '>', 0)]",
        help="Select the referrer partner"
    )
    
    referrer_rate = fields.Float(
        string="Referrer Rate (%)",
        tracking=True,
        digits='Commission Rate',
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
        digits='Commission Rate',
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
        domain="[('supplier_rank', '>', 0)]",
        help="Select other external commission recipient"
    )
    
    other_external_rate = fields.Float(
        string="Other External Rate (%)",
        tracking=True,
        digits='Commission Rate',
        help="Commission rate as percentage"
    )
    
    other_external_amount = fields.Monetary(
        string="Other External Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Commission amount for other external party"
    )

    # ===========================================
    # INTERNAL COMMISSIONS (GROUP B)
    # ===========================================
    
    total_internal_commission_rate = fields.Float(
        string='Total Internal Rate (%)',
        compute='_compute_commission_totals',
        store=True,
        digits='Commission Rate',
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
        domain="[('is_company', '=', False), ('supplier_rank', '>', 0)]",
        help="Select Agent 1 for internal commission"
    )
    
    agent1_rate = fields.Float(
        string='Agent 1 Rate (%)', 
        tracking=True, 
        digits='Commission Rate',
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
        domain="[('is_company', '=', False), ('supplier_rank', '>', 0)]",
        help="Select Agent 2 for internal commission"
    )
    
    agent2_rate = fields.Float(
        string='Agent 2 Rate (%)', 
        tracking=True, 
        digits='Commission Rate',
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
        domain="[('is_company', '=', False), ('supplier_rank', '>', 0)]",
        help="Select Manager for internal commission"
    )
    
    manager_rate = fields.Float(
        string='Manager Rate (%)', 
        tracking=True, 
        digits='Commission Rate',
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
        domain="[('is_company', '=', False), ('supplier_rank', '>', 0)]",
        help="Select Director for internal commission"
    )
    
    director_rate = fields.Float(
        string='Director Rate (%)', 
        tracking=True, 
        digits='Commission Rate',
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
        digits='Commission Rate',
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

    purchase_order_ids = fields.One2many(
        'purchase.order', 
        'origin_so_id', 
        string="Generated Purchase Orders"
    )
    
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
                order.commission_base_amount = sum(
                    line.price_unit * line.product_uom_qty 
                    for line in order.order_line
                )
            elif order.commission_calculation_method == 'untaxed_total':
                order.commission_base_amount = order.amount_untaxed
            elif order.commission_calculation_method == 'fixed_amount':
                # For fixed amount, base amount is just 1
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
            base_amount_untaxed = order.amount_untaxed
            base_amount_price_unit = sum(
                line.price_unit * line.product_uom_qty 
                for line in order.order_line
            )
            
            def calculate_commission(rate, amount, commission_type):
                """Helper function to calculate commission based on type"""
                if commission_type == 'fixed_amount':
                    return amount or 0.0
                elif commission_type == 'price_unit':
                    return (rate / 100.0 * base_amount_price_unit) if rate else (amount or 0.0)
                else:  # untaxed_total
                    return (rate / 100.0 * base_amount_untaxed) if rate else (amount or 0.0)
            
            # External commissions
            external_amounts = [
                calculate_commission(order.broker_rate, order.broker_amount, order.broker_commission_type),
                calculate_commission(order.referrer_rate, order.referrer_amount, order.referrer_commission_type),
                calculate_commission(order.cashback_rate, order.cashback_amount, order.cashback_commission_type),
                calculate_commission(order.other_external_rate, order.other_external_amount, order.other_external_commission_type)
            ]
            
            # Internal commissions
            internal_amounts = [
                calculate_commission(order.agent1_rate, order.agent1_amount, order.agent1_commission_type),
                calculate_commission(order.agent2_rate, order.agent2_amount, order.agent2_commission_type),
                calculate_commission(order.manager_rate, order.manager_amount, order.manager_commission_type),
                calculate_commission(order.director_rate, order.director_amount, order.director_commission_type)
            ]
            
            # Calculate rates (for display purposes)
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
    
    def _get_base_amount_for_commission_type(self, commission_type):
        """Get base amount based on commission type"""
        if commission_type == 'untaxed_total':
            return self.amount_untaxed
        elif commission_type == 'price_unit':
            return sum(line.price_unit * line.product_uom_qty for line in self.order_line)
        return 0.0

    # External Commission Onchanges
    @api.onchange('broker_rate', 'broker_commission_type')
    def _onchange_broker_rate(self):
        if self.broker_rate and self.broker_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.broker_commission_type)
            self.broker_amount = (self.broker_rate / 100.0) * base_amount

    @api.onchange('broker_amount', 'broker_commission_type')
    def _onchange_broker_amount(self):
        if self.broker_amount and self.broker_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.broker_commission_type)
            if base_amount:
                self.broker_rate = (self.broker_amount / base_amount) * 100.0

    @api.onchange('referrer_rate', 'referrer_commission_type')
    def _onchange_referrer_rate(self):
        if self.referrer_rate and self.referrer_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.referrer_commission_type)
            self.referrer_amount = (self.referrer_rate / 100.0) * base_amount

    @api.onchange('referrer_amount', 'referrer_commission_type')
    def _onchange_referrer_amount(self):
        if self.referrer_amount and self.referrer_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.referrer_commission_type)
            if base_amount:
                self.referrer_rate = (self.referrer_amount / base_amount) * 100.0

    # Similar onchange methods for other commissions (keeping original logic but cleaner)
    @api.onchange('cashback_rate', 'cashback_commission_type')
    def _onchange_cashback_rate(self):
        if self.cashback_rate and self.cashback_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.cashback_commission_type)
            self.cashback_amount = (self.cashback_rate / 100.0) * base_amount

    @api.onchange('cashback_amount', 'cashback_commission_type')
    def _onchange_cashback_amount(self):
        if self.cashback_amount and self.cashback_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.cashback_commission_type)
            if base_amount:
                self.cashback_rate = (self.cashback_amount / base_amount) * 100.0

    # ===========================================
    # ACTION METHODS
    # ===========================================
    
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
                'sticky': False,
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
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        
        if len(self.purchase_order_ids) > 1:
            action.update({
                'domain': [('id', 'in', self.purchase_order_ids.ids)],
                'name': _('Commission Purchase Orders'),
            })
        elif len(self.purchase_order_ids) == 1:
            action.update({
                'views': [(self.env.ref('purchase.purchase_order_form').id, 'form')],
                'res_id': self.purchase_order_ids.id,
                'name': _('Commission Purchase Order'),
            })
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
        return action

    def action_generate_commission_purchase_orders(self):
        """Generate Purchase Orders for all commissions"""
        self.ensure_one()
        
        if self.commission_status != 'confirmed':
            raise UserError(_('Please confirm commissions before generating purchase orders.'))
        
        if self.commission_processed:
            raise UserError(_('Commission purchase orders have already been generated.'))
        
        purchase_orders_created = []
        commission_product = self._get_or_create_commission_product()

        # Define commission data
        commission_data = [
            # External commissions
            (self.broker_partner_id, self.broker_amount, 'Broker Commission'),
            (self.referrer_partner_id, self.referrer_amount, 'Referrer Commission'),
            (self.cashback_partner_id, self.cashback_amount, 'Cashback Commission'),
            (self.other_external_partner_id, self.other_external_amount, 'Other External Commission'),
            # Internal commissions
            (self.agent1_partner_id, self.agent1_amount, 'Agent 1 Commission'),
            (self.agent2_partner_id, self.agent2_amount, 'Agent 2 Commission'),
            (self.manager_partner_id, self.manager_amount, 'Manager Commission'),
            (self.director_partner_id, self.director_amount, 'Director Commission'),
        ]

        for partner, amount, comm_type in commission_data:
            if partner and amount > 0:
                po_vals = {
                    'partner_id': partner.id,
                    'date_order': fields.Date.today(),
                    'origin': self.name,
                    'origin_so_id': self.id,
                    'commission_type': comm_type,
                    'order_line': [(0, 0, {
                        'product_id': commission_product.id,
                        'name': f"{comm_type} for SO: {self.name}",
                        'product_qty': 1.0,
                        'product_uom': commission_product.uom_po_id.id,
                        'price_unit': amount,
                    })],
                }
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

    def _get_or_create_commission_product(self):
        """Get or create commission service product"""
        product = self.env['product.product'].search([
            ('name', '=', 'Commission Service'),
            ('type', '=', 'service')
        ], limit=1)
        
        if not product:
            product = self.env['product.product'].create({
                'name': 'Commission Service',
                'type': 'service',
                'list_price': 0.0,
                'purchase_ok': True,
                'sale_ok': False,
                'categ_id': self.env.ref('product.product_category_all').id,
            })
        
        return product

    def action_confirm(self):
        """Extend Sale Order Confirmation"""
        res = super().action_confirm()
        # Auto-calculate commissions when order is confirmed
        for order in self:
            if order.commission_status == 'draft':
                order.action_calculate_commissions()
        return res

    # ===========================================
    # VALIDATION AND CONSTRAINTS
    # ===========================================
    
    @api.constrains('total_commission_rate')
    def _check_total_commission_rate(self):
        """Validate that total commission rate doesn't exceed 100%"""
        for order in self:
            if order.total_commission_rate > 100:
                raise ValidationError(
                    _('Total commission rate cannot exceed 100%%. Current total: %.2f%%') 
                    % order.total_commission_rate
                )
    
    @api.constrains(
        'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate', 
        'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate'
    )
    def _check_individual_commission_rates(self):
        """Validate individual commission rates"""
        for order in self:
            rates = [
                order.broker_rate, order.referrer_rate, order.cashback_rate, 
                order.other_external_rate, order.agent1_rate, order.agent2_rate, 
                order.manager_rate, order.director_rate
            ]
            for rate in rates:
                if rate < 0:
                    raise ValidationError(_('Commission rates cannot be negative.'))
                if rate > 100:
                    raise ValidationError(_('Individual commission rates cannot exceed 100%.'))

    @api.constrains(
        'broker_amount', 'referrer_amount', 'cashback_amount', 'other_external_amount',
        'agent1_amount', 'agent2_amount', 'manager_amount', 'director_amount'
    )
    def _check_commission_amounts(self):
        """Validate commission amounts"""
        for order in self:
            amounts = [
                order.broker_amount, order.referrer_amount, order.cashback_amount, 
                order.other_external_amount, order.agent1_amount, order.agent2_amount, 
                order.manager_amount, order.director_amount
            ]
            for amount in amounts:
                if amount < 0:
                    raise ValidationError(_('Commission amounts cannot be negative.'))


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    origin_so_id = fields.Many2one(
        'sale.order', 
        string="Source Sale Order", 
        readonly=True
    )
    commission_type = fields.Char(
        string="Commission Type", 
        readonly=True
    )
    
    def action_view_source_sale_order(self):
        """Action to view the source sale order"""
        self.ensure_one()
        if self.origin_so_id:
            action = self.env.ref('sale.action_orders').read()[0]
            action.update({
                'views': [(self.env.ref('sale.view_order_form').id, 'form')],
                'res_id': self.origin_so_id.id,
                'name': _('Source Sale Order'),
            })
            return action
        return False