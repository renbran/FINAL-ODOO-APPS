# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ========== COMMISSION BASE FIELD ==========
    sales_value = fields.Float(
        string='Sales Value',
        tracking=True,
        help='Base value used for commission calculations when type is "Based on Price Unit"'
    )

    # ========== COMMISSION TYPE FIELDS ==========
    broker_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Broker Commission Type',
        default='untaxed_total'
    )
    
    referrer_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Referrer Commission Type',
        default='untaxed_total'
    )
    
    cashback_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Cashback Commission Type',
        default='untaxed_total'
    )
    
    other_external_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Other External Commission Type',
        default='untaxed_total'
    )
    
    agent1_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Agent 1 Commission Type',
        default='untaxed_total'
    )
    
    agent2_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Agent 2 Commission Type',
        default='untaxed_total'
    )
    
    manager_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Manager Commission Type',
        default='untaxed_total'
    )
    
    director_commission_type = fields.Selection(
        selection=[('price_unit', 'Based on Price Unit'),
                   ('untaxed_total', 'Based on Untaxed Total'),
                   ('fixed_amount', 'Fixed Amount')],
        string='Director Commission Type',
        default='untaxed_total'
    )

    # ========== EXTERNAL COMMISSION FIELDS ==========
    broker_partner_id = fields.Many2one('res.partner', string="Broker", tracking=True)
    broker_rate = fields.Float(string="Broker Rate", tracking=True, digits='Commission Rate')
    broker_amount = fields.Monetary(string="Broker Amount", currency_field='currency_id', compute='_compute_commission_totals', store=True)

    referrer_partner_id = fields.Many2one('res.partner', string="Referrer", tracking=True)
    referrer_rate = fields.Float(string="Referrer Rate", tracking=True, digits='Commission Rate')
    referrer_amount = fields.Monetary(string="Referrer Amount", currency_field='currency_id', compute='_compute_commission_totals', store=True)

    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Recipient", tracking=True)
    cashback_rate = fields.Float(string="Cashback Rate", tracking=True, digits='Commission Rate')
    cashback_amount = fields.Monetary(string="Cashback Amount", currency_field='currency_id', compute='_compute_commission_totals', store=True)

    other_external_partner_id = fields.Many2one('res.partner', string="Other External Party", tracking=True)
    other_external_rate = fields.Float(string="Other External Rate", tracking=True, digits='Commission Rate')
    other_external_amount = fields.Monetary(string="Other External Amount", currency_field='currency_id', compute='_compute_commission_totals', store=True)

    # ========== INTERNAL COMMISSION FIELDS ==========
    agent1_partner_id = fields.Many2one('res.partner', string='Agent 1', tracking=True)
    agent1_rate = fields.Float(string='Agent 1 Rate', tracking=True, digits='Commission Rate')
    agent1_amount = fields.Monetary(string='Agent 1 Amount', currency_field='currency_id', compute='_compute_commission_totals', store=True)

    agent2_partner_id = fields.Many2one('res.partner', string='Agent 2', tracking=True)
    agent2_rate = fields.Float(string='Agent 2 Rate', tracking=True, digits='Commission Rate')
    agent2_amount = fields.Monetary(string='Agent 2 Amount', currency_field='currency_id', compute='_compute_commission_totals', store=True)

    manager_partner_id = fields.Many2one('res.partner', string='Manager', tracking=True)
    manager_rate = fields.Float(string='Manager Rate', tracking=True, digits='Commission Rate')
    manager_amount = fields.Monetary(string='Manager Amount', currency_field='currency_id', compute='_compute_commission_totals', store=True)

    director_partner_id = fields.Many2one('res.partner', string='Director', tracking=True)
    director_rate = fields.Float(string='Director Rate', tracking=True, digits='Commission Rate')
    director_amount = fields.Monetary(string='Director Amount', currency_field='currency_id', compute='_compute_commission_totals', store=True)

    # ========== COMMISSION SUMMARY FIELDS ==========
    total_external_commission_amount = fields.Monetary(
        string='Total External Amount',
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True
    )
    
    total_internal_commission_amount = fields.Monetary(
        string='Total Internal Amount',
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True
    )
    
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        currency_field='currency_id',
        compute='_compute_commission_totals',
        store=True
    )
    
    company_share = fields.Monetary(
        string="Company Share", 
        compute='_compute_commission_totals', 
        store=True
    )
    
    net_company_share = fields.Monetary(
        string="Net Company Share", 
        compute='_compute_commission_totals', 
        store=True
    )

    commission_status = fields.Selection([
        ('draft', 'Draft'),  
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Commission Status', default='draft', tracking=True)
    
    commission_processed = fields.Boolean(
        string="Commission Processed", 
        default=False
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

    # ========== COMPUTE METHODS ==========
    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)
    
    @api.depends(
        'amount_untaxed', 'sales_value',
        'broker_rate', 'broker_commission_type',
        'referrer_rate', 'referrer_commission_type',
        'cashback_rate', 'cashback_commission_type',
        'other_external_rate', 'other_external_commission_type',
        'agent1_rate', 'agent1_commission_type',
        'agent2_rate', 'agent2_commission_type',
        'manager_rate', 'manager_commission_type',
        'director_rate', 'director_commission_type'
    )
    def _compute_commission_totals(self):
        """Compute all commission totals and company shares"""
        for order in self:
            untaxed_amount = order.amount_untaxed
            sales_value = order.sales_value or 0.0

            def calculate_commission(rate, commission_type):
                """Calculate commission based on type"""
                if commission_type == 'price_unit':
                    return rate * sales_value
                elif commission_type == 'untaxed_total':
                    return rate * untaxed_amount
                return 0.0

            # Calculate all commission amounts
            order.broker_amount = calculate_commission(
                order.broker_rate, order.broker_commission_type
            )
            order.referrer_amount = calculate_commission(
                order.referrer_rate, order.referrer_commission_type
            )
            order.cashback_amount = calculate_commission(
                order.cashback_rate, order.cashback_commission_type
            )
            order.other_external_amount = calculate_commission(
                order.other_external_rate, order.other_external_commission_type
            )
            order.agent1_amount = calculate_commission(
                order.agent1_rate, order.agent1_commission_type
            )
            order.agent2_amount = calculate_commission(
                order.agent2_rate, order.agent2_commission_type
            )
            order.manager_amount = calculate_commission(
                order.manager_rate, order.manager_commission_type
            )
            order.director_amount = calculate_commission(
                order.director_rate, order.director_commission_type
            )

            # Calculate totals
            external_commissions = [
                order.broker_amount,
                order.referrer_amount,
                order.cashback_amount,
                order.other_external_amount
            ]
            internal_commissions = [
                order.agent1_amount,
                order.agent2_amount,
                order.manager_amount,
                order.director_amount
            ]

            order.total_external_commission_amount = sum(external_commissions)
            order.total_internal_commission_amount = sum(internal_commissions)
            order.total_commission_amount = (order.total_external_commission_amount + 
                                          order.total_internal_commission_amount)
            order.company_share = untaxed_amount - order.total_commission_amount
            order.net_company_share = order.company_share

    # ========== BUSINESS METHODS ==========
    def _get_or_create_commission_product(self):
        """Get or create commission product for POs"""
        commission_product = self.env['product.product'].search([
            ('default_code', '=', 'COMMISSION')
        ], limit=1)
        
        if not commission_product:
            commission_product = self.env['product.product'].create({
                'name': 'Commission Payment',
                'default_code': 'COMMISSION',
                'type': 'service',
                'purchase_ok': True,
                'sale_ok': False,
                'list_price': 0.0,
                'standard_price': 0.0,
            })
        return commission_product

    def _create_commission_purchase_order(self, partner, amount, description):
        """Create a PO for commission payment"""
        if not partner or not amount or amount <= 0:
            return False
            
        commission_product = self._get_or_create_commission_product()
        
        po_vals = {
            'partner_id': partner.id,
            'origin': self.name,
            'origin_so_id': self.id,
            'order_line': [(0, 0, {
                'product_id': commission_product.id,
                'name': f"{description} - {self.name}",
                'product_qty': 1,
                'price_unit': amount,
                'product_uom': commission_product.uom_po_id.id,
            })]
        }
        
        try:
            return self.env['purchase.order'].create(po_vals)
        except Exception as e:
            _logger.error(f"Failed to create PO for {partner.name}: {str(e)}")
            return False

    def action_generate_commission_purchase_orders(self):
        """Generate POs for all commission recipients"""
        if self.commission_processed:
            raise UserError(_("Commission POs already generated"))
        
        if self.state != 'sale':
            raise UserError(_("Only confirmed orders can generate commission POs"))

        generated_pos = []
        commission_partners = [
            ('broker', self.broker_partner_id, self.broker_amount, "Broker Commission"),
            ('referrer', self.referrer_partner_id, self.referrer_amount, "Referrer Commission"),
            ('cashback', self.cashback_partner_id, self.cashback_amount, "Cashback Commission"),
            ('other', self.other_external_partner_id, self.other_external_amount, "Other Commission"),
            ('agent1', self.agent1_partner_id, self.agent1_amount, "Agent 1 Commission"),
            ('agent2', self.agent2_partner_id, self.agent2_amount, "Agent 2 Commission"),
            ('manager', self.manager_partner_id, self.manager_amount, "Manager Commission"),
            ('director', self.director_partner_id, self.director_amount, "Director Commission"),
        ]

        for partner_type, partner, amount, desc in commission_partners:
            if partner and amount > 0:
                if po := self._create_commission_purchase_order(partner, amount, desc):
                    generated_pos.append(po.id)

        if generated_pos:
            self.write({
                'commission_processed': True,
                'commission_status': 'confirmed',
                'purchase_order_ids': [(6, 0, generated_pos)]
            })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Commission POs',
                'res_model': 'purchase.order',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', generated_pos)],
            }
        raise UserError(_("No valid commission partners with amounts > 0 found"))