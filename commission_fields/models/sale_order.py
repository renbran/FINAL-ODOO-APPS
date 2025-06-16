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
    
    deal_id = fields.Char(
        string='Deal ID',
        tracking=True,
        copy=False,
        index=True,
        help="Unique identifier for the deal"
    )
    
    project_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        domain="[('detailed_type', '=', 'service'), ('can_be_expensed', '=', False)]",
        help="The project associated with this sale order",
        index=True
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
        domain="[('product_tmpl_id', '=', project_id)]",
        help="The specific unit associated with this sale order"
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
        help="Reference number for commission payment"
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
    broker_agency_name = fields.Char(
        string="Broker/Agency Name",
        tracking=True,
        help="Name of the broker or agency"
    )
    
    broker_agency_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION,
        string="Broker/Agency Commission Type",
        default='unit_price',
        tracking=True,
        help="How to compute the broker/agency commission."
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
    referral_name = fields.Char(
        string="Referral Name",
        tracking=True,
        help="Name of the referral source"
    )
    referral_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION,
        string="Referral Commission Type",
        default='unit_price',
        tracking=True,
        help="How to compute the referral commission."
    )
    referral_rate = fields.Float(
        string="Referral Commission %",
        digits=(5, 2),
        tracking=True
    )
    referral_fixed_amount = fields.Monetary(
        string="Referral Fixed Amount",
        currency_field='currency_id',
        tracking=True
    )
    referral_total = fields.Monetary(
        string="Referral Commission Amount",
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True,
        tracking=True
    )

    # Cashback Commission
    cashback_name = fields.Char(
        string="Cashback Name",
        tracking=True,
        help="Cashback recipient name"
    )
    cashback_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION,
        string="Cashback Commission Type",
        default='unit_price',
        tracking=True,
        help="How to compute the cashback commission."
    )
    cashback_rate = fields.Float(
        string="Cashback Commission %",
        digits=(5, 2),
        tracking=True
    )
    cashback_fixed_amount = fields.Monetary(
        string="Cashback Fixed Amount",
        currency_field='currency_id',
        tracking=True
    )
    cashback_total = fields.Monetary(
        string="Cashback Commission Amount",
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True,
        tracking=True
    )

    # Other External Commission
    other_external_name = fields.Char(
        string="Other External Name",
        tracking=True,
        help="Other external commission recipient"
    )
    
    other_external_commission_type = fields.Selection(
        COMMISSION_TYPE_SELECTION,
        string="Other External Commission Type",
        default='unit_price',
        tracking=True,
        help="How to compute the other external commission."
    )
    
    other_external_rate = fields.Float(
        string="Other External Commission %",
        digits=(5, 2),
        tracking=True
    )
    
    other_external_fixed_amount = fields.Monetary(
        string="Other External Fixed Amount",
        currency_field='currency_id',
        tracking=True
    )
    
    other_external_total = fields.Monetary(
        string="Other External Commission Amount",
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True,
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
        compute='_compute_internal_commissions', 
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
        compute='_compute_internal_commissions', 
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
        compute='_compute_internal_commissions', 
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
        compute='_compute_internal_commissions', 
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

    # Existing purchase order count field
    purchase_order_count = fields.Integer(
        string='Purchase Count',
        compute='_compute_purchase_order_count',
        store=False,
        help="Count of purchase orders linked to this sale order"
    )

    # ===========================================
    # COMPUTED BOOLEAN FIELDS FOR VIEW CONTROL
    # ===========================================
    
    show_external_percentage = fields.Boolean(
        compute='_compute_show_external_percentage',
        store=False
    )
    show_external_fixed_amount = fields.Boolean(
        compute='_compute_show_external_fixed_amount',
        store=False
    )
    show_agent1_rate = fields.Boolean(
        compute='_compute_show_agent1_rate',
        store=False
    )
    show_agent1_fixed = fields.Boolean(
        compute='_compute_show_agent1_fixed',
        store=False
    )
    show_agent2_rate = fields.Boolean(
        compute='_compute_show_agent2_rate',
        store=False
    )
    show_agent2_fixed = fields.Boolean(
        compute='_compute_show_agent2_fixed',
        store=False
    )
    show_manager_rate = fields.Boolean(
        compute='_compute_show_manager_rate',
        store=False
    )
    show_manager_fixed = fields.Boolean(
        compute='_compute_show_manager_fixed',
        store=False
    )
    show_director_rate = fields.Boolean(
        compute='_compute_show_director_rate',
        store=False
    )
    show_director_fixed = fields.Boolean(
        compute='_compute_show_director_fixed',
        store=False
    )

    @api.depends('external_commission_type')
    def _compute_show_external_percentage(self):
        for rec in self:
            rec.show_external_percentage = rec.external_commission_type != 'fixed'

    @api.depends('external_commission_type')
    def _compute_show_external_fixed_amount(self):
        for rec in self:
            rec.show_external_fixed_amount = rec.external_commission_type == 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_agent1_rate(self):
        for rec in self:
            rec.show_agent1_rate = rec.internal_commission_type != 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_agent1_fixed(self):
        for rec in self:
            rec.show_agent1_fixed = rec.internal_commission_type == 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_agent2_rate(self):
        for rec in self:
            rec.show_agent2_rate = rec.internal_commission_type != 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_agent2_fixed(self):
        for rec in self:
            rec.show_agent2_fixed = rec.internal_commission_type == 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_manager_rate(self):
        for rec in self:
            rec.show_manager_rate = rec.internal_commission_type != 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_manager_fixed(self):
        for rec in self:
            rec.show_manager_fixed = rec.internal_commission_type == 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_director_rate(self):
        for rec in self:
            rec.show_director_rate = rec.internal_commission_type != 'fixed'

    @api.depends('internal_commission_type')
    def _compute_show_director_fixed(self):
        for rec in self:
            rec.show_director_fixed = rec.internal_commission_type == 'fixed'

    # ===========================================
    # CONSTRAINTS
    # ===========================================
    
    _sql_constraints = [
        ('deal_id_unique', 'UNIQUE(deal_id)', 'Deal ID must be unique across all sale orders!'),
        ('commission_percentage_positive', 
         'CHECK(external_percentage >= 0 AND external_percentage <= 100)', 
         'External commission percentage must be between 0 and 100!'),
    ]

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
            record.external_commission_amount = record._compute_commission_amount(
                record.external_commission_type, record.external_percentage, record.external_fixed_amount
            )

    @api.depends('order_line', 'amount_untaxed', 'broker_agency_commission_type', 'broker_agency_rate', 'broker_agency_total')
    def _compute_commission_totals(self):
        """Calculate all external commission totals"""
        for order in self:
            order.broker_agency_total = order._compute_commission_amount(
                order.broker_agency_commission_type, order.broker_agency_rate
            )
            order.referral_total = order._compute_commission_amount(
                order.referral_commission_type, order.referral_rate
            )
            order.cashback_total = order._compute_commission_amount(
                order.cashback_commission_type, order.cashback_rate
            )
            order.other_external_total = order._compute_commission_amount(
                order.other_external_commission_type, order.other_external_rate
            )

    @api.depends('order_line', 'amount_untaxed', 'internal_commission_type', 'agent1_rate', 'agent1_fixed', 'agent2_rate', 'agent2_fixed', 'manager_rate', 'manager_fixed', 'director_rate', 'director_fixed')
    def _compute_internal_commissions(self):
        """Calculate internal commission amounts"""
        for record in self:
            if record.internal_commission_type == 'unit_price':
                base = sum(line.price_unit for line in record.order_line)
                record.agent1_commission = (base * (record.agent1_rate or 0) / 100)
                record.agent2_commission = (base * (record.agent2_rate or 0) / 100)
                record.manager_commission = (base * (record.manager_rate or 0) / 100)
                record.director_commission = (base * (record.director_rate or 0) / 100)
            elif record.internal_commission_type == 'untaxed':
                base = record.amount_untaxed or 0.0
                record.agent1_commission = (base * (record.agent1_rate or 0) / 100)
                record.agent2_commission = (base * (record.agent2_rate or 0) / 100)
                record.manager_commission = (base * (record.manager_rate or 0) / 100)
                record.director_commission = (base * (record.director_rate or 0) / 100)
            elif record.internal_commission_type == 'fixed':
                record.agent1_commission = record.agent1_fixed or 0.0
                record.agent2_commission = record.agent2_fixed or 0.0
                record.manager_commission = record.manager_fixed or 0.0
                record.director_commission = record.director_fixed or 0.0

    @api.depends('agent1_commission', 'agent2_commission', 'manager_commission', 'director_commission',
                 'external_commission_amount', 'broker_agency_total', 'referral_total', 
                 'cashback_total', 'other_external_total')
    def _compute_total_commissions(self):
        """Calculate total commission amounts"""
        for record in self:
            # Internal commission total
            record.total_internal_commission = sum([
                record.agent1_commission or 0.0,
                record.agent2_commission or 0.0,
                record.manager_commission or 0.0,
                record.director_commission or 0.0
            ])
            
            # External commission total
            record.total_external_commission = sum([
                record.external_commission_amount or 0.0,
                record.broker_agency_total or 0.0,
                record.referral_total or 0.0,
                record.cashback_total or 0.0,
                record.other_external_total or 0.0
            ])
            
            # Grand total
            record.grand_total_commission = record.total_internal_commission + record.total_external_commission

    @api.depends('grand_total_commission', 'amount_total', 'sale_value')
    def _compute_allocation_status(self):
        """Determine commission allocation status and calculate variance based on untaxed amount (excluding tax)"""
        for record in self:
            # Use amount_untaxed as the base for commission allocation, not amount_total (which includes tax)
            base_amount = record.amount_untaxed or 0.0
            commission_total = record.grand_total_commission or 0.0
            
            # Calculate variance
            record.commission_variance = commission_total - base_amount
            
            # Calculate percentage
            if base_amount > 0:
                record.commission_percentage = (commission_total / base_amount) * 100
            else:
                record.commission_percentage = 0.0
            
            # Determine status with tolerance
            tolerance = 0.01  # 1 cent tolerance
            if float_compare(commission_total, base_amount, precision_digits=2) == 0:
                record.commission_allocation_status = 'full'
            elif commission_total < base_amount - tolerance:
                record.commission_allocation_status = 'under'
            elif commission_total > base_amount + tolerance:
                record.commission_allocation_status = 'over'
            else:
                record.commission_allocation_status = 'full'

    def _compute_purchase_order_count(self):
        """Count related purchase orders"""
        for order in self:
            order.purchase_order_count = self.env['purchase.order'].search_count([
                ('origin', '=', order.name)
            ])

    # ===========================================
    # HELPER METHODS
    # ===========================================
    
    def _compute_commission_amount(self, commission_type, rate, fixed_amount=0.0):
        """Calculate commission amount based on type and rate"""
        self.ensure_one()
        if commission_type == 'unit_price':
            base = sum(line.price_unit for line in self.order_line)
            return float_round((base * rate) / 100, precision_digits=2) if rate else 0.0
        elif commission_type == 'untaxed':
            base = self.amount_untaxed or 0.0
            return float_round((base * rate) / 100, precision_digits=2) if rate else 0.0
        elif commission_type == 'fixed':
            return fixed_amount or 0.0
        return 0.0

    def _generate_commission_sequence(self):
        """Generate commission tracking sequence"""
        if not self.commission_sequence:
            sequence = self.env['ir.sequence'].next_by_code('commission.sequence') or '/'
            self.commission_sequence = sequence

    # ===========================================
    # VALIDATION AND CONSTRAINTS
    # ===========================================
    
    @api.constrains('developer_commission')
    def _check_developer_commission(self):
        """Validate developer commission amount"""
        for order in self:
            if order.developer_commission < 0:
                raise ValidationError(_("Developer commission cannot be negative!"))
    @api.constrains('agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _check_commission_rates(self):
        """Validate internal commission rates"""
        for order in self:
            if order.internal_commission_type == 'sale_percentage':
                for rate in [order.agent1_rate, order.agent2_rate, order.manager_rate, order.director_rate]:
                    if rate and (rate < 0 or rate > 100):
                        raise ValidationError(_("Commission rates must be between 0 and 100 when using percentage type!"))
            elif order.internal_commission_type == 'total_percentage':
                total_rate = sum([
                    order.agent1_rate or 0,
                    order.agent2_rate or 0,
                    order.manager_rate or 0,
                    order.director_rate or 0
                ])
                if total_rate > 100:
                    raise ValidationError(_("Total commission rate cannot exceed 100% when using total percentage type!"))

    # ===========================================
    # ACTION METHODS
    # ===========================================

    def action_confirm_commission(self):
        """Confirm commission calculations"""
        for order in self:
            if order.commission_status != 'calculated':
                raise UserError(_("Commission must be in 'Calculated' state before confirmation!"))
            
            if order.commission_allocation_status == 'over':
                raise UserError(_("Cannot confirm commission with over allocation!"))
            
            order._generate_commission_sequence()
            order.commission_status = 'confirmed'
            order.message_post(body=_("Commission confirmed by %s") % self.env.user.name)

    def action_pay_commission(self):
        """Mark commission as paid"""
        for order in self:
            if order.commission_status != 'confirmed':
                raise UserError(_("Commission must be confirmed before marking as paid!"))
            
            order.commission_status = 'paid'
            order.commission_payment_date = fields.Date.today()
            order.message_post(body=_("Commission marked as paid by %s") % self.env.user.name)

    def action_calculate_commission(self):
        """Calculate commission amounts"""
        for order in self:
            # Recompute all commission fields
            order._compute_external_commission()
            order._compute_commission_totals()
            order._compute_internal_commissions()
            order._compute_total_commissions()
            order._compute_allocation_status()
            
            order.commission_status = 'calculated'
            order.message_post(body=_("Commission recalculated by %s") % self.env.user.name)

    def action_reset_commission(self):
        """Reset commission to draft state"""
        for order in self:
            if order.commission_status == 'paid':
                raise UserError(_("Cannot reset paid commissions!"))
            
            order.commission_status = 'draft'
            order.message_post(body=_("Commission reset to draft by %s") % self.env.user.name)

    def action_view_related_purchase_orders(self):
        """View purchase orders linked to this sale order"""
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('purchase.purchase_form_action')
        purchases = self.env['purchase.order'].search([('origin', '=', self.name)])
        
        if len(purchases) == 1:
            action['res_id'] = purchases.id
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        else:
            action['domain'] = [('id', 'in', purchases.ids)]
            action['context'] = {}
        
        return action

    def action_view_commission_invoices(self):
        """View all invoices related to this sale order's commission"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('deal_id', '=', self.id)],
            'context': {'default_deal_id': self.id},
        }

    def action_create_commission_purchase_order(self):
        """Create purchase orders for all commission recipients with non-zero commission amounts."""
        PurchaseOrder = self.env['purchase.order']
        created_pos = []
        commission_product = self.env['product.product'].search([('name', '=', 'Commission Fee')], limit=1)
        if not commission_product:
            commission_product = self.env['product.product'].create({
                'name': 'Commission Fee',
                'type': 'service',
                'purchase_ok': True,
                'sale_ok': False,
            })
        for order in self:
            if order.commission_status not in ['confirmed', 'paid']:
                raise UserError(_('Commission must be confirmed or paid before creating a purchase order.'))
            if not order.invoice_ids or not any(inv.state in ['posted', 'paid'] for inv in order.invoice_ids):
                raise UserError(_('You must have at least one processed invoice (posted/paid) before creating a commission purchase order.'))

            # Prepare all commission recipients and amounts
            commission_lines = []
            # Internal
            if order.agent1_id and order.agent1_commission > 0:
                commission_lines.append({
                    'partner': order.agent1_id,
                    'name': _('Agent 1 Commission for Sale Order %s') % order.name,
                    'amount': order.agent1_commission
                })
            if order.agent2_id and order.agent2_commission > 0:
                commission_lines.append({
                    'partner': order.agent2_id,
                    'name': _('Agent 2 Commission for Sale Order %s') % order.name,
                    'amount': order.agent2_commission
                })
            if order.manager_id and order.manager_commission > 0:
                commission_lines.append({
                    'partner': order.manager_id,
                    'name': _('Manager Commission for Sale Order %s') % order.name,
                    'amount': order.manager_commission
                })
            if order.director_id and order.director_commission > 0:
                commission_lines.append({
                    'partner': order.director_id,
                    'name': _('Director Commission for Sale Order %s') % order.name,
                    'amount': order.director_commission
                })
            # External
            if order.external_partner_id and order.external_commission_amount > 0:
                commission_lines.append({
                    'partner': order.external_partner_id,
                    'name': _('External Partner Commission for Sale Order %s') % order.name,
                    'amount': order.external_commission_amount
                })
            if order.broker_agency_name and order.broker_agency_total > 0:
                broker_partner = order.broker_agency_partner_id if hasattr(order, 'broker_agency_partner_id') and order.broker_agency_partner_id else False
                commission_lines.append({
                    'partner': broker_partner or order.partner_id,  # fallback to order partner
                    'name': _('Broker/Agency Commission for Sale Order %s (%s)') % (order.name, order.broker_agency_name),
                    'amount': order.broker_agency_total
                })
            if order.referral_name and order.referral_total > 0:
                referral_partner = order.referral_partner_id if hasattr(order, 'referral_partner_id') and order.referral_partner_id else False
                commission_lines.append({
                    'partner': referral_partner or order.partner_id,
                    'name': _('Referral Commission for Sale Order %s (%s)') % (order.name, order.referral_name),
                    'amount': order.referral_total
                })
            if order.cashback_name and order.cashback_total > 0:
                cashback_partner = order.cashback_partner_id if hasattr(order, 'cashback_partner_id') and order.cashback_partner_id else False
                commission_lines.append({
                    'partner': cashback_partner or order.partner_id,
                    'name': _('Cashback for Sale Order %s (%s)') % (order.name, order.cashback_name),
                    'amount': order.cashback_total
                })
            if order.other_external_name and order.other_external_total > 0:
                other_partner = order.other_external_partner_id if hasattr(order, 'other_external_partner_id') and order.other_external_partner_id else False
                commission_lines.append({
                    'partner': other_partner or order.partner_id,
                    'name': _('Other External Commission for Sale Order %s (%s)') % (order.name, order.other_external_name),
                    'amount': order.other_external_total
                })

            if not commission_lines:
                raise UserError(_('No commission recipients with non-zero commission found.'))

            # Group lines by partner (one PO per partner)
            partner_map = {}
            for line in commission_lines:
                partner = line['partner']
                if not partner:
                    continue
                if partner not in partner_map:
                    partner_map[partner] = []
                partner_map[partner].append(line)

            for partner, lines in partner_map.items():
                po_lines = []
                for l in lines:
                    po_lines.append((0, 0, {
                        'name': l['name'],
                        'product_qty': 1,
                        'product_uom': commission_product.uom_id.id,
                        'price_unit': l['amount'],
                        'date_planned': fields.Date.today(),
                        'product_id': commission_product.id,
                    }))
                po_vals = {
                    'partner_id': partner.id,
                    'origin': order.name,
                    'commission_sale_order_id': order.id,
                    'order_line': po_lines,
                }
                po = PurchaseOrder.create(po_vals)
                created_pos.append(po.id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': created_pos[0] if len(created_pos) == 1 else False,
            'domain': [('id', 'in', created_pos)],
        }

    # ===========================================
    # ONCHANGE METHODS
    # ===========================================

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Reset unit when project changes"""
        if self.project_id:
            return {'domain': {'unit_id': [('product_tmpl_id', '=', self.project_id.id)]}}
        else:
            self.unit_id = False
            return {'domain': {'unit_id': []}}

    @api.onchange('internal_commission_type')
    def _onchange_internal_commission_type(self):
        """Reset rates when commission type changes"""
        if self.internal_commission_type == 'fixed':
            self.agent1_rate = 0
            self.agent2_rate = 0
            self.manager_rate = 0
            self.director_rate = 0
        else:
            self.agent1_fixed = 0
            self.agent2_fixed = 0
            self.manager_fixed = 0
            self.director_fixed = 0

    # ===========================================
    # OVERRIDES
    # ===========================================

    def action_confirm(self):
        """Override confirm to ensure commission validation"""
        for order in self:
            if order.commission_status == 'draft' and order.grand_total_commission > 0:
                raise UserError(_("Please calculate commissions before confirming the order!"))
        
        # Corrected super() usage to avoid recursion
        return super().action_confirm()

    def write(self, vals):
        """Prevent modifications to certain fields after confirmation"""
        protected_fields = [
            'sale_value', 'developer_commission', 'commission_status',
            'external_commission_amount', 'broker_agency_total',
            'referral_total', 'cashback_total', 'other_external_total',
            'agent1_commission', 'agent2_commission', 
            'manager_commission', 'director_commission'
        ]
        
        if any(field in vals for field in protected_fields):
            for order in self:
                if order.state not in ['draft', 'sent'] and order.commission_status in ['confirmed', 'paid']:
                    raise UserError(_("Cannot modify commission details after order confirmation when commission is confirmed or paid!"))
        
        return super().write(vals)  # FIX: use super() instead of super(SaleOrder, self)

    def copy(self, default=None):
        """Handle copying of commission-related fields"""
        default = dict(default or {})
        default.update({
            'commission_status': 'draft',
            'commission_sequence': False,
            'commission_payment_date': False,
            'commission_reference': False,
        })
        return super(SaleOrder, self).copy(default)

    # ===========================================
    # REPORTING METHODS
    # ===========================================

    def get_commission_summary(self):
        """Return commission data for reporting"""
        self.ensure_one()
        return {
            'internal': {
                'agent1': {
                    'name': self.agent1_id.name if self.agent1_id else 'N/A',
                    'rate': self.agent1_rate,
                    'amount': self.agent1_commission
                },
                'agent2': {
                    'name': self.agent2_id.name if self.agent2_id else 'N/A',
                    'rate': self.agent2_rate,
                    'amount': self.agent2_commission
                },
                'manager': {
                    'name': self.manager_id.name if self.manager_id else 'N/A',
                    'rate': self.manager_rate,
                    'amount': self.manager_commission
                },
                'director': {
                    'name': self.director_id.name if self.director_id else 'N/A',
                    'rate': self.director_rate,
                    'amount': self.director_commission
                },
                'total': self.total_internal_commission
            },
            'external': {
                'partner': {
                    'name': self.external_partner_id.name if self.external_partner_id else 'N/A',
                    'amount': self.external_commission_amount
                },
                'broker': {
                    'name': self.broker_agency_name or 'N/A',
                    'amount': self.broker_agency_total
                },
                'referral': {
                    'name': self.referral_name or 'N/A',
                    'amount': self.referral_total
                },
                'cashback': {
                    'name': self.cashback_name or 'N/A',
                    'amount': self.cashback_total
                },
                'other': {
                    'name': self.other_external_name or 'N/A',
                    'amount': self.other_external_total
                },
                'total': self.total_external_commission
            },
            'grand_total': self.grand_total_commission,
            'status': self.commission_status,
            'variance': self.commission_variance,
            'percentage': self.commission_percentage
        }

# Patch purchase.order to add a link to sale.order
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    commission_sale_order_id = fields.Many2one('sale.order', string='Commission Sale Order', index=True, help='The sale order that generated this commission purchase order.')

# Add a One2many on sale.order for navigation
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    commission_purchase_order_ids = fields.One2many('purchase.order', 'commission_sale_order_id', string='Commission Purchase Orders')

    def action_create_commission_purchase_order(self):
        """Create purchase orders for all commission recipients with non-zero commission amounts."""
        PurchaseOrder = self.env['purchase.order']
        created_pos = []
        commission_product = self.env['product.product'].search([('name', '=', 'Commission Fee')], limit=1)
        if not commission_product:
            commission_product = self.env['product.product'].create({
                'name': 'Commission Fee',
                'type': 'service',
                'purchase_ok': True,
                'sale_ok': False,
            })
        for order in self:
            if order.commission_status not in ['confirmed', 'paid']:
                raise UserError(_('Commission must be confirmed or paid before creating a purchase order.'))
            if not order.invoice_ids or not any(inv.state in ['posted', 'paid'] for inv in order.invoice_ids):
                raise UserError(_('You must have at least one processed invoice (posted/paid) before creating a commission purchase order.'))

            # Prepare all commission recipients and amounts
            commission_lines = []
            # Internal
            if order.agent1_id and order.agent1_commission > 0:
                commission_lines.append({
                    'partner': order.agent1_id,
                    'name': _('Agent 1 Commission for Sale Order %s') % order.name,
                    'amount': order.agent1_commission
                })
            if order.agent2_id and order.agent2_commission > 0:
                commission_lines.append({
                    'partner': order.agent2_id,
                    'name': _('Agent 2 Commission for Sale Order %s') % order.name,
                    'amount': order.agent2_commission
                })
            if order.manager_id and order.manager_commission > 0:
                commission_lines.append({
                    'partner': order.manager_id,
                    'name': _('Manager Commission for Sale Order %s') % order.name,
                    'amount': order.manager_commission
                })
            if order.director_id and order.director_commission > 0:
                commission_lines.append({
                    'partner': order.director_id,
                    'name': _('Director Commission for Sale Order %s') % order.name,
                    'amount': order.director_commission
                })
            # External
            if order.external_partner_id and order.external_commission_amount > 0:
                commission_lines.append({
                    'partner': order.external_partner_id,
                    'name': _('External Partner Commission for Sale Order %s') % order.name,
                    'amount': order.external_commission_amount
                })
            if order.broker_agency_name and order.broker_agency_total > 0:
                broker_partner = order.broker_agency_partner_id if hasattr(order, 'broker_agency_partner_id') and order.broker_agency_partner_id else False
                commission_lines.append({
                    'partner': broker_partner or order.partner_id,  # fallback to order partner
                    'name': _('Broker/Agency Commission for Sale Order %s (%s)') % (order.name, order.broker_agency_name),
                    'amount': order.broker_agency_total
                })
            if order.referral_name and order.referral_total > 0:
                referral_partner = order.referral_partner_id if hasattr(order, 'referral_partner_id') and order.referral_partner_id else False
                commission_lines.append({
                    'partner': referral_partner or order.partner_id,
                    'name': _('Referral Commission for Sale Order %s (%s)') % (order.name, order.referral_name),
                    'amount': order.referral_total
                })
            if order.cashback_name and order.cashback_total > 0:
                cashback_partner = order.cashback_partner_id if hasattr(order, 'cashback_partner_id') and order.cashback_partner_id else False
                commission_lines.append({
                    'partner': cashback_partner or order.partner_id,
                    'name': _('Cashback for Sale Order %s (%s)') % (order.name, order.cashback_name),
                    'amount': order.cashback_total
                })
            if order.other_external_name and order.other_external_total > 0:
                other_partner = order.other_external_partner_id if hasattr(order, 'other_external_partner_id') and order.other_external_partner_id else False
                commission_lines.append({
                    'partner': other_partner or order.partner_id,
                    'name': _('Other External Commission for Sale Order %s (%s)') % (order.name, order.other_external_name),
                    'amount': order.other_external_total
                })

            if not commission_lines:
                raise UserError(_('No commission recipients with non-zero commission found.'))

            # Group lines by partner (one PO per partner)
            partner_map = {}
            for line in commission_lines:
                partner = line['partner']
                if not partner:
                    continue
                if partner not in partner_map:
                    partner_map[partner] = []
                partner_map[partner].append(line)

            for partner, lines in partner_map.items():
                po_lines = []
                for l in lines:
                    po_lines.append((0, 0, {
                        'name': l['name'],
                        'product_qty': 1,
                        'product_uom': commission_product.uom_id.id,
                        'price_unit': l['amount'],
                        'date_planned': fields.Date.today(),
                        'product_id': commission_product.id,
                    }))
                po_vals = {
                    'partner_id': partner.id,
                    'origin': order.name,
                    'commission_sale_order_id': order.id,
                    'order_line': po_lines,
                }
                po = PurchaseOrder.create(po_vals)
                created_pos.append(po.id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': created_pos[0] if len(created_pos) == 1 else False,
            'domain': [('id', 'in', created_pos)],
        }

    # ===========================================
    # HELPER METHODS
    # ===========================================

    @api.model
    def search_by_deal_id(self, deal_id_str):
        """Search sale.order by deal_id string."""
        return self.search([('deal_id', '=', deal_id_str)])
