from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round
import logging

_logger = logging.getLogger(__name__)

COMMISSION_TYPE_SELECTION = [
    ('unit_price', 'Unit Price'),
    ('untaxed', 'Untaxed Total'),
    ('fixed', 'Fixed Amount')
]

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Deal Information Fields (grouped)
    deal_id = fields.Char(
        string='Deal ID',
        index=True,
        copy=False,
        help="Unique identifier for the deal"
    )
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help="The date when the booking was made",
        index=True
    )
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
        help="The buyer associated with this sale order",
        index=True
    )
    project_id = fields.Many2one(
        'product.template',
        string='Project',
        help="The project associated with this sale order",
        ondelete='restrict',
        domain=[],
        required=True,
    )
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        help="The specific unit associated with this sale order",
        ondelete='restrict',
        domain="[('product_tmpl_id', '=', project_id)]",
        required=True,
    )
    sale_value = fields.Monetary(
        string='Sale Value',
        currency_field='currency_id',
        tracking=True,
        copy=True
    )

    # ===========================================
    # BASIC DEAL INFORMATION
    # ===========================================
    
    broker_commission = fields.Monetary(
        string='Broker Commission',
        currency_field='currency_id',
        tracking=True,
        copy=False
    )
    # Commission Status
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid')
    ], string='Commission Status', 
        default='draft',
        tracking=True,
        copy=False
    )

    # Commission Details
    commission_payment_date = fields.Date(
        string='Payment Date',
        copy=False,
        tracking=True
    )
    commission_reference = fields.Char(
        string='Reference',
        copy=False,
        tracking=True
    )
    commission_notes = fields.Html(
        string='Notes',
        tracking=True
    )

    # Commission Amounts
    total_internal_commission = fields.Monetary(
        string='Internal Commission',
        currency_field='currency_id',
        compute='_compute_total_commissions',
        store=True
    )
    total_external_commission = fields.Monetary(
        string='External Commission',
        currency_field='currency_id',
        compute='_compute_total_commissions',
        store=True
    )
    commission_percentage = fields.Float(
        string='Commission %',
        digits=(5, 2),
    )
    external_percentage = fields.Float(
        string='External Percentage',
        digits=(5, 2),
    )
    broker_agency_rate = fields.Float(
        string='Broker/Agency Percentage',
        digits=(5, 2),
    )
    agent1_rate = fields.Float(
        string='Agent 1 Percentage',
        digits=(5, 2),
    )
    agent2_rate = fields.Float(
        string='Agent 2 Percentage',
        digits=(5, 2),
    )

    # Computed summary fields
    grand_total_commission = fields.Monetary(string='Grand Total Commission', compute='_compute_total_commissions', store=True, tracking=True, currency_field='currency_id')
    commission_allocation_status = fields.Selection([
        ('under', 'Under Allocated'),
        ('full', 'Fully Allocated'),
        ('over', 'Over Allocated')
    ], string='Commission Allocation Status', compute='_compute_allocation_status', store=True, help="Shows if commission allocation matches the order value")
    company_net_commission = fields.Monetary(string='Company Net Commission', compute='_compute_company_net_commission', store=True, currency_field='currency_id', help="Net commission allocated to the company after external and internal commissions.")
    # Purchase order link
    commission_purchase_order_ids = fields.One2many('purchase.order', 'commission_sale_order_id', string='Commission Purchase Orders')

    # UI visibility logic
    @api.depends('external_commission_type', 'internal_commission_type', 'agent1_id', 'agent2_id', 'manager_id', 'director_id', 'external_partner_id')
    def _compute_show_commission_fields(self):
        for order in self:
            order.show_external_percentage = False
            order.show_external_fixed_amount = False
            order.show_agent1_rate = False
            order.show_agent1_fixed = False
            order.show_agent2_rate = False
            order.show_agent2_fixed = False
            order.show_manager_rate = False
            order.show_manager_fixed = False
            order.show_director_rate = False
            order.show_director_fixed = False

            if order.external_partner_id:
                if order.external_commission_type in ['unit_price', 'untaxed']:
                    order.show_external_percentage = True
                elif order.external_commission_type == 'fixed':
                    order.show_external_fixed_amount = True

            if order.agent1_id:
                if order.internal_commission_type in ['unit_price', 'untaxed']:
                    order.show_agent1_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_agent1_fixed = True
            if order.agent2_id:
                if order.internal_commission_type in ['unit_price', 'untaxed']:
                    order.show_agent2_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_agent2_fixed = True
            if order.manager_id:
                if order.internal_commission_type in ['unit_price', 'untaxed']:
                    order.show_manager_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_manager_fixed = True
            if order.director_id:
                if order.internal_commission_type in ['unit_price', 'untaxed']:
                    order.show_director_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_director_fixed = True

    # Commission percentage computation
    @api.depends(
        'external_commission_type', 'external_fixed_amount', 'amount_untaxed',
        'agent1_fixed', 'agent2_fixed', 'manager_fixed', 'director_fixed',
        'internal_commission_type'
    )
    def _compute_commission_percentages(self):
        for order in self:
            base = order.amount_untaxed or 0.0
            if order.external_commission_type == 'fixed' and base > 0 and order.external_fixed_amount:
                order.external_percentage = (order.external_fixed_amount / base) * 100
            if order.internal_commission_type == 'fixed' and base > 0:
                order.agent1_rate = (order.agent1_fixed / base) * 100 if order.agent1_fixed else 0.0
                order.agent2_rate = (order.agent2_fixed / base) * 100 if order.agent2_fixed else 0.0
                order.manager_rate = (order.manager_fixed / base) * 100 if order.manager_fixed else 0.0
                order.director_rate = (order.director_fixed / base) * 100 if order.director_fixed else 0.0

    # External commission totals
    @api.depends('order_line', 'amount_untaxed', 'external_commission_type', 'external_percentage', 'external_fixed_amount',
                 'broker_agency_commission_type', 'broker_agency_rate', 'referral_commission_type', 'referral_rate',
                 'cashback_commission_type', 'cashback_rate', 'other_external_commission_type', 'other_external_rate')
    def _compute_commission_totals(self):
        for order in self:
            order.external_commission_amount = order._compute_commission_amount(
                order.external_commission_type, order.external_percentage, order.external_fixed_amount
            )
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

    # Internal commission computation
    @api.depends('order_line', 'amount_untaxed', 'internal_commission_type', 'agent1_rate', 'agent1_fixed', 'agent2_rate', 'agent2_fixed', 'manager_rate', 'manager_fixed', 'director_rate', 'director_fixed', 'total_external_commission')
    def _compute_internal_commissions(self):
        for record in self:
            # Company share after external commission
            company_share = (record.grand_total_commission or 0.0) - (record.total_external_commission or 0.0)
            if company_share < 0:
                company_share = 0.0
            if record.internal_commission_type in ['unit_price', 'untaxed']:
                record.agent1_commission = (company_share * (record.agent1_rate or 0) / 100)
                record.agent2_commission = (company_share * (record.agent2_rate or 0) / 100)
                record.manager_commission = (company_share * (record.manager_rate or 0) / 100)
                record.director_commission = (company_share * (record.director_rate or 0) / 100)
            elif record.internal_commission_type == 'fixed':
                record.agent1_commission = record.agent1_fixed or 0.0
                record.agent2_commission = record.agent2_fixed or 0.0
                record.manager_commission = record.manager_fixed or 0.0
                record.director_commission = record.director_fixed or 0.0

    # Total commissions
    @api.depends('agent1_commission', 'agent2_commission', 'manager_commission', 'director_commission',
                 'external_commission_amount', 'broker_agency_total', 'referral_total', 
                 'cashback_total', 'other_external_total')
    def _compute_total_commissions(self):
        for record in self:
            record.total_internal_commission = sum([
                record.agent1_commission or 0.0,
                record.agent2_commission or 0.0,
                record.manager_commission or 0.0,
                record.director_commission or 0.0
            ])
            record.total_external_commission = sum([
                record.external_commission_amount or 0.0,
                record.broker_agency_total or 0.0,
                record.referral_total or 0.0,
                record.cashback_total or 0.0,
                record.other_external_total or 0.0
            ])
            record.grand_total_commission = record.total_internal_commission + record.total_external_commission

    # Company net commission
    @api.depends('total_external_commission', 'total_internal_commission', 'grand_total_commission')
    def _compute_company_net_commission(self):
        for record in self:
            record.company_net_commission = (record.grand_total_commission or 0.0) - (record.total_external_commission or 0.0) - (record.total_internal_commission or 0.0)

    # Allocation status and commission %
    @api.depends('grand_total_commission', 'amount_total', 'sale_value')
    def _compute_allocation_status(self):
        for record in self:
            base_amount = record.amount_untaxed or 0.0
            commission_total = record.grand_total_commission or 0.0
            if base_amount > 0:
                record.commission_percentage = (commission_total / base_amount) * 100
            else:
                record.commission_percentage = 0.0
            tolerance = 0.01
            if float_compare(commission_total, base_amount, precision_digits=2) == 0:
                record.commission_allocation_status = 'full'
            elif commission_total < base_amount - tolerance:
                record.commission_allocation_status = 'under'
            elif commission_total > base_amount + tolerance:
                record.commission_allocation_status = 'over'
            else:
                record.commission_allocation_status = 'full'

    # Helper
    def _compute_commission_amount(self, commission_type, rate, fixed_amount=0.0):
        self.ensure_one()
        if commission_type == 'unit_price':
            base = self.order_line[0].price_unit if self.order_line else 0.0
            return float_round((base * rate) / 100, precision_digits=2) if rate else 0.0
        elif commission_type == 'untaxed':
            base = self.amount_untaxed or 0.0
            return float_round((base * rate) / 100, precision_digits=2) if rate else 0.0
        elif commission_type == 'fixed':
            return fixed_amount or 0.0
        return 0.0

    def _generate_commission_sequence(self):
        if not self.commission_sequence:
            sequence = self.env['ir.sequence'].next_by_code('commission.sequence') or '/'
            self.commission_sequence = sequence

    # Constraints
    @api.constrains('agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate')
    def _check_commission_rates(self):
        for order in self:
            if order.internal_commission_type in ['unit_price', 'untaxed']:
                for rate in [order.agent1_rate, order.agent2_rate, order.manager_rate, order.director_rate]:
                    if rate and (rate < 0 or rate > 100):
                        raise ValidationError(_("Commission rates must be between 0 and 100 when using percentage type!"))
            elif order.internal_commission_type == 'fixed':
                # No constraint needed for fixed
                pass

    # Actions
    def action_confirm_commission(self):
        for order in self:
            if order.commission_status != 'calculated':
                raise UserError(_("Commission must be in 'Calculated' state before confirmation!"))
            if order.commission_allocation_status == 'over':
                raise UserError(_("Cannot confirm commission with over allocation!"))
            order._generate_commission_sequence()
            order.commission_status = 'confirmed'
            order.message_post(body=_("Commission confirmed by %s") % self.env.user.name)

    def action_pay_commission(self):
        for order in self:
            if order.commission_status != 'confirmed':
                raise UserError(_("Commission must be confirmed before marking as paid!"))
            order.commission_status = 'paid'
            order.commission_payment_date = fields.Date.today()
            order.message_post(body=_("Commission marked as paid by %s") % self.env.user.name)

    def _calculate_external_commissions(self):
        """Calculate all external commissions and set their fields."""
        self.external_commission_amount = self._compute_commission_amount(
            self.external_commission_type, self.external_percentage, self.external_fixed_amount
        )
        self.broker_agency_total = self._compute_commission_amount(
            self.broker_agency_commission_type, self.broker_agency_rate
        )
        self.referral_total = self._compute_commission_amount(
            self.referral_commission_type, self.referral_rate
        )
        self.cashback_total = self._compute_commission_amount(
            self.cashback_commission_type, self.cashback_rate
        )
        self.other_external_total = self._compute_commission_amount(
            self.other_external_commission_type, self.other_external_rate
        )
        self.total_external_commission = sum([
            self.external_commission_amount or 0.0,
            self.broker_agency_total or 0.0,
            self.referral_total or 0.0,
            self.cashback_total or 0.0,
            self.other_external_total or 0.0
        ])

    def _calculate_internal_commissions(self):
        """Calculate all internal commissions based on company share."""
        company_share = max((self.amount_untaxed or 0.0) - (self.total_external_commission or 0.0), 0.0)
        if self.internal_commission_type in ['unit_price', 'untaxed']:
            self.agent1_commission = (company_share * (self.agent1_rate or 0) / 100)
            self.agent2_commission = (company_share * (self.agent2_rate or 0) / 100)
            self.manager_commission = (company_share * (self.manager_rate or 0) / 100)
            self.director_commission = (company_share * (self.director_rate or 0) / 100)
        elif self.internal_commission_type == 'fixed':
            self.agent1_commission = self.agent1_fixed or 0.0
            self.agent2_commission = self.agent2_fixed or 0.0
            self.manager_commission = self.manager_fixed or 0.0
            self.director_commission = self.director_fixed or 0.0
        self.total_internal_commission = sum([
            self.agent1_commission or 0.0,
            self.agent2_commission or 0.0,
            self.manager_commission or 0.0,
            self.director_commission or 0.0
        ])

    def _check_commission_consistency(self):
        """Ensure total commissions do not exceed untaxed amount and are not negative."""
        if self.total_external_commission < 0 or self.total_internal_commission < 0:
            raise UserError(_('Commission values cannot be negative.'))
        total_commission = (self.total_external_commission or 0.0) + (self.total_internal_commission or 0.0)
        if total_commission > (self.amount_untaxed or 0.0) + 0.01:  # allow small rounding error
            raise UserError(_('Total commission cannot exceed the untaxed amount.'))

    def action_calculate_commission(self):
        for order in self:
            order._calculate_external_commissions()
            order._calculate_internal_commissions()
            order._check_commission_consistency()
            order.grand_total_commission = (order.total_external_commission or 0.0) + (order.total_internal_commission or 0.0)
            order._compute_allocation_status()
            order.commission_status = 'calculated'
            order.message_post(body=_('Commission recalculated by %s') % self.env.user.name)

    def action_reset_commission(self):
        for order in self:
            if order.commission_status == 'paid':
                raise UserError(_("Cannot reset paid commissions!"))
            for po in order.commission_purchase_order_ids:
                if po.state not in ['cancel', 'done']:
                    po.button_cancel()
                po.unlink()
            order.commission_status = 'draft'
            order.message_post(body=_("Commission reset to draft by %s") % self.env.user.name)

    def action_view_related_purchase_orders(self):
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
            for po in order.commission_purchase_order_ids:
                if po.state not in ['cancel', 'done']:
                    po.button_cancel()
                po.unlink()
            if order.commission_status not in ['confirmed', 'paid']:
                raise UserError(_('Commission must be confirmed or paid before creating a purchase order.'))
            if not order.invoice_ids or not any(inv.state in ['posted', 'paid'] for inv in order.invoice_ids):
                raise UserError(_('You must have at least one processed invoice (posted/paid) before creating a commission purchase order.'))
            commission_lines = []
            if order.agent1_id and order.agent1_commission > 0:
                commission_lines.append({'partner': order.agent1_id, 'amount': order.agent1_commission})
            if order.agent2_id and order.agent2_commission > 0:
                commission_lines.append({'partner': order.agent2_id, 'amount': order.agent2_commission})
            if order.manager_id and order.manager_commission > 0:
                commission_lines.append({'partner': order.manager_id, 'amount': order.manager_commission})
            if order.director_id and order.director_commission > 0:
                commission_lines.append({'partner': order.director_id, 'amount': order.director_commission})
            if order.external_partner_id and order.external_commission_amount > 0:
                commission_lines.append({'partner': order.external_partner_id, 'amount': order.external_commission_amount})
            if order.broker_agency_partner_id and order.broker_agency_total > 0:
                commission_lines.append({'partner': order.broker_agency_partner_id, 'amount': order.broker_agency_total})
            if order.referral_partner_id and order.referral_total > 0:
                commission_lines.append({'partner': order.referral_partner_id, 'amount': order.referral_total})
            if order.cashback_partner_id and order.cashback_total > 0:
                commission_lines.append({'partner': order.cashback_partner_id, 'amount': order.cashback_total})
            if order.other_external_partner_id and order.other_external_total > 0:
                commission_lines.append({'partner': order.other_external_partner_id, 'amount': order.other_external_total})
            if not commission_lines:
                raise UserError(_('No commission recipients with non-zero commission found.'))
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
                        'name': '',
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

    # Onchange
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            return {'domain': {'unit_id': [('product_tmpl_id', '=', self.project_id.id)]}}
        else:
            self.unit_id = False
            return {'domain': {'unit_id': []}}

    @api.onchange('internal_commission_type')
    def _onchange_internal_commission_type(self):
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

    # Overrides
    def action_confirm(self):
        for order in self:
            if order.commission_status == 'draft' and order.grand_total_commission > 0:
                raise UserError(_("Please calculate commissions before confirming the order!"))
        return super().action_confirm()

    def write(self, vals):
        protected_fields = [
            'sale_value', 'broker_commission', 'commission_status',
            'external_commission_amount', 'broker_agency_total',
            'referral_total', 'cashback_total', 'other_external_total',
            'agent1_commission', 'agent2_commission', 
            'manager_commission', 'director_commission'
        ]
        if any(field in vals for field in protected_fields):
            for order in self:
                if order.state not in ['draft', 'sent'] and order.commission_status in ['confirmed', 'paid']:
                    raise UserError(_("Cannot modify commission details after order confirmation when commission is confirmed or paid!"))
        return super().write(vals)

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'commission_status': 'draft',
            'commission_sequence': False,
            'commission_payment_date': False,
            'commission_reference': False,
        })
        return super(SaleOrder, self).copy(default)

    # Reporting
    def get_commission_summary(self):
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
                    'name': self.broker_agency_partner_id.name if self.broker_agency_partner_id else 'N/A',
                    'amount': self.broker_agency_total
                },
                'referral': {
                    'name': self.referral_partner_id.name if self.referral_partner_id else 'N/A',
                    'amount': self.referral_total
                },
                'cashback': {
                    'name': self.cashback_partner_id.name if self.cashback_partner_id else 'N/A',
                    'amount': self.cashback_total
                },
                'other': {
                    'name': self.other_external_partner_id.name if self.other_external_partner_id else 'N/A',
                    'amount': self.other_external_total
                },
                'total': self.total_external_commission
            },
            'grand_total': self.grand_total_commission,
            'status': self.commission_status,
            'percentage': self.commission_percentage
        }

# Patch purchase.order to add a link to sale.order
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    commission_sale_order_id = fields.Many2one('sale.order', string='Commission Sale Order', index=True, help='The sale order that generated this commission purchase order.')

    def action_create_commission_purchase_order(self):
        """Create purchase orders for all commission recipients with non-zero commission amounts.
        Removes/cancels old commission POs before creating new ones for accuracy and to avoid duplicates."""
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
            # Remove/cancel old commission POs
            for po in order.commission_purchase_order_ids:
                if po.state not in ['cancel', 'done']:
                    po.button_cancel()
                po.unlink()
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
                    'amount': order.agent1_commission
                })
            if order.agent2_id and order.agent2_commission > 0:
                commission_lines.append({
                    'partner': order.agent2_id,
                    'amount': order.agent2_commission
                })
            if order.manager_id and order.manager_commission > 0:
                commission_lines.append({
                    'partner': order.manager_id,
                    'amount': order.manager_commission
                })
            if order.director_id and order.director_commission > 0:
                commission_lines.append({
                    'partner': order.director_id,
                    'amount': order.director_commission
                })
            # External
            if order.external_partner_id and order.external_commission_amount > 0:
                commission_lines.append({
                    'partner': order.external_partner_id,
                    'amount': order.external_commission_amount
                })
            if order.broker_agency_partner_id and order.broker_agency_total > 0:
                commission_lines.append({
                    'partner': order.broker_agency_partner_id,
                    'amount': order.broker_agency_total
                })
            if order.referral_partner_id and order.referral_total > 0:
                commission_lines.append({
                    'partner': order.referral_partner_id,
                    'amount': order.referral_total
                })
            if order.cashback_partner_id and order.cashback_total > 0:
                commission_lines.append({
                    'partner': order.cashback_partner_id,
                    'amount': order.cashback_total
                })
            if order.other_external_partner_id and order.other_external_total > 0:
                commission_lines.append({
                    'partner': order.other_external_partner_id,
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
                        'name': '',
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
            'sale_value', 'broker_commission', 'commission_status',
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
    # COMPUTED FIELDS FOR UI VISIBILITY CONTROL
    # ===========================================
    
    # Compute fields for UI visibility control
    show_external_percentage = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_external_fixed_amount = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_agent1_rate = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_agent1_fixed = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_agent2_rate = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_agent2_fixed = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_manager_rate = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_manager_fixed = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_director_rate = fields.Boolean(compute='_compute_show_commission_fields', store=True)
    show_director_fixed = fields.Boolean(compute='_compute_show_commission_fields', store=True)

    @api.depends('external_commission_type', 'internal_commission_type', 'agent1_id', 'agent2_id', 'manager_id', 'director_id')
    def _compute_show_commission_fields(self):
        """Compute visibility of commission fields based on selected partners and commission types."""
        for order in self:
            # Default to False
            order.show_external_percentage = False
            order.show_external_fixed_amount = False
            order.show_agent1_rate = False
            order.show_agent1_fixed = False
            order.show_agent2_rate = False
            order.show_agent2_fixed = False
            order.show_manager_rate = False
            order.show_manager_fixed = False
            order.show_director_rate = False
            order.show_director_fixed = False
            
            # External commission fields visibility
            if order.external_partner_id:
                if order.external_commission_type == 'unit_price':
                    order.show_external_percentage = True
                elif order.external_commission_type == 'fixed':
                    order.show_external_fixed_amount = True

            # Internal commission fields visibility
            if order.agent1_id:
                order.show_agent1_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_agent1_fixed = True
            if order.agent2_id:
                order.show_agent2_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_agent2_fixed = True
            if order.manager_id:
                order.show_manager_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_manager_fixed = True
            if order.director_id:
                order.show_director_rate = True
                if order.internal_commission_type == 'fixed':
                    order.show_director_fixed = True

    # ===========================================
    # COMPUTED FIELDS FOR INTERNAL COMMISSION BASE
    # ===========================================

    internal_commission_base = fields.Monetary(
        string='Internal Commission Base',
        currency_field='currency_id',
        compute='_compute_internal_commission_base',
        store=False,
        help='The company share (after external commission) used as the base for internal commission calculation.'
    )

    def _compute_internal_commission_base(self):
        for rec in self:
            rec.internal_commission_base = max((rec.grand_total_commission or 0.0) - (rec.total_external_commission or 0.0), 0.0)

    # ===========================================
    # BUTTON AND FIELD VISIBILITY COMPUTED FIELDS
    # ===========================================

    can_calculate_commission = fields.Boolean(
        compute='_compute_commission_button_visibility',
        store=False
    )
    can_confirm_commission = fields.Boolean(
        compute='_compute_commission_button_visibility',
        store=False
    )
    can_pay_commission = fields.Boolean(
        compute='_compute_commission_button_visibility',
        store=False
    )
    can_reset_commission = fields.Boolean(
        compute='_compute_commission_button_visibility',
        store=False
    )

    @api.depends('commission_status')
    def _compute_commission_button_visibility(self):
        for rec in self:
            rec.can_calculate_commission = rec.commission_status == 'draft'
            rec.can_confirm_commission = rec.commission_status == 'calculated'
            rec.can_pay_commission = rec.commission_status == 'confirmed'
            rec.can_reset_commission = rec.commission_status != 'paid'