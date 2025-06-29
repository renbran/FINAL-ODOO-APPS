from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ===========================================
    # COMMISSION CALCULATION TYPES
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
        compute='_compute_broker_amount',
        store=True,
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
        digits='Commission Rate',
        help="Commission rate as percentage"
    )
    
    referrer_amount = fields.Monetary(
        string="Referrer Amount", 
        currency_field='currency_id',
        compute='_compute_referrer_amount',
        store=True,
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
        compute='_compute_cashback_amount',
        store=True,
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
        digits='Commission Rate',
        help="Commission rate as percentage"
    )
    
    other_external_amount = fields.Monetary(
        string="Other External Amount", 
        currency_field='currency_id',
        compute='_compute_other_external_amount',
        store=True,
        help="Commission amount for other external party"
    )

    # Fixed amount fields for when commission type is 'fixed_amount'
    broker_fixed_amount = fields.Monetary(
        string="Broker Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for broker"
    )
    
    referrer_fixed_amount = fields.Monetary(
        string="Referrer Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for referrer"
    )
    
    cashback_fixed_amount = fields.Monetary(
        string="Cashback Fixed Amount",
        currency_field='currency_id',
        help="Fixed cashback amount"
    )
    
    other_external_fixed_amount = fields.Monetary(
        string="Other External Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for other external party"
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
        currency_field='currency_id',
        compute='_compute_agent1_amount',
        store=True,
        help="Commission amount for Agent 1"
    )
    
    agent1_fixed_amount = fields.Monetary(
        string="Agent 1 Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for Agent 1"
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
        digits='Commission Rate',
        help="Commission rate as percentage"
    )
    
    agent2_amount = fields.Monetary(
        string='Agent 2 Amount', 
        currency_field='currency_id',
        compute='_compute_agent2_amount',
        store=True,
        help="Commission amount for Agent 2"
    )
    
    agent2_fixed_amount = fields.Monetary(
        string="Agent 2 Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for Agent 2"
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
        digits='Commission Rate',
        help="Commission rate as percentage"
    )
    
    manager_amount = fields.Monetary(
        string='Manager Amount', 
        currency_field='currency_id',
        compute='_compute_manager_amount',
        store=True,
        help="Commission amount for Manager"
    )
    
    manager_fixed_amount = fields.Monetary(
        string="Manager Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for Manager"
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
        digits='Commission Rate',
        help="Commission rate as percentage"
    )
    
    director_amount = fields.Monetary(
        string='Director Amount', 
        currency_field='currency_id',
        compute='_compute_director_amount',
        store=True,
        help="Commission amount for Director"
    )
    
    director_fixed_amount = fields.Monetary(
        string="Director Fixed Amount",
        currency_field='currency_id',
        help="Fixed commission amount for Director"
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
    # INDIVIDUAL COMMISSION COMPUTE METHODS
    # ===========================================
    
    def _calculate_commission_amount(self, rate, fixed_amount, commission_type):
        """Simple commission calculation helper"""
        if commission_type == 'fixed_amount':
            return fixed_amount or 0.0
        elif commission_type == 'price_unit':
            price_unit_total = sum(line.price_unit * line.product_uom_qty for line in self.order_line)
            return (rate / 100.0) * price_unit_total
        elif commission_type == 'untaxed_total':
            return (rate / 100.0) * self.amount_untaxed
        return 0.0

    @api.depends('broker_rate', 'broker_fixed_amount', 'broker_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_broker_amount(self):
        for order in self:
            order.broker_amount = order._calculate_commission_amount(
                order.broker_rate, order.broker_fixed_amount, order.broker_commission_type
            )

    @api.depends('referrer_rate', 'referrer_fixed_amount', 'referrer_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_referrer_amount(self):
        for order in self:
            order.referrer_amount = order._calculate_commission_amount(
                order.referrer_rate, order.referrer_fixed_amount, order.referrer_commission_type
            )

    @api.depends('cashback_rate', 'cashback_fixed_amount', 'cashback_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_cashback_amount(self):
        for order in self:
            order.cashback_amount = order._calculate_commission_amount(
                order.cashback_rate, order.cashback_fixed_amount, order.cashback_commission_type
            )

    @api.depends('other_external_rate', 'other_external_fixed_amount', 'other_external_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_other_external_amount(self):
        for order in self:
            order.other_external_amount = order._calculate_commission_amount(
                order.other_external_rate, order.other_external_fixed_amount, order.other_external_commission_type
            )

    @api.depends('agent1_rate', 'agent1_fixed_amount', 'agent1_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_agent1_amount(self):
        for order in self:
            order.agent1_amount = order._calculate_commission_amount(
                order.agent1_rate, order.agent1_fixed_amount, order.agent1_commission_type
            )

    @api.depends('agent2_rate', 'agent2_fixed_amount', 'agent2_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_agent2_amount(self):
        for order in self:
            order.agent2_amount = order._calculate_commission_amount(
                order.agent2_rate, order.agent2_fixed_amount, order.agent2_commission_type
            )

    @api.depends('manager_rate', 'manager_fixed_amount', 'manager_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_manager_amount(self):
        for order in self:
            order.manager_amount = order._calculate_commission_amount(
                order.manager_rate, order.manager_fixed_amount, order.manager_commission_type
            )

    @api.depends('director_rate', 'director_fixed_amount', 'director_commission_type', 'amount_untaxed', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_director_amount(self):
        for order in self:
            order.director_amount = order._calculate_commission_amount(
                order.director_rate, order.director_fixed_amount, order.director_commission_type
            )

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)

    # ===========================================
    # MAIN COMMISSION TOTALS COMPUTE METHOD
    # ===========================================
    
    @api.depends(
        'broker_amount', 'referrer_amount', 'cashback_amount', 'other_external_amount',
        'agent1_amount', 'agent2_amount', 'manager_amount', 'director_amount',
        'amount_untaxed'
    )
    def _compute_commission_totals(self):
        """Compute all commission totals and company shares"""
        for order in self:
            # External commissions
            external_amounts = [
                order.broker_amount,
                order.referrer_amount,
                order.cashback_amount,
                order.other_external_amount
            ]
            
            # Internal commissions
            internal_amounts = [
                order.agent1_amount,
                order.agent2_amount,
                order.manager_amount,
                order.director_amount
            ]
            
            # Calculate rates for display (only for percentage-based calculations)
            external_rates = []
            internal_rates = []
            
            # External rates
            if order.broker_commission_type != 'fixed_amount':
                external_rates.append(order.broker_rate)
            if order.referrer_commission_type != 'fixed_amount':
                external_rates.append(order.referrer_rate)
            if order.cashback_commission_type != 'fixed_amount':
                external_rates.append(order.cashback_rate)
            if order.other_external_commission_type != 'fixed_amount':
                external_rates.append(order.other_external_rate)
                
            # Internal rates
            if order.agent1_commission_type != 'fixed_amount':
                internal_rates.append(order.agent1_rate)
            if order.agent2_commission_type != 'fixed_amount':
                internal_rates.append(order.agent2_rate)
            if order.manager_commission_type != 'fixed_amount':
                internal_rates.append(order.manager_rate)
            if order.director_commission_type != 'fixed_amount':
                internal_rates.append(order.director_rate)

            # Set computed values
            order.total_external_commission_rate = sum(external_rates)
            order.total_external_commission_amount = sum(external_amounts)
            order.total_internal_commission_rate = sum(internal_rates)
            order.total_internal_commission_amount = sum(internal_amounts)
            order.total_commission_rate = order.total_external_commission_rate + order.total_internal_commission_rate
            order.total_commission_amount = order.total_external_commission_amount + order.total_internal_commission_amount
            order.company_share = order.amount_untaxed - order.total_commission_amount
            order.net_company_share = order.company_share

    # ===========================================
    # HELPER METHODS
    # ===========================================
    
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
            _logger.info(f"Created commission purchase order {purchase_order.name} for {partner.name}")
            return purchase_order
        except Exception as e:
            _logger.error(f"Error creating commission purchase order: {e}")
            return False

    def generate_commission_purchase_orders(self):
        """Generate purchase orders for all commission recipients"""
        if self.commission_processed:
            raise UserError(_("Commission purchase orders have already been generated for this order."))
        
        purchase_orders = []
        commission_data = [
            (self.broker_partner_id, self.broker_amount, "Broker Commission"),
            (self.referrer_partner_id, self.referrer_amount, "Referrer Commission"),
            (self.cashback_partner_id, self.cashback_amount, "Cashback"),
            (self.other_external_partner_id, self.other_external_amount, "Other External Commission"),
            (self.agent1_partner_id, self.agent1_amount, "Agent 1 Commission"),
            (self.agent2_partner_id, self.agent2_amount, "Agent 2 Commission"),
            (self.manager_partner_id, self.manager_amount, "Manager Commission"),
            (self.director_partner_id, self.director_amount, "Director Commission"),
        ]
        
        for partner, amount, description in commission_data:
            if partner and amount > 0:
                po = self._create_commission_purchase_order(partner, amount, description)
                if po:
                    purchase_orders.append(po)
        
        if purchase_orders:
            self.commission_processed = True
            self.commission_status = 'confirmed'
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', [po.id for po in purchase_orders])],
            'context': self.env.context
        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    origin_so_id = fields.Many2one(
        'sale.order',
        string='Origin Sale Order',
        help='Sale order that generated this commission purchase order'
    )