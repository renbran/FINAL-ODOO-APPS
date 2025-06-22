from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # External Commission Fields
    external_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('price_unit', 'Price Unit'),
        ('untaxed_total', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='External Commission Type', default='untaxed_total')

    # Broker Subgroup
    broker_partner_id = fields.Many2one('res.partner', string='Broker')
    broker_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('price_unit', 'Price Unit'),
        ('untaxed_total', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Broker Commission Type', default='unit_price')
    broker_rate = fields.Float(string='Broker Rate (%)', digits=(5, 2))
    broker_commission_amount = fields.Monetary(
        string='Broker Commission',
        compute='_compute_broker_commission',
        store=True
    )

    # Referral Subgroup
    referral_partner_id = fields.Many2one('res.partner', string='Referral')
    referral_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('price_unit', 'Price Unit'),
        ('untaxed_total', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Referral Commission Type', default='price_unit')
    referral_rate = fields.Float(string='Referral Rate (%)', digits=(5, 2))
    referral_commission_amount = fields.Monetary(
        string='Referral Commission',
        compute='_compute_referral_commission',
        store=True
    )

    # Cashback Subgroup
    cashback_partner_id = fields.Many2one('res.partner', string='Cashback')
    cashback_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('price_unit', 'Price Unit'),
        ('untaxed_total', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Cashback Commission Type', default='untaxed_total')
    cashback_rate = fields.Float(string='Cashback Rate (%)', digits=(5, 2))
    cashback_commission_amount = fields.Monetary(
        string='Cashback Commission',
        compute='_compute_cashback_commission',
        store=True
    )

    # Others Subgroup
    other_partner_id = fields.Many2one('res.partner', string='Other')
    other_commission_type = fields.Selection([
        ('unit_price', 'Unit Price'),
        ('price_unit', 'Price Unit'),
        ('untaxed_total', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Other Commission Type', default='fixed')
    other_rate = fields.Float(string='Other Rate (%)', digits=(5, 2))
    other_fixed_amount = fields.Monetary(string='Other Fixed Amount')
    other_commission_amount = fields.Monetary(
        string='Other Commission',
        compute='_compute_other_commission',
        store=True
    )

    # Internal Commission Fields
    internal_commission_type = fields.Selection([
        ('untaxed_total', 'Untaxed Total'),
        ('fixed', 'Fixed Amount')
    ], string='Internal Commission Type', default='untaxed_total')

    # Agent 1 Subgroup
    agent1_id = fields.Many2one('hr.employee', string='Agent 1')
    agent1_rate = fields.Float(string='Agent 1 Rate (%)', digits=(5, 2))
    agent1_fixed_amount = fields.Monetary(string='Agent 1 Fixed Amount')
    agent1_commission_amount = fields.Monetary(
        string='Agent 1 Commission',
        compute='_compute_agent1_commission',
        store=True
    )

    # Agent 2 Subgroup
    agent2_id = fields.Many2one('hr.employee', string='Agent 2')
    agent2_rate = fields.Float(string='Agent 2 Rate (%)', digits=(5, 2))
    agent2_fixed_amount = fields.Monetary(string='Agent 2 Fixed Amount')
    agent2_commission_amount = fields.Monetary(
        string='Agent 2 Commission',
        compute='_compute_agent2_commission',
        store=True
    )

    # Manager Subgroup
    manager_id = fields.Many2one('hr.employee', string='Manager')
    manager_rate = fields.Float(string='Manager Rate (%)', digits=(5, 2))
    manager_fixed_amount = fields.Monetary(string='Manager Fixed Amount')
    manager_commission_amount = fields.Monetary(
        string='Manager Commission',
        compute='_compute_manager_commission',
        store=True
    )

    # Director Subgroup
    director_id = fields.Many2one('hr.employee', string='Director')
    director_rate = fields.Float(string='Director Rate (%)', digits=(5, 2))
    director_fixed_amount = fields.Monetary(string='Director Fixed Amount')
    director_commission_amount = fields.Monetary(
        string='Director Commission',
        compute='_compute_director_commission',
        store=True
    )

    # Commission Workflow Fields
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid')
    ], string='Commission Status', default='draft', tracking=True)
    commission_payment_date = fields.Date(string='Commission Payment Date', tracking=True)
    commission_reference = fields.Char(string='Commission Reference', tracking=True)
    commission_notes = fields.Html(string='Commission Notes', tracking=True)
    commission_allocation_status = fields.Selection([
        ('under', 'Under Allocated'),
        ('full', 'Fully Allocated'),
        ('over', 'Over Allocated')
    ], string='Allocation Status', compute='_compute_allocation_status', store=True)
    commission_percentage = fields.Float(string='Commission %', compute='_compute_allocation_status', store=True)
    internal_commission_base = fields.Monetary(string='Internal Commission Base', compute='_compute_internal_commission_base', store=True, currency_field='currency_id')

    # Summary Fields
    total_external_commission = fields.Monetary(
        string='Total External',
        compute='_compute_total_commissions',
        store=True
    )
    total_internal_commission = fields.Monetary(
        string='Total Internal',
        compute='_compute_total_commissions',
        store=True
    )
    total_payable = fields.Monetary(
        string='Total Payable',
        compute='_compute_total_commissions',
        store=True
    )
    company_net_commission = fields.Monetary(
        string='Company Net Commission',
        compute='_compute_company_net_commission',
        store=True
    )
    remaining_unallocated_amount = fields.Monetary(
        string='Remaining Unallocated Amount',
        compute='_compute_remaining_unallocated',
        store=True
    )

    # Button and field visibility logic
    can_calculate_commission = fields.Boolean(compute='_compute_commission_button_visibility', store=False)
    can_confirm_commission = fields.Boolean(compute='_compute_commission_button_visibility', store=False)
    can_pay_commission = fields.Boolean(compute='_compute_commission_button_visibility', store=False)
    can_reset_commission = fields.Boolean(compute='_compute_commission_button_visibility', store=False)

    @api.depends('commission_status')
    def _compute_commission_button_visibility(self):
        for rec in self:
            rec.can_calculate_commission = rec.commission_status == 'draft'
            rec.can_confirm_commission = rec.commission_status == 'calculated'
            rec.can_pay_commission = rec.commission_status == 'confirmed'
            rec.can_reset_commission = rec.commission_status != 'paid'

    @api.depends('amount_untaxed', 'total_external_commission')
    def _compute_internal_commission_base(self):
        for rec in self:
            rec.internal_commission_base = max((rec.amount_untaxed or 0.0) - (rec.total_external_commission or 0.0), 0.0)

    @api.depends('total_external_commission', 'total_internal_commission', 'amount_untaxed')
    def _compute_allocation_status(self):
        for rec in self:
            base_amount = rec.amount_untaxed or 0.0
            commission_total = (rec.total_external_commission or 0.0) + (rec.total_internal_commission or 0.0)
            rec.commission_percentage = (commission_total / base_amount) * 100 if base_amount > 0 else 0.0
            tolerance = 0.01
            if abs(commission_total - base_amount) < tolerance:
                rec.commission_allocation_status = 'full'
            elif commission_total < base_amount - tolerance:
                rec.commission_allocation_status = 'under'
            elif commission_total > base_amount + tolerance:
                rec.commission_allocation_status = 'over'
            else:
                rec.commission_allocation_status = 'full'

    # Computation Methods
    @api.depends('order_line.price_unit', 'broker_rate', 'broker_commission_type')
    def _compute_broker_commission(self):
        for order in self:
            if order.broker_commission_type == 'unit_price':
                base = order.order_line[0].price_unit if order.order_line else 0.0
                order.broker_commission_amount = (base * order.broker_rate) / 100
            elif order.broker_commission_type == 'price_unit':
                base = sum(line.price_unit * line.product_uom_qty for line in order.order_line)
                order.broker_commission_amount = (base * order.broker_rate) / 100
            elif order.broker_commission_type == 'untaxed_total':
                order.broker_commission_amount = (order.amount_untaxed * order.broker_rate) / 100
            else:
                order.broker_commission_amount = 0.0

    @api.depends('order_line.price_unit', 'referral_rate', 'referral_commission_type')
    def _compute_referral_commission(self):
        for order in self:
            if order.referral_commission_type == 'unit_price':
                base = order.order_line[0].price_unit if order.order_line else 0.0
                order.referral_commission_amount = (base * order.referral_rate) / 100
            elif order.referral_commission_type == 'price_unit':
                base = sum(line.price_unit * line.product_uom_qty for line in order.order_line)
                order.referral_commission_amount = (base * order.referral_rate) / 100
            elif order.referral_commission_type == 'untaxed_total':
                order.referral_commission_amount = (order.amount_untaxed * order.referral_rate) / 100
            else:
                order.referral_commission_amount = 0.0

    @api.depends('amount_untaxed', 'cashback_rate', 'cashback_commission_type')
    def _compute_cashback_commission(self):
        for order in self:
            if order.cashback_commission_type == 'untaxed_total':
                order.cashback_commission_amount = (order.amount_untaxed * order.cashback_rate) / 100
            else:
                order.cashback_commission_amount = 0.0

    @api.depends('other_rate', 'other_commission_type', 'other_fixed_amount')
    def _compute_other_commission(self):
        for order in self:
            if order.other_commission_type == 'untaxed_total':
                order.other_commission_amount = (order.amount_untaxed * order.other_rate) / 100
            elif order.other_commission_type == 'fixed':
                order.other_commission_amount = order.other_fixed_amount
            else:
                order.other_commission_amount = 0.0

    @api.depends('amount_untaxed', 'agent1_rate', 'internal_commission_type', 'agent1_fixed_amount')
    def _compute_agent1_commission(self):
        for order in self:
            if order.internal_commission_type == 'untaxed_total':
                order.agent1_commission_amount = (order.amount_untaxed * order.agent1_rate) / 100
            elif order.internal_commission_type == 'fixed':
                order.agent1_commission_amount = order.agent1_fixed_amount
            else:
                order.agent1_commission_amount = 0.0

    @api.depends('amount_untaxed', 'agent2_rate', 'internal_commission_type', 'agent2_fixed_amount')
    def _compute_agent2_commission(self):
        for order in self:
            if order.internal_commission_type == 'untaxed_total':
                order.agent2_commission_amount = (order.amount_untaxed * order.agent2_rate) / 100
            elif order.internal_commission_type == 'fixed':
                order.agent2_commission_amount = order.agent2_fixed_amount
            else:
                order.agent2_commission_amount = 0.0

    @api.depends('amount_untaxed', 'manager_rate', 'internal_commission_type', 'manager_fixed_amount')
    def _compute_manager_commission(self):
        for order in self:
            if order.internal_commission_type == 'untaxed_total':
                order.manager_commission_amount = (order.amount_untaxed * order.manager_rate) / 100
            elif order.internal_commission_type == 'fixed':
                order.manager_commission_amount = order.manager_fixed_amount
            else:
                order.manager_commission_amount = 0.0

    @api.depends('amount_untaxed', 'director_rate', 'internal_commission_type', 'director_fixed_amount')
    def _compute_director_commission(self):
        for order in self:
            if order.internal_commission_type == 'untaxed_total':
                order.director_commission_amount = (order.amount_untaxed * order.director_rate) / 100
            elif order.internal_commission_type == 'fixed':
                order.director_commission_amount = order.director_fixed_amount
            else:
                order.director_commission_amount = 0.0

    @api.depends(
        'broker_commission_amount',
        'referral_commission_amount',
        'cashback_commission_amount',
        'other_commission_amount',
        'agent1_commission_amount',
        'agent2_commission_amount',
        'manager_commission_amount',
        'director_commission_amount'
    )
    def _compute_total_commissions(self):
        for order in self:
            order.total_external_commission = sum([
                order.broker_commission_amount,
                order.referral_commission_amount,
                order.cashback_commission_amount,
                order.other_commission_amount
            ])
            order.total_internal_commission = sum([
                order.agent1_commission_amount,
                order.agent2_commission_amount,
                order.manager_commission_amount,
                order.director_commission_amount
            ])
            order.total_payable = order.total_external_commission + order.total_internal_commission

    @api.depends('amount_untaxed', 'total_external_commission', 'total_internal_commission')
    def _compute_company_net_commission(self):
        for order in self:
            order.company_net_commission = order.amount_untaxed - order.total_payable

    @api.depends('amount_untaxed', 'total_payable')
    def _compute_remaining_unallocated(self):
        for order in self:
            order.remaining_unallocated_amount = max(order.amount_untaxed - order.total_payable, 0)

    # Button Actions
    def action_calculate_commission(self):
        for order in self:
            # Recompute all commission fields
            order._recompute_dynamic_fields()
            order.commission_status = 'calculated'
            order.message_post(body=_('Commission recalculated by %s') % self.env.user.name)

    def action_confirm_commission(self):
        for order in self:
            if order.commission_status != 'calculated':
                raise UserError(_('Commission must be in "Calculated" state before confirmation!'))
            if order.commission_allocation_status == 'over':
                raise UserError(_('Cannot confirm commission with over allocation!'))
            order.commission_status = 'confirmed'
            order.commission_reference = self.env['ir.sequence'].next_by_code('commission.reference') or '/'
            order.message_post(body=_('Commission confirmed by %s') % self.env.user.name)

    def action_pay_commission(self):
        for order in self:
            if order.commission_status != 'confirmed':
                raise UserError(_('Commission must be confirmed before marking as paid!'))
            order.commission_status = 'paid'
            order.commission_payment_date = fields.Date.today()
            order.message_post(body=_('Commission marked as paid by %s') % self.env.user.name)

    def action_reset_commission(self):
        for order in self:
            order.commission_status = 'draft'
            order.commission_payment_date = False
            order.commission_reference = False
            order.message_post(body=_('Commission reset to draft by %s') % self.env.user.name)

    def _recompute_dynamic_fields(self):
        # Force recompute of all computed fields
        self._compute_broker_commission()
        self._compute_referral_commission()
        self._compute_cashback_commission()
        self._compute_other_commission()
        self._compute_agent1_commission()
        self._compute_agent2_commission()
        self._compute_manager_commission()
        self._compute_director_commission()
        self._compute_total_commissions()
        self._compute_company_net_commission()
        self._compute_remaining_unallocated()
        self._compute_internal_commission_base()
        self._compute_allocation_status()

    # Constraints
    @api.constrains(
        'broker_rate', 'referral_rate', 'cashback_rate', 'other_rate',
        'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate'
    )
    def _check_commission_rates(self):
        for order in self:
            for rate_field in [
                'broker_rate', 'referral_rate', 'cashback_rate', 'other_rate',
                'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate'
            ]:
                rate = getattr(order, rate_field)
                if rate and (rate < 0 or rate > 100):
                    raise ValidationError(_("Commission rates must be between 0 and 100!"))