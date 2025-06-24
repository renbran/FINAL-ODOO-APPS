# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round
import logging

_logger = logging.getLogger(__name__)

# --- Standardized Commission Type Selection ---
COMMISSION_TYPE_SELECTION = [
    ('unit_price', 'Unit Price'),
    ('untaxed', 'Untaxed Total'),
    ('fixed', 'Fixed Amount')
]

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
    
    # External Partner Commission
    external_partner_id = fields.Many2one(
        'res.partner',
        string='External Partner',
        tracking=True,
        help="External partner/agent for commission"
    )
    
    external_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION,
        string='External Commission Type',
        default='unit_price',
        tracking=True,
        help="How to compute the external partner's commission."
    )
    
    external_percentage = fields.Float(
        string='External Commission %',
        digits=(5, 2),
        tracking=True
    )
    
    external_fixed_amount = fields.Monetary(
        string='External Fixed Amount',
        currency_field='currency_id',
        tracking=True
    )
    
    external_commission_amount = fields.Monetary(
        string='External Commission Amount',
        currency_field='currency_id',
        compute='_compute_external_commission',
        store=True,
        tracking=True
    )

    # Broker/Agency Commission
    broker_agency_partner_id = fields.Many2one(
        'res.partner',
        string="Broker/Agency Partner",
        tracking=True,
        help="Select the broker or agency partner."
    )
    
    broker_agency_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Broker/Agency Calculation Type', default='unit_price'
    )
    
    broker_agency_rate = fields.Float(
        string="Broker/Agency Rate",
        tracking=True,
        digits=(5, 2)
    )
    
    broker_agency_total = fields.Monetary(
        string="Broker/Agency Total", 
        compute='_compute_commission_totals', 
        store=True,
        currency_field='currency_id',
        tracking=True
    )

    # Referral Commission
    referral_partner_id = fields.Many2one(
        'res.partner',
        string="Referral Partner",
        tracking=True,
        help="Select the referral partner."
    )
    
    referral_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Referral Calculation Type', default='unit_price'
    )
    
    referral_rate = fields.Float(
        string="Referral Rate",
        tracking=True,
        digits=(5, 2)
    )
    
    referral_total = fields.Monetary(
        string="Referral Total", 
        compute='_compute_commission_totals', 
        store=True,
        currency_field='currency_id',
        tracking=True
    )

    # Cashback Commission
    cashback_partner_id = fields.Many2one(
        'res.partner',
        string="Cashback Partner",
        tracking=True,
        help="Select the cashback recipient partner."
    )
    
    cashback_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Cashback Calculation Type', default='unit_price'
    )
    
    cashback_rate = fields.Float(
        string="Cashback Rate",
        tracking=True,
        digits=(5, 2)
    )
    
    cashback_total = fields.Monetary(
        string="Cashback Total", 
        compute='_compute_commission_totals', 
        store=True,
        currency_field='currency_id',
        tracking=True
    )

    # Other External Commission
    other_external_partner_id = fields.Many2one(
        'res.partner',
        string="Other External Partner",
        tracking=True,
        help="Select the other external commission recipient."
    )
    
    other_external_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Other External Calculation Type', default='unit_price'
    )
    
    other_external_rate = fields.Float(
        string="Other External Rate",
        tracking=True,
        digits=(5, 2)
    )
    
    other_external_total = fields.Monetary(
        string="Other External Total", 
        compute='_compute_commission_totals', 
        store=True,
        currency_field='currency_id',
        tracking=True
    )

    # ===========================================
    # INTERNAL COMMISSION FIELDS
    # ===========================================
    
    internal_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION,
        string='Internal Commission Type',
        default='unit_price',
        tracking=True,
        help="How to compute the internal commission for agents/managers/directors."
    )

    # Agent 1 Commission
    agent1_id = fields.Many2one(
        'res.partner',
        string='Agent 1',
        tracking=True,
        domain="[]",
        help="Select any partner as Agent 1 for internal commission."
    )
    
    agent1_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Agent 1 Calculation Type', default='unit_price'
    )
    
    agent1_rate = fields.Float(
        string='Agent 1 Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    
    agent1_fixed = fields.Monetary(
        string='Agent 1 Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    
    agent1_commission = fields.Monetary(
        string='Agent 1 Commission', 
        compute='_compute_commission_totals', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # Agent 2 Commission
    agent2_id = fields.Many2one(
        'res.partner',
        string='Agent 2',
        tracking=True,
        domain="[]",
        help="Select any partner as Agent 2 for internal commission."
    )
    
    agent2_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Agent 2 Calculation Type', default='unit_price'
    )
    
    agent2_rate = fields.Float(
        string='Agent 2 Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    
    agent2_fixed = fields.Monetary(
        string='Agent 2 Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    
    agent2_commission = fields.Monetary(
        string='Agent 2 Commission', 
        compute='_compute_commission_totals', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # Manager Commission
    manager_id = fields.Many2one(
        'res.partner',
        string='Manager',
        tracking=True,
        domain="[]",
        help="Select any partner as Manager for internal commission."
    )
    
    manager_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Manager Calculation Type', default='unit_price'
    )
    
    manager_rate = fields.Float(
        string='Manager Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    
    manager_fixed = fields.Monetary(
        string='Manager Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    
    manager_commission = fields.Monetary(
        string='Manager Commission', 
        compute='_compute_commission_totals', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # Director Commission
    director_id = fields.Many2one(
        'res.partner',
        string='Director',
        tracking=True,
        domain="[]",
        help="Select any partner as Director for internal commission."
    )
    
    director_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION, string='Director Calculation Type', default='unit_price'
    )
    
    director_rate = fields.Float(
        string='Director Rate (%)', 
        tracking=True, 
        digits=(5, 2)
    )
    
    director_fixed = fields.Monetary(
        string='Director Fixed Amount', 
        tracking=True, 
        currency_field='currency_id'
    )
    
    director_commission = fields.Monetary(
        string='Director Commission', 
        compute='_compute_commission_totals', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )

    # ===========================================
    # COMPUTED SUMMARY FIELDS
    # ===========================================
    
    total_internal_commission = fields.Monetary(
        string='Total Internal Commission', 
        compute='_compute_total_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )
    
    total_external_commission = fields.Monetary(
        string='Total External Commission', 
        compute='_compute_total_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )
    
    grand_total_commission = fields.Monetary(
        string='Grand Total Commission', 
        compute='_compute_total_commissions', 
        store=True, 
        tracking=True, 
        currency_field='currency_id'
    )
    
    commission_allocation_status = fields.Selection([
        ('under', 'Under Allocated'),
        ('full', 'Fully Allocated'),
        ('over', 'Over Allocated')
    ], string='Commission Allocation Status', 
       compute='_compute_allocation_status', 
       store=True,
       help="Shows if commission allocation matches the order value")

    commission_variance = fields.Monetary(
        string='Commission Variance',
        compute='_compute_allocation_status',
        store=True,
        currency_field='currency_id',
        help="Difference between total commission and order value"
    )

    commission_percentage = fields.Float(
        string='Commission %',
        compute='_compute_allocation_status',
        store=True,
        digits=(5, 2),
        help="Total commission as percentage of order value"
    )
    
    # ===========================================
    # VISIBILITY CONTROL FIELDS
    # ===========================================
    
    show_external_percentage = fields.Boolean(
        string='Show External Percentage',
        compute='_compute_visibility_fields',
        help="Control visibility of external percentage field"
    )
    
    show_external_fixed_amount = fields.Boolean(
        string='Show External Fixed Amount',
        compute='_compute_visibility_fields',
        help="Control visibility of external fixed amount field"  
    )
    
    show_agent1_rate = fields.Boolean(
        string='Show Agent 1 Rate',
        compute='_compute_visibility_fields',
        help="Control visibility of agent 1 rate field"
    )
    
    show_agent1_fixed = fields.Boolean(
        string='Show Agent 1 Fixed',
        compute='_compute_visibility_fields',
        help="Control visibility of agent 1 fixed amount field"
    )
    
    show_agent2_rate = fields.Boolean(
        string='Show Agent 2 Rate',
        compute='_compute_visibility_fields',
        help="Control visibility of agent 2 rate field"
    )
    
    show_agent2_fixed = fields.Boolean(
        string='Show Agent 2 Fixed',
        compute='_compute_visibility_fields',
        help="Control visibility of agent 2 fixed amount field"
    )
    
    show_manager_rate = fields.Boolean(
        string='Show Manager Rate',
        compute='_compute_visibility_fields',
        help="Control visibility of manager rate field"
    )
    
    show_manager_fixed = fields.Boolean(
        string='Show Manager Fixed',
        compute='_compute_visibility_fields',
        help="Control visibility of manager fixed amount field"
    )
    
    show_director_rate = fields.Boolean(
        string='Show Director Rate',
        compute='_compute_visibility_fields',
        help="Control visibility of director rate field"
    )
    
    show_director_fixed = fields.Boolean(
        string='Show Director Fixed',
        compute='_compute_visibility_fields',
        help="Control visibility of director fixed amount field"
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
    # COMPUTE METHODS
    # ===========================================
    
    @api.depends('amount_total', 'amount_untaxed')
    def _compute_sale_value(self):
        """Compute sale value based on order totals"""
        for record in self:
            if not record.sale_value:
                record.sale_value = record.amount_untaxed or record.amount_total or 0.0

    @api.depends('external_commission_type', 'external_percentage', 'external_fixed_amount', 'order_line', 'amount_untaxed')
    def _compute_external_commission(self):
        """Calculate external commission based on type and parameters"""
        for record in self:
            record.external_commission_amount = record._compute_commission_value(
                record.external_commission_type, record.external_percentage, record.external_fixed_amount
            )

    def _compute_commission_value(self, commission_type, rate, fixed_amount=0):
        """Helper method to compute commission value based on type"""
        self.ensure_one()
        if commission_type == 'unit_price':
            base = self.amount_total or 0.0
        elif commission_type == 'untaxed':
            base = self.amount_untaxed or 0.0
        elif commission_type == 'fixed':
            return fixed_amount or 0.0
        else:
            base = 0.0
        return (rate or 0.0) * base / 100

    @api.depends('order_line', 'amount_untaxed', 'amount_total',
                 'broker_agency_commission_type', 'broker_agency_rate',
                 'referral_commission_type', 'referral_rate', 
                 'cashback_commission_type', 'cashback_rate',
                 'other_external_commission_type', 'other_external_rate',
                 'agent1_commission_type', 'agent1_rate', 'agent1_fixed',
                 'agent2_commission_type', 'agent2_rate', 'agent2_fixed',
                 'manager_commission_type', 'manager_rate', 'manager_fixed',
                 'director_commission_type', 'director_rate', 'director_fixed')
    def _compute_commission_totals(self):
        """Calculate all commission totals using the correct base for each commission type"""
        for order in self:
            # External commissions
            order.broker_agency_total = order._compute_commission_value(
                order.broker_agency_commission_type, order.broker_agency_rate
            )
            order.referral_total = order._compute_commission_value(
                order.referral_commission_type, order.referral_rate
            )
            order.cashback_total = order._compute_commission_value(
                order.cashback_commission_type, order.cashback_rate
            )
            order.other_external_total = order._compute_commission_value(
                order.other_external_commission_type, order.other_external_rate
            )
            
            # Internal commissions
            order.agent1_commission = order._compute_commission_value(
                order.agent1_commission_type, order.agent1_rate, order.agent1_fixed
            )
            order.agent2_commission = order._compute_commission_value(
                order.agent2_commission_type, order.agent2_rate, order.agent2_fixed
            )
            order.manager_commission = order._compute_commission_value(
                order.manager_commission_type, order.manager_rate, order.manager_fixed
            )
            order.director_commission = order._compute_commission_value(
                order.director_commission_type, order.director_rate, order.director_fixed
            )

    @api.depends('broker_agency_total', 'referral_total', 'cashback_total', 'other_external_total', 
                 'agent1_commission', 'agent2_commission', 'manager_commission', 'director_commission')
    def _compute_total_commissions(self):
        """
        Compute the total commissions (internal + external) and set grand_total_commission.
        This method is required for button actions and field dependencies.
        """
        for order in self:
            order.total_external_commission = (
                order.broker_agency_total + order.referral_total + order.cashback_total + order.other_external_total
            )
            order.total_internal_commission = (
                order.agent1_commission + order.agent2_commission + order.manager_commission + order.director_commission
            )
            order.grand_total_commission = order.total_external_commission + order.total_internal_commission

    @api.depends('grand_total_commission', 'amount_untaxed')
    def _compute_allocation_status(self):
        """Compute allocation status comparing commission total with order value"""
        for rec in self:
            base = rec.amount_untaxed or 0.0
            commission_total = rec.grand_total_commission or 0.0
            rec.commission_variance = base - commission_total
            rec.commission_percentage = (commission_total / base * 100) if base else 0.0
            
            tolerance = 0.01
            if abs(commission_total - base) <= tolerance:
                rec.commission_allocation_status = 'full'
            elif commission_total < base - tolerance:
                rec.commission_allocation_status = 'under'
            else:
                rec.commission_allocation_status = 'over'

    def _compute_purchase_order_count(self):
        """Compute the count of purchase orders linked to this sale order"""
        for record in self:
            # This is a placeholder - implement based on your purchase order relationship
            record.purchase_order_count = 0
    
    @api.depends('external_commission_type', 'agent1_commission_type', 'agent2_commission_type', 
                 'manager_commission_type', 'director_commission_type')
    def _compute_visibility_fields(self):
        """Compute visibility fields for the UI"""
        for record in self:
            # External commission visibility
            record.show_external_percentage = record.external_commission_type in ['unit_price', 'untaxed']
            record.show_external_fixed_amount = record.external_commission_type == 'fixed'
            
            # Agent 1 visibility
            record.show_agent1_rate = record.agent1_commission_type in ['unit_price', 'untaxed']
            record.show_agent1_fixed = record.agent1_commission_type == 'fixed'
            
            # Agent 2 visibility
            record.show_agent2_rate = record.agent2_commission_type in ['unit_price', 'untaxed']
            record.show_agent2_fixed = record.agent2_commission_type == 'fixed'
            
            # Manager visibility
            record.show_manager_rate = record.manager_commission_type in ['unit_price', 'untaxed']
            record.show_manager_fixed = record.manager_commission_type == 'fixed'
            
            # Director visibility
            record.show_director_rate = record.director_commission_type in ['unit_price', 'untaxed']
            record.show_director_fixed = record.director_commission_type == 'fixed'
    
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
            record._compute_commission_totals()
            record._compute_total_commissions()
            record._compute_allocation_status()
        return True

    def action_confirm_commission(self):
        """Confirm commission calculation"""
        for record in self:
            if record.commission_status == 'draft':
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
                'title': _('Success'),                'message': _('Commission marked as paid'),
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
            # Reset calculated amounts
            record.total_external_commission = 0.0
            record.total_internal_commission = 0.0
            record.grand_total_commission = 0.0
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
            'tag': 'display_notification',            'params': {
                'title': _('Info'),
                'message': _('View related purchase orders is not yet implemented'),
                'sticky': False,
            }
        }
    
    def action_reject_commission(self):
        """Reject commission (admin only)"""
        # Check if user has admin rights
        if not (self.env.user.has_group('base.group_system') or 
                self.env.user.has_group('account.group_account_manager')):
            raise UserError(_('Only administrators can reject commissions.'))
            
        for record in self:
            if record.commission_status in ['confirmed', 'paid']:
                record.commission_status = 'canceled'
                record.commission_rejected_by = self.env.user
                record.commission_rejected_date = fields.Datetime.now()
                record.commission_notes = (record.commission_notes or '') + \
                    f"\n--- Rejected by {self.env.user.name} on {fields.Date.today()} ---"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Commission rejected successfully'),
                'sticky': False,
            }
        }
    # ===========================================
    # CONSTRAINTS
    # ===========================================
    
    _sql_constraints = [
        ('commission_percentage_positive', 
         'CHECK(external_percentage >= 0 AND external_percentage <= 100)', 
         'External commission percentage must be between 0 and 100!'),
    ]
