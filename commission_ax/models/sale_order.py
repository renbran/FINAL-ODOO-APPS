from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ===========================================
    # COMMISSION CALCULATION TYPES (Individual)
    # ===========================================
    
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
    
    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)
    
    @api.depends(
        'amount_untaxed', 'order_line.sales_value', 'order_line.product_uom_qty',
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
            # Get base amounts for different calculation types
            untaxed_amount = order.amount_untaxed
            unit_price_total = sum(line.sales_value * line.product_uom_qty for line in order.order_line)

            def calculate_commission(rate, amount, commission_type):
                """
                Calculate commission based on individual commission type:
                1. 'price_unit': Rate(%) × Sales Value Total = Commission Amount
                2. 'untaxed_total': Rate(%) × Untaxed Amount = Commission Amount  
                3. 'fixed_amount': Use fixed amount directly
                """
                if commission_type == 'price_unit':
                    # Rate(%) × Sales Value Total = Commission Amount
                    return (rate / 100.0) * unit_price_total if rate else 0.0
                elif commission_type == 'untaxed_total':
                    # Rate(%) × Untaxed Amount = Commission Amount
                    return (rate / 100.0) * untaxed_amount if rate else 0.0
                elif commission_type == 'fixed_amount':
                    # Use fixed amount directly (capped at untaxed total for safety)
                    return min(amount or 0.0, untaxed_amount)
                return 0.0

            # Calculate commission amounts for all parties using their individual types
            external_commissions = [
                ('broker', calculate_commission(order.broker_rate, order.broker_amount, order.broker_commission_type)),
                ('referrer', calculate_commission(order.referrer_rate, order.referrer_amount, order.referrer_commission_type)),
                ('cashback', calculate_commission(order.cashback_rate, order.cashback_amount, order.cashback_commission_type)),
                ('other_external', calculate_commission(order.other_external_rate, order.other_external_amount, order.other_external_commission_type))
            ]
            
            internal_commissions = [
                ('agent1', calculate_commission(order.agent1_rate, order.agent1_amount, order.agent1_commission_type)),
                ('agent2', calculate_commission(order.agent2_rate, order.agent2_amount, order.agent2_commission_type)),
                ('manager', calculate_commission(order.manager_rate, order.manager_amount, order.manager_commission_type)),
                ('director', calculate_commission(order.director_rate, order.director_amount, order.director_commission_type))
            ]

            # Calculate rates for display (only show rates for percentage-based calculations, 0 for fixed amounts)
            def get_display_rate(rate, commission_type):
                return rate if commission_type in ['price_unit', 'untaxed_total'] else 0.0

            external_rates = [
                get_display_rate(order.broker_rate, order.broker_commission_type),
                get_display_rate(order.referrer_rate, order.referrer_commission_type),
                get_display_rate(order.cashback_rate, order.cashback_commission_type),
                get_display_rate(order.other_external_rate, order.other_external_commission_type)
            ]
            
            internal_rates = [
                get_display_rate(order.agent1_rate, order.agent1_commission_type),
                get_display_rate(order.agent2_rate, order.agent2_commission_type),
                get_display_rate(order.manager_rate, order.manager_commission_type),
                get_display_rate(order.director_rate, order.director_commission_type)
            ]

            # Get amounts only
            external_amounts = [comm[1] for comm in external_commissions]
            internal_amounts = [comm[1] for comm in internal_commissions]

            # Set computed values
            order.total_external_commission_rate = sum(external_rates)
            order.total_external_commission_amount = sum(external_amounts)
            order.total_internal_commission_rate = sum(internal_rates)
            order.total_internal_commission_amount = sum(internal_amounts)
            order.total_commission_rate = order.total_external_commission_rate + order.total_internal_commission_rate
            order.total_commission_amount = order.total_external_commission_amount + order.total_internal_commission_amount
            order.company_share = untaxed_amount - order.total_commission_amount
            order.net_company_share = order.company_share

    # ===========================================
    # ONCHANGE METHODS FOR AUTO-CALCULATION
    # ===========================================

    def _get_base_amount_for_commission_type(self, commission_type):
        """Get base amount based on commission type"""
        if commission_type == 'untaxed_total':
            return self.amount_untaxed
        elif commission_type == 'price_unit':
            return sum(line.sales_value * line.product_uom_qty for line in self.order_line)
        return 0.0

    # ========== EXTERNAL COMMISSION ONCHANGES ==========

    # Broker Commission
    @api.onchange('broker_rate', 'broker_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_broker_rate(self):
        """Auto-calculate broker amount when rate changes"""
        if self.broker_commission_type != 'fixed_amount' and self.broker_rate:
            base_amount = self._get_base_amount_for_commission_type(self.broker_commission_type)
            self.broker_amount = (self.broker_rate / 100.0) * base_amount

    @api.onchange('broker_amount', 'broker_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_broker_amount(self):
        """Auto-calculate broker rate when amount changes (except for fixed amount type)"""
        if self.broker_commission_type == 'fixed_amount':
            # Cap fixed amount at untaxed total for safety
            if self.broker_amount and self.amount_untaxed:
                self.broker_amount = min(self.broker_amount, self.amount_untaxed)
        elif self.broker_amount and self.broker_commission_type != 'fixed_amount':
            # Calculate rate from amount: Rate(%) = (Amount / Base Amount) × 100
            base_amount = self._get_base_amount_for_commission_type(self.broker_commission_type)
            if base_amount:
                self.broker_rate = (self.broker_amount / base_amount) * 100.0

    # Referrer Commission
    @api.onchange('referrer_rate', 'referrer_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_referrer_rate(self):
        if self.referrer_commission_type != 'fixed_amount' and self.referrer_rate:
            base_amount = self._get_base_amount_for_commission_type(self.referrer_commission_type)
            self.referrer_amount = (self.referrer_rate / 100.0) * base_amount

    @api.onchange('referrer_amount', 'referrer_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_referrer_amount(self):
        if self.referrer_commission_type == 'fixed_amount':
            if self.referrer_amount and self.amount_untaxed:
                self.referrer_amount = min(self.referrer_amount, self.amount_untaxed)
        elif self.referrer_amount and self.referrer_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.referrer_commission_type)
            if base_amount:
                self.referrer_rate = (self.referrer_amount / base_amount) * 100.0

    # Cashback Commission
    @api.onchange('cashback_rate', 'cashback_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_cashback_rate(self):
        if self.cashback_commission_type != 'fixed_amount' and self.cashback_rate:
            base_amount = self._get_base_amount_for_commission_type(self.cashback_commission_type)
            self.cashback_amount = (self.cashback_rate / 100.0) * base_amount

    @api.onchange('cashback_amount', 'cashback_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_cashback_amount(self):
        if self.cashback_commission_type == 'fixed_amount':
            if self.cashback_amount and self.amount_untaxed:
                self.cashback_amount = min(self.cashback_amount, self.amount_untaxed)
        elif self.cashback_amount and self.cashback_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.cashback_commission_type)
            if base_amount:
                self.cashback_rate = (self.cashback_amount / base_amount) * 100.0

    # Other External Commission
    @api.onchange('other_external_rate', 'other_external_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_other_external_rate(self):
        if self.other_external_commission_type != 'fixed_amount' and self.other_external_rate:
            base_amount = self._get_base_amount_for_commission_type(self.other_external_commission_type)
            self.other_external_amount = (self.other_external_rate / 100.0) * base_amount

    @api.onchange('other_external_amount', 'other_external_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_other_external_amount(self):
        if self.other_external_commission_type == 'fixed_amount':
            if self.other_external_amount and self.amount_untaxed:
                self.other_external_amount = min(self.other_external_amount, self.amount_untaxed)
        elif self.other_external_amount and self.other_external_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.other_external_commission_type)
            if base_amount:
                self.other_external_rate = (self.other_external_amount / base_amount) * 100.0

    # ========== INTERNAL COMMISSION ONCHANGES ==========

    # Agent 1 Commission
    @api.onchange('agent1_rate', 'agent1_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_agent1_rate(self):
        if self.agent1_commission_type != 'fixed_amount' and self.agent1_rate:
            base_amount = self._get_base_amount_for_commission_type(self.agent1_commission_type)
            self.agent1_amount = (self.agent1_rate / 100.0) * base_amount

    @api.onchange('agent1_amount', 'agent1_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_agent1_amount(self):
        if self.agent1_commission_type == 'fixed_amount':
            if self.agent1_amount and self.amount_untaxed:
                self.agent1_amount = min(self.agent1_amount, self.amount_untaxed)
        elif self.agent1_amount and self.agent1_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.agent1_commission_type)
            if base_amount:
                self.agent1_rate = (self.agent1_amount / base_amount) * 100.0

    # Agent 2 Commission
    @api.onchange('agent2_rate', 'agent2_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_agent2_rate(self):
        if self.agent2_commission_type != 'fixed_amount' and self.agent2_rate:
            base_amount = self._get_base_amount_for_commission_type(self.agent2_commission_type)
            self.agent2_amount = (self.agent2_rate / 100.0) * base_amount

    @api.onchange('agent2_amount', 'agent2_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_agent2_amount(self):
        if self.agent2_commission_type == 'fixed_amount':
            if self.agent2_amount and self.amount_untaxed:
                self.agent2_amount = min(self.agent2_amount, self.amount_untaxed)
        elif self.agent2_amount and self.agent2_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.agent2_commission_type)
            if base_amount:
                self.agent2_rate = (self.agent2_amount / base_amount) * 100.0

    # Manager Commission
    @api.onchange('manager_rate', 'manager_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_manager_rate(self):
        if self.manager_commission_type != 'fixed_amount' and self.manager_rate:
            base_amount = self._get_base_amount_for_commission_type(self.manager_commission_type)
            self.manager_amount = (self.manager_rate / 100.0) * base_amount

    @api.onchange('manager_amount', 'manager_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_manager_amount(self):
        if self.manager_commission_type == 'fixed_amount':
            if self.manager_amount and self.amount_untaxed:
                self.manager_amount = min(self.manager_amount, self.amount_untaxed)
        elif self.manager_amount and self.manager_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.manager_commission_type)
            if base_amount:
                self.manager_rate = (self.manager_amount / base_amount) * 100.0

    # Director Commission
    @api.onchange('director_rate', 'director_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_director_rate(self):
        if self.director_commission_type != 'fixed_amount' and self.director_rate:
            base_amount = self._get_base_amount_for_commission_type(self.director_commission_type)
            self.director_amount = (self.director_rate / 100.0) * base_amount

    @api.onchange('director_amount', 'director_commission_type', 'amount_untaxed', 'order_line')
    def _onchange_director_amount(self):
        if self.director_commission_type == 'fixed_amount':
            if self.director_amount and self.amount_untaxed:
                self.director_amount = min(self.director_amount, self.amount_untaxed)
        elif self.director_amount and self.director_commission_type != 'fixed_amount':
            base_amount = self._get_base_amount_for_commission_type(self.director_commission_type)
            if base_amount:
                self.director_rate = (self.director_amount / base_amount) * 100.0

    # ===========================================
    # HELPER METHODS
    # ===========================================
    
    def _calculate_individual_commission(self, rate, amount, commission_type):
        """Calculate individual commission amount based on type"""
        if commission_type == 'fixed_amount':
            return min(amount or 0.0, self.amount_untaxed)
        elif commission_type == 'price_unit':
            unit_price_total = sum(line.sales_value * line.product_uom_qty for line in self.order_line)
            return (rate / 100.0) * unit_price_total if rate else 0.0
        elif commission_type == 'untaxed_total':
            return (rate / 100.0) * self.amount_untaxed if rate else 0.0
        return 0.0

    def _get_or_create_commission_product(self):
        """Get or create commission product for purchase orders"""
        commission_product = self.env['product.product'].search([
            ('default_code', '=', 'COMMISSION'),
            ('name', '=', 'Commission Payment')
        ], limit=1)
        
        if not commission_product:
            # Create commission product if it doesn't exist
            commission_category = self.env['product.category'].search([
                ('name', '=', 'Services')
            ], limit=1)
            
            if not commission_category:
                commission_category = self.env['product.category'].create({
                    'name': 'Services'
                })
            
            commission_product = self.env['product.product'].create({
                'name': 'Commission Payment',
                'default_code': 'COMMISSION',
                'type': 'service',
                'categ_id': commission_category.id,
                'purchase_ok': True,
                'sale_ok': False,
                'list_price': 0.0,
                'standard_price': 0.0,
            })
        
        return commission_product

    def _create_commission_purchase_order(self, partner, amount, description):
        """Create a purchase order for commission payment"""
        if not partner or not amount or amount <= 0:
            return False
            
        commission_product = self._get_or_create_commission_product()
        
        # Create purchase order
        purchase_vals = {
            'partner_id': partner.id,
            'origin': self.name,
            'origin_so_id': self.id,
            'order_line': [(0, 0, {
                'product_id': commission_product.id,
                'name': f"{description} - {self.name}",
                'product_qty': 1,
                'price_unit': amount,
                'product_uom': commission_product.uom_po_id.id,
                'date_planned': fields.Datetime.now(),
            })]
        }
        
        try:
            purchase_order = self.env['purchase.order'].create(purchase_vals)
            _logger.info(f"Created commission purchase order {purchase_order.name} for {partner.display_name} (Amount: {amount})")
            return purchase_order
        except Exception as e:
            _logger.error(f"Failed to create commission purchase order for {partner.display_name}: {e}")
            return False

    def action_generate_commission_purchase_orders(self):
        """Generate purchase orders for all commission recipients"""
        if self.commission_processed:
            raise UserError(_("Commission purchase orders have already been generated for this sale order."))

        purchase_orders = []
        # External commissions
        if self.broker_partner_id and self.broker_amount > 0:
            po = self._create_commission_purchase_order(self.broker_partner_id, self.broker_amount, "Broker Commission")
            if po:
                purchase_orders.append(po.id)
        if self.referrer_partner_id and self.referrer_amount > 0:
            po = self._create_commission_purchase_order(self.referrer_partner_id, self.referrer_amount, "Referrer Commission")
            if po:
                purchase_orders.append(po.id)
        if self.cashback_partner_id and self.cashback_amount > 0:
            po = self._create_commission_purchase_order(self.cashback_partner_id, self.cashback_amount, "Cashback Commission")
            if po:
                purchase_orders.append(po.id)
        if self.other_external_partner_id and self.other_external_amount > 0:
            po = self._create_commission_purchase_order(self.other_external_partner_id, self.other_external_amount, "Other External Commission")
            if po:
                purchase_orders.append(po.id)
        # Internal commissions
        if self.agent1_partner_id and self.agent1_amount > 0:
            po = self._create_commission_purchase_order(self.agent1_partner_id, self.agent1_amount, "Agent 1 Commission")
            if po:
                purchase_orders.append(po.id)
        if self.agent2_partner_id and self.agent2_amount > 0:
            po = self._create_commission_purchase_order(self.agent2_partner_id, self.agent2_amount, "Agent 2 Commission")
            if po:
                purchase_orders.append(po.id)
        if self.manager_partner_id and self.manager_amount > 0:
            po = self._create_commission_purchase_order(self.manager_partner_id, self.manager_amount, "Manager Commission")
            if po:
                purchase_orders.append(po.id)
        if self.director_partner_id and self.director_amount > 0:
            po = self._create_commission_purchase_order(self.director_partner_id, self.director_amount, "Director Commission")
            if po:
                purchase_orders.append(po.id)

        self.commission_processed = True
        self.commission_status = 'confirmed'
        if purchase_orders:
            self.purchase_order_ids = [(6, 0, purchase_orders)]
        _logger.info(f"Commission purchase orders generated for Sale Order {self.name}")
        return True

    def action_calculate_commissions(self):
        """Calculate commissions for this sale order."""
        # Implement commission calculation logic here
        for order in self:
            # Example: set status to calculated
            order.commission_status = 'calculated'
        return True

    def action_confirm_commissions(self):
        """Confirm calculated commissions for this sale order."""
        for order in self:
            order.commission_status = 'confirmed'
        return True

    def action_reset_commissions(self):
        """Reset commission status to draft for this sale order."""
        for order in self:
            order.commission_status = 'draft'
        return True

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sales_value = fields.Float(string='Sales Value',
        help='Snapshot of the product price at the time of order line creation, used for commission calculations.')

    @api.model
    def create(self, vals):
        if 'sales_value' not in vals:
            vals['sales_value'] = vals.get('price_unit', 0.0)
        return super().create(vals)

    def write(self, vals):
        # Optionally, prevent sales_value from being overwritten unless explicitly set
        if 'price_unit' in vals and 'sales_value' not in vals:
            for line in self:
                if not line.sales_value:
                    vals['sales_value'] = vals['price_unit']
        return super().write(vals)