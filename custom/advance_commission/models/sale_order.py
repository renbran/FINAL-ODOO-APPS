# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ===========================================
    # BASIC DEAL INFORMATION
    # ===========================================
    
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="The date when the booking was made",
        index=True
    )
    
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits='Account',
        help="Commission amount for the broker"
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="The buyer associated with this sale order",
        index=True
    )
    
    deal_id = fields.Float(string='Deal ID', help="Deal ID for commission mapping.", copy=False, index=True)

    project_id = fields.Many2one(
        'product.template',
        string='Project',
        help="The project associated with this sale order",
        ondelete='set null',
        domain=[],
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        help="The specific unit associated with this sale order",
        ondelete='set null',
        domain=[],
    )

    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
        help="The total sale value of the order",
        compute='_compute_sale_value',
        store=True,
        readonly=False
    )
    
    # ===========================================
    # COMMISSION STATUS AND CONTROL
    # ===========================================
    
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
    ], string='Commission Status', default='draft', tracking=True, index=True)
    
    commission_payment_date = fields.Date(
        string='Commission Payment Date',
        tracking=True,
        copy=False
    )
    
    commission_notes = fields.Html(
        string='Commission Notes',
        tracking=True,
        help="Additional notes about commission calculations"
    )
    
    commission_reference = fields.Char(
        string='Commission Reference',
        tracking=True,
        copy=False,
        help="Reference number for commission payment"
    )
    
    commission_rejected_by = fields.Many2one(
        'res.users',
        string='Rejected By',
        readonly=True,
        copy=False,
        help="User who rejected this commission"
    )
    
    commission_rejected_date = fields.Datetime(
        string='Rejected Date',
        readonly=True,
        copy=False,
        help="Date and time when commission was rejected"
    )

    commission_sequence = fields.Char(
        string='Commission Number',
        copy=False,
        readonly=True,
        help="Auto-generated commission tracking number"
    )

    # ===========================================
    # EXTERNAL COMMISSION FIELDS
    # ===========================================
    
    # Broker/Agency Commission
    broker_agency_partner_id = fields.Many2one(
        'res.partner',
        string="Broker/Agency Partner",
        tracking=True,
        help="Select the broker or agency partner."
    )
    
    broker_agency_rate = fields.Float(
        string="Broker/Agency Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    broker_agency_amount = fields.Monetary(
        string="Broker/Agency Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # Referral Commission
    referral_partner_id = fields.Many2one(
        'res.partner',
        string="Referral Partner",
        tracking=True,
        help="Select the referral partner."
    )
    
    referral_rate = fields.Float(
        string="Referral Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    referral_amount = fields.Monetary(
        string="Referral Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # Cashback Commission
    cashback_partner_id = fields.Many2one(
        'res.partner',
        string="Cashback Partner",
        tracking=True,
        help="Select the cashback recipient partner."
    )
    
    cashback_rate = fields.Float(
        string="Cashback Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    cashback_amount = fields.Monetary(
        string="Cashback Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # Other External Commission
    other_external_partner_id = fields.Many2one(
        'res.partner',
        string="Other External Partner",
        tracking=True,
        help="Select the other external commission recipient."
    )
    
    other_external_rate = fields.Float(
        string="Other External Rate (%)",
        tracking=True,
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    other_external_amount = fields.Monetary(
        string="Other External Amount", 
        currency_field='currency_id',
        tracking=True,
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # ===========================================
    # INTERNAL COMMISSION FIELDS
    # ===========================================
    
    # Agent 1 Commission
    agent1_id = fields.Many2one(
        'res.partner',
        string='Agent 1',
        tracking=True,
        domain="[]",
        help="Select any partner as Agent 1 for internal commission."
    )
    
    agent1_rate = fields.Float(
        string='Agent 1 Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    agent1_amount = fields.Monetary(
        string='Agent 1 Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # Agent 2 Commission
    agent2_id = fields.Many2one(
        'res.partner',
        string='Agent 2',
        tracking=True,
        domain="[]",
        help="Select any partner as Agent 2 for internal commission."
    )
    
    agent2_rate = fields.Float(
        string='Agent 2 Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    agent2_amount = fields.Monetary(
        string='Agent 2 Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # Manager Commission
    manager_id = fields.Many2one(
        'res.partner',
        string='Manager',
        tracking=True,
        domain="[]",
        help="Select any partner as Manager for internal commission."
    )
    
    manager_rate = fields.Float(
        string='Manager Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if amount is entered."
    )
    
    manager_amount = fields.Monetary(
        string='Manager Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # Director Commission
    director_id = fields.Many2one(
        'res.partner',
        string='Director',
        tracking=True,
        domain="[]",
        help="Select any partner as Director for internal commission."
    )
    
    director_rate = fields.Float(
        string='Director Rate (%)', 
        tracking=True, 
        digits=(5, 2),
        help="Commission rate as percentage. Will auto-calculate if rate is entered."
    )
    
    director_amount = fields.Monetary(
        string='Director Amount', 
        tracking=True, 
        currency_field='currency_id',
        help="Fixed commission amount. Will auto-calculate if rate is entered."
    )

    # ===========================================
    # COMPUTED SUMMARY FIELDS
    # ===========================================
    
    # Gross commission base (sale value)
    gross_commission_base = fields.Monetary(
        string='Gross Commission Base',
        compute='_compute_commission_summary',
        store=True,
        readonly=True,
        currency_field='currency_id',
        help="Base amount for commission calculations (sale value)"
    )
    
    # External commission totals
    total_external_allocation = fields.Monetary(
        string='Total External Allocation', 
        compute='_compute_commission_summary', 
        store=True, 
        tracking=True, 
        currency_field='currency_id',
        help="Total of all external commission allocations"
    )
    
    # Internal commission totals  
    total_internal_allocation = fields.Monetary(
        string='Total Internal Allocation', 
        compute='_compute_commission_summary', 
        store=True, 
        tracking=True, 
        currency_field='currency_id',
        help="Total of all internal commission allocations"
    )
    
    # Company net amount
    total_company_net = fields.Monetary(
        string='Total Company Net', 
        compute='_compute_commission_summary', 
        store=True, 
        tracking=True, 
        currency_field='currency_id',
        help="Company net amount after commission allocations"
    )
    
    # Summary totals
    grand_total_commission = fields.Monetary(
        string='Grand Total Commission', 
        compute='_compute_commission_summary', 
        store=True, 
        tracking=True, 
        currency_field='currency_id',
        help="Total of all commission allocations"
    )
    
    # Status and allocation information
    commission_allocation_status = fields.Selection([
        ('under', 'Under Allocated'),
        ('full', 'Fully Allocated'),
        ('over', 'Over Allocated')
    ], string='Commission Allocation Status', 
       compute='_compute_commission_summary', 
       store=True,
       help="Shows if commission allocation matches the sale value")

    commission_variance = fields.Monetary(
        string='Commission Variance',
        compute='_compute_commission_summary',
        store=True,
        currency_field='currency_id',
        help="Difference between total commission and sale value"
    )

    commission_percentage = fields.Float(
        string='Total Commission %',
        compute='_compute_commission_summary',
        store=True,
        digits=(5, 2),
        help="Total commission as percentage of sale value"
    )
    
    # ===========================================
    # BUTTON VISIBILITY CONTROL FIELDS
    # ===========================================
    
    show_calculate_button = fields.Boolean(
        string='Show Calculate Button',
        compute='_compute_button_visibility',
        help="Control visibility of calculate commission button"
    )
    
    show_confirm_button = fields.Boolean(
        string='Show Confirm Button',
        compute='_compute_button_visibility',
        help="Control visibility of confirm commission button"
    )
    
    show_reset_button = fields.Boolean(
        string='Show Reset Button',
        compute='_compute_button_visibility',
        help="Control visibility of reset commission button"
    )
    
    show_pay_button = fields.Boolean(
        string='Show Pay Button',
        compute='_compute_button_visibility',
        help="Control visibility of mark as paid button"
    )
    
    show_reject_button = fields.Boolean(
        string='Show Reject Button',
        compute='_compute_button_visibility',
        help="Control visibility of reject button (admin only)"
    )

    # ===========================================
    # COMMISSION TYPE FIELDS
    # ===========================================
    
    broker_agency_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Broker/Agency Calculation Type', default='unit_price')
    
    referral_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Referral Calculation Type', default='unit_price')
    
    cashback_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Cashback Calculation Type', default='unit_price')
    
    other_external_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Other External Calculation Type', default='unit_price')
    
    agent1_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Agent 1 Calculation Type', default='unit_price')
    
    agent2_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Agent 2 Calculation Type', default='unit_price')
    
    manager_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Manager Calculation Type', default='unit_price')
    
    director_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('untaxed', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Director Calculation Type', default='unit_price')

    # ===========================================
    # COMPUTE METHODS
    # ===========================================
    
    @api.depends('amount_total', 'amount_untaxed')
    def _compute_sale_value(self):
        """Compute sale value based on order totals"""
        for record in self:
            if not record.sale_value:
                record.sale_value = record.amount_total or 0.0

    def _get_commission_base(self, commission_type):
        """Get the base amount for commission calculation based on type"""
        if commission_type == 'unit_price':
            # Sum of price_unit for all order lines
            return sum(self.order_line.mapped('price_unit'))
        elif commission_type == 'untaxed':
            return self.amount_untaxed or 0.0
        else:  # 'fixed' or unknown type
            return 0.0

    def _calculate_commission_amount(self, rate_field, amount_field, base_amount, type_field=None):
        """
        Helper method to calculate commission amount from rate or amount fields.
        If amount is provided, use it and calculate rate.
        If rate is provided, calculate amount.
        If both are provided, amount takes precedence.
        """
        self.ensure_one()
        commission_type = getattr(self, type_field) if type_field else 'unit_price'
        
        if commission_type == 'fixed':
            amount_value = getattr(self, amount_field, 0.0)
            rate_value = (amount_value / base_amount * 100) if base_amount else 0.0
            setattr(self, rate_field, rate_value)
            return amount_value
        else:
            base = self._get_commission_base(commission_type)
            rate_value = getattr(self, rate_field, 0.0)
            amount_value = getattr(self, amount_field, 0.0)
            
            if amount_value:
                calculated_rate = (amount_value / base * 100) if base else 0.0
                setattr(self, rate_field, calculated_rate)
                return amount_value
            elif rate_value:
                calculated_amount = (rate_value * base / 100) if base else 0.0
                setattr(self, amount_field, calculated_amount)
                return calculated_amount
            else:
                setattr(self, amount_field, 0.0)
                setattr(self, rate_field, 0.0)
                return 0.0

    @api.depends('sale_value', 'amount_total', 'amount_untaxed',
                 'broker_agency_rate', 'broker_agency_amount', 'broker_agency_commission_type',
                 'referral_rate', 'referral_amount', 'referral_commission_type',
                 'cashback_rate', 'cashback_amount', 'cashback_commission_type',
                 'other_external_rate', 'other_external_amount', 'other_external_commission_type',
                 'agent1_rate', 'agent1_amount', 'agent1_commission_type',
                 'agent2_rate', 'agent2_amount', 'agent2_commission_type',
                 'manager_rate', 'manager_amount', 'manager_commission_type',
                 'director_rate', 'director_amount', 'director_commission_type')
    def _compute_commission_summary(self):
        """Compute commission summary values including gross base and allocations"""
        for order in self:
            # Calculate gross commission base first
            order.gross_commission_base = order.sale_value or order.amount_total or 0.0
            base_amount = order.gross_commission_base

            # Calculate individual commission amounts
            broker_total = order._calculate_commission_amount('broker_agency_rate', 'broker_agency_amount', base_amount, 'broker_agency_commission_type')
            referral_total = order._calculate_commission_amount('referral_rate', 'referral_amount', base_amount, 'referral_commission_type')
            cashback_total = order._calculate_commission_amount('cashback_rate', 'cashback_amount', base_amount, 'cashback_commission_type')
            other_external_total = order._calculate_commission_amount('other_external_rate', 'other_external_amount', base_amount, 'other_external_commission_type')
            agent1_total = order._calculate_commission_amount('agent1_rate', 'agent1_amount', base_amount, 'agent1_commission_type')
            agent2_total = order._calculate_commission_amount('agent2_rate', 'agent2_amount', base_amount, 'agent2_commission_type')
            manager_total = order._calculate_commission_amount('manager_rate', 'manager_amount', base_amount, 'manager_commission_type')
            director_total = order._calculate_commission_amount('director_rate', 'director_amount', base_amount, 'director_commission_type')

            # Update commission amounts
            order.broker_agency_amount = broker_total
            order.referral_amount = referral_total
            order.cashback_amount = cashback_total
            order.other_external_amount = other_external_total
            order.agent1_amount = agent1_total
            order.agent2_amount = agent2_total
            order.manager_amount = manager_total
            order.director_amount = director_total

            # Calculate totals
            order.total_external_allocation = broker_total + referral_total + cashback_total + other_external_total
            order.total_internal_allocation = agent1_total + agent2_total + manager_total + director_total
            order.grand_total_commission = order.total_external_allocation + order.total_internal_allocation

            # Calculate company net and variance
            untaxed = order.amount_untaxed or 0.0
            if order.grand_total_commission > untaxed:
                order.grand_total_commission = untaxed
                order.total_company_net = 0.0
            else:
                order.total_company_net = untaxed - order.grand_total_commission

            # Calculate status and percentages
            tolerance = 0.01
            variance = untaxed - order.grand_total_commission
            order.commission_variance = variance
            order.commission_percentage = (order.grand_total_commission / untaxed * 100) if untaxed else 0.0

            if abs(variance) <= tolerance:
                order.commission_allocation_status = 'full'
            elif variance > tolerance:
                order.commission_allocation_status = 'under'
            else:
                order.commission_allocation_status = 'over'

    @api.depends('commission_status')
    def _compute_button_visibility(self):
        """Compute button visibility based on commission status and user permissions"""
        for record in self:
            # Check if user is admin/manager
            is_admin = self.env.user.has_group('base.group_system') or \
                      self.env.user.has_group('account.group_account_manager')
            
            # Default all buttons to False
            record.show_calculate_button = False
            record.show_confirm_button = False
            record.show_reset_button = False
            record.show_pay_button = False
            record.show_reject_button = False
            
            # Button visibility based on status
            if record.commission_status == 'draft':
                record.show_calculate_button = True
                record.show_reset_button = True
                
            elif record.commission_status == 'calculated':
                record.show_confirm_button = True
                record.show_reset_button = True
                record.show_calculate_button = True  # Allow recalculation
                
            elif record.commission_status == 'confirmed':
                record.show_pay_button = True
                record.show_reset_button = True
                if is_admin:
                    record.show_reject_button = True
                    
            elif record.commission_status in ['paid', 'canceled']:
                record.show_reset_button = True
                if is_admin:
                    record.show_reject_button = True

    # ===========================================
    # BUSINESS METHODS
    # ===========================================
    
    def calculate_commission(self):
        """Calculate and update commission values"""
        for record in self:
            # Trigger the computation of commission summary
            record._compute_commission_summary()
            record.commission_status = 'calculated'
        return True

    def action_calculate_commission(self):
        """Action to calculate commission from UI"""
        self.calculate_commission()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission calculated successfully'),
                'sticky': False,
            }
        }

    def action_confirm_commission(self):
        """Confirm commission calculation"""
        for record in self:
            if record.commission_status == 'calculated':
                record.commission_status = 'confirmed'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission confirmed successfully'),
                'sticky': False,
            }
        }
    
    def action_pay_commission(self):
        """Mark commission as paid"""
        for record in self:
            if record.commission_status in ['calculated', 'confirmed']:
                record.commission_status = 'paid'
                record.commission_payment_date = fields.Date.today()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission marked as paid'),
                'sticky': False,
            }
        }
    
    def action_reset_commission(self):
        """Reset commission to draft state"""
        for record in self:
            record.commission_status = 'draft'
            record.commission_payment_date = False
            record.commission_reference = False
            record.commission_notes = False
            record.commission_rejected_by = False
            record.commission_rejected_date = False
            # Reset all commission fields
            for f in [
                'broker_agency_rate', 'broker_agency_amount',
                'referral_rate', 'referral_amount',
                'cashback_rate', 'cashback_amount',
                'other_external_rate', 'other_external_amount',
                'agent1_rate', 'agent1_amount',
                'agent2_rate', 'agent2_amount',
                'manager_rate', 'manager_amount',
                'director_rate', 'director_amount']:
                setattr(record, f, 0.0)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission reset to draft'),
                'sticky': False,
            }
        }
    
    def action_create_commission_purchase_order(self):
        """Create a purchase order for commission payments"""
        # This is a placeholder - implement based on your business logic
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Info'),
                'message': _('Commission purchase order creation is not yet implemented'),
                'sticky': False,
            }
        }
    
    def action_view_related_purchase_orders(self):
        """View related purchase orders for commission"""
        # This is a placeholder - implement based on your business logic
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Info'),
                'message': _('View related purchase orders is not yet implemented'),
                'sticky': False,
            }
        }
    
    def action_reject_commission(self):
        """
        Reject the commission for this sale order. Sets status to 'canceled', records user and timestamp.
        Returns a client action to display a notification.
        """
        for order in self:
            order.commission_status = 'canceled'
            order.commission_rejected_by = self.env.user
            order.commission_rejected_date = fields.Datetime.now()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Commission Rejected'),
                'message': _('Commission has been rejected and marked as canceled'),
                'sticky': False,
                'type': 'warning',
            }
        }

    # ===========================================
    # CONSTRAINTS
    # ===========================================
    
    _sql_constraints = [
        ('commission_percentage_positive', 
         'CHECK(broker_agency_rate >= 0 AND broker_agency_rate <= 100 AND '
         'referral_rate >= 0 AND referral_rate <= 100 AND '
         'cashback_rate >= 0 AND cashback_rate <= 100 AND '
         'other_external_rate >= 0 AND other_external_rate <= 100 AND '
         'agent1_rate >= 0 AND agent1_rate <= 100 AND '
         'agent2_rate >= 0 AND agent2_rate <= 100 AND '
         'manager_rate >= 0 AND manager_rate <= 100 AND '
         'director_rate >= 0 AND director_rate <= 100)', 
         'All commission percentages must be between 0 and 100!'),
    ]