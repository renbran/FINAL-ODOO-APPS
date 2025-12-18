from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Commission fields (Legacy - using percentage-based calculation)
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Consultant Commission Type", default='percent_untaxed_total')
    consultant_comm_percentage = fields.Float(string="Consultant Commission (%)", default=0.0)
    consultant_calculation_base = fields.Monetary(
        string="Consultant Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for consultant commission calculation"
    )
    salesperson_commission = fields.Monetary(string="Consultant Commission Amount", compute="_compute_commissions", store=True)

    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_legacy_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Legacy Commission Type", default='percent_untaxed_total')
    manager_comm_percentage = fields.Float(string="Manager Commission (%)", default=0.0)
    manager_legacy_calculation_base = fields.Monetary(
        string="Manager Legacy Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for manager legacy commission calculation"
    )
    manager_commission = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_id = fields.Many2one('res.partner', string="Director")
    director_legacy_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Director Legacy Commission Type", default='percent_untaxed_total')
    director_comm_percentage = fields.Float(string="Director Commission (%)", default=3.0)
    director_legacy_calculation_base = fields.Monetary(
        string="Director Legacy Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for director legacy commission calculation"
    )
    director_commission = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)

    # Second Agent fields
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    second_agent_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Second Agent Commission Type", default='percent_untaxed_total')
    second_agent_comm_percentage = fields.Float(string="Second Agent Commission (%)", default=0.0)
    second_agent_calculation_base = fields.Monetary(
        string="Second Agent Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for second agent commission calculation"
    )
    second_agent_commission = fields.Monetary(string="Second Agent Commission Amount", compute="_compute_commissions", store=True)

    # Extended Commission Structure - External Commissions
    broker_partner_id = fields.Many2one('res.partner', string="Broker")
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Broker Commission Type", default='percent_unit_price')
    broker_rate = fields.Float(string="Broker Rate")
    broker_amount = fields.Monetary(string="Broker Commission", compute="_compute_commissions", store=True)
    broker_calculation_base = fields.Monetary(
        string="Broker Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for broker commission calculation"
    )

    referrer_partner_id = fields.Many2one('res.partner', string="Referrer")
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Referrer Commission Type", default='percent_unit_price')
    referrer_rate = fields.Float(string="Referrer Rate")
    referrer_amount = fields.Monetary(string="Referrer Commission", compute="_compute_commissions", store=True)
    referrer_calculation_base = fields.Monetary(
        string="Referrer Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for referrer commission calculation"
    )

    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Partner")
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Cashback Type", default='percent_unit_price')
    cashback_rate = fields.Float(string="Cashback Rate")
    cashback_amount = fields.Monetary(string="Cashback Amount", compute="_compute_commissions", store=True)
    cashback_calculation_base = fields.Monetary(
        string="Cashback Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for cashback calculation"
    )

    other_external_partner_id = fields.Many2one('res.partner', string="Other External Partner")
    other_external_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Other External Commission Type", default='percent_unit_price')
    other_external_rate = fields.Float(string="Other External Rate")
    other_external_amount = fields.Monetary(string="Other External Commission", compute="_compute_commissions", store=True)
    other_external_calculation_base = fields.Monetary(
        string="Other External Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for other external commission calculation"
    )

    # Extended Commission Structure - Internal Commissions
    agent1_partner_id = fields.Many2one('res.partner', string="Agent 1")
    agent1_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 1 Commission Type", default='percent_unit_price')
    agent1_rate = fields.Float(string="Agent 1 Rate")
    agent1_amount = fields.Monetary(string="Agent 1 Commission", compute="_compute_commissions", store=True)
    agent1_calculation_base = fields.Monetary(
        string="Agent 1 Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for agent 1 commission calculation"
    )

    agent2_partner_id = fields.Many2one('res.partner', string="Agent 2")
    agent2_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 2 Commission Type", default='percent_unit_price')
    agent2_rate = fields.Float(string="Agent 2 Rate")
    agent2_amount = fields.Monetary(string="Agent 2 Commission", compute="_compute_commissions", store=True)
    agent2_calculation_base = fields.Monetary(
        string="Agent 2 Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for agent 2 commission calculation"
    )

    manager_partner_id = fields.Many2one('res.partner', string="Manager Partner")
    manager_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Commission Type", default='percent_unit_price')
    manager_rate = fields.Float(string="Manager Rate")
    manager_amount = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)
    manager_calculation_base = fields.Monetary(
        string="Manager Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for manager commission calculation"
    )

    director_partner_id = fields.Many2one('res.partner', string="Director Partner")
    director_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Director Commission Type", default='percent_unit_price')
    director_rate = fields.Float(string="Director Rate", default=3.0)
    director_amount = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)
    director_calculation_base = fields.Monetary(
        string="Director Calculation Base",
        compute="_compute_commission_calculation_bases",
        help="The base amount used for director commission calculation"
    )

    # Summary fields
    total_external_commission_amount = fields.Monetary(string="Total External Commissions", compute="_compute_commissions", store=True)
    total_internal_commission_amount = fields.Monetary(string="Total Internal Commissions", compute="_compute_commissions", store=True)
    total_commission_amount = fields.Monetary(string="Total Commission Amount", compute="_compute_commissions", store=True)

    # Computed fields
    company_share = fields.Monetary(string="Company Share", compute="_compute_commissions", store=True)
    net_company_share = fields.Monetary(string="Net Company Share", compute="_compute_commissions", store=True)

    # Sales Value field for commission computation
    sales_value = fields.Monetary(string="Sales Value", compute="_compute_sales_value", store=True)

    # Related fields
    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    purchase_order_count = fields.Integer(string="PO Count", compute="_compute_purchase_order_count")
    purchase_order_total_amount = fields.Monetary(string="Total PO Amount", compute="_compute_purchase_order_count", 
                                                 help="Total amount of all commission purchase orders")
    commission_processed = fields.Boolean(string="Commissions Processed", default=False)
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed')
    ], string="Commission Processing Status", default='draft')
    
    # Commission lines count for compatibility
    commission_lines_count = fields.Integer(
        string="Commission Partners Count",
        compute="_compute_commission_lines_count",
        help="Number of commission partners configured for this order"
    )
    
    # Invoice status field for compatibility
    is_fully_invoiced = fields.Boolean(
        string="Fully Invoiced",
        compute="_compute_is_fully_invoiced",
        help="True if all order lines are fully invoiced"
    )
    
    # Posted invoices check for compatibility
    has_posted_invoices = fields.Boolean(
        string="Has Posted Invoices",
        compute="_compute_has_posted_invoices",
        help="True if this order has at least one posted invoice"
    )
    
    # Commission lines relationship
    commission_line_ids = fields.One2many(
        'commission.ax',
        'sale_order_id',
        string="Commission Lines",
        help="Commission records associated with this sale order"
    )

    @api.depends('purchase_order_ids', 'purchase_order_ids.amount_total')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)
            # Calculate total amount of commission purchase orders
            order.purchase_order_total_amount = sum(
                po.amount_total for po in order.purchase_order_ids if po.state != 'cancel'
            )
    
    @api.depends(
        'broker_partner_id', 'broker_amount',
        'referrer_partner_id', 'referrer_amount',
        'cashback_partner_id', 'cashback_amount',
        'other_external_partner_id', 'other_external_amount',
        'agent1_partner_id', 'agent1_amount',
        'agent2_partner_id', 'agent2_amount',
        'manager_partner_id', 'manager_amount',
        'director_partner_id', 'director_amount',
        'consultant_id', 'salesperson_commission',
        'manager_id', 'manager_commission',
        'second_agent_id', 'second_agent_commission',
        'director_id', 'director_commission'
    )
    def _compute_commission_lines_count(self):
        """Compute the number of active commission partners."""
        for order in self:
            count = 0
            # Count external commission partners
            if order.broker_partner_id and order.broker_amount:
                count += 1
            if order.referrer_partner_id and order.referrer_amount:
                count += 1
            if order.cashback_partner_id and order.cashback_amount:
                count += 1
            if order.other_external_partner_id and order.other_external_amount:
                count += 1
            # Count internal commission partners
            if order.agent1_partner_id and order.agent1_amount:
                count += 1
            if order.agent2_partner_id and order.agent2_amount:
                count += 1
            if order.manager_partner_id and order.manager_amount:
                count += 1
            if order.director_partner_id and order.director_amount:
                count += 1
            # Count legacy commission partners
            if order.consultant_id and order.salesperson_commission:
                count += 1
            if order.manager_id and order.manager_commission:
                count += 1
            if order.second_agent_id and order.second_agent_commission:
                count += 1
            if order.director_id and order.director_commission:
                count += 1
            order.commission_lines_count = count
    
    @api.depends('order_line.invoice_lines', 'order_line.product_uom_qty', 'order_line.qty_invoiced')
    def _compute_is_fully_invoiced(self):
        """Check if all order lines are fully invoiced."""
        for order in self:
            if not order.order_line:
                order.is_fully_invoiced = False
                continue
            
            # Check if all lines are fully invoiced
            fully_invoiced = True
            for line in order.order_line:
                # Skip service products or products set to ordered quantities
                if line.product_id.invoice_policy == 'order':
                    if line.qty_invoiced < line.product_uom_qty:
                        fully_invoiced = False
                        break
                # For delivered products, check if delivered qty is invoiced
                elif line.product_id.invoice_policy == 'delivery':
                    if line.qty_invoiced < line.qty_delivered:
                        fully_invoiced = False
                        break
            
            order.is_fully_invoiced = fully_invoiced
    
    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_has_posted_invoices(self):
        """Check if this order has at least one posted invoice."""
        for order in self:
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            order.has_posted_invoices = len(posted_invoices) > 0
    
    @api.depends('order_line.price_unit', 'order_line.price_subtotal', 'amount_untaxed',
                 'broker_commission_type', 'referrer_commission_type', 'cashback_commission_type',
                 'other_external_commission_type', 'agent1_commission_type', 'agent2_commission_type',
                 'manager_commission_type', 'director_commission_type',
                 'consultant_commission_type', 'manager_legacy_commission_type', 
                 'director_legacy_commission_type', 'second_agent_commission_type')
    def _compute_commission_calculation_bases(self):
        """Compute the calculation base amounts for commission calculations."""
        for order in self:
            if order.order_line:
                first_line = order.order_line[0]
                unit_price = first_line.price_unit
                untaxed_total = order.amount_untaxed
                
                # External Commissions
                order.broker_calculation_base = unit_price if order.broker_commission_type == 'percent_unit_price' else untaxed_total
                order.referrer_calculation_base = unit_price if order.referrer_commission_type == 'percent_unit_price' else untaxed_total
                order.cashback_calculation_base = unit_price if order.cashback_commission_type == 'percent_unit_price' else untaxed_total
                order.other_external_calculation_base = unit_price if order.other_external_commission_type == 'percent_unit_price' else untaxed_total
                
                # Internal Commissions
                order.agent1_calculation_base = unit_price if order.agent1_commission_type == 'percent_unit_price' else untaxed_total
                order.agent2_calculation_base = unit_price if order.agent2_commission_type == 'percent_unit_price' else untaxed_total
                order.manager_calculation_base = unit_price if order.manager_commission_type == 'percent_unit_price' else untaxed_total
                order.director_calculation_base = unit_price if order.director_commission_type == 'percent_unit_price' else untaxed_total
                
                # Legacy Commissions
                order.consultant_calculation_base = unit_price if order.consultant_commission_type == 'percent_unit_price' else untaxed_total
                order.manager_legacy_calculation_base = unit_price if order.manager_legacy_commission_type == 'percent_unit_price' else untaxed_total
                order.director_legacy_calculation_base = unit_price if order.director_legacy_commission_type == 'percent_unit_price' else untaxed_total
                order.second_agent_calculation_base = unit_price if order.second_agent_commission_type == 'percent_unit_price' else untaxed_total
            else:
                # External Commissions
                order.broker_calculation_base = 0.0
                order.referrer_calculation_base = 0.0
                order.cashback_calculation_base = 0.0
                order.other_external_calculation_base = 0.0
                # Internal Commissions
                order.agent1_calculation_base = 0.0
                order.agent2_calculation_base = 0.0
                order.manager_calculation_base = 0.0
                order.director_calculation_base = 0.0
                # Legacy Commissions
                order.consultant_calculation_base = 0.0
                order.manager_legacy_calculation_base = 0.0
                order.director_legacy_calculation_base = 0.0
                order.second_agent_calculation_base = 0.0

    @api.constrains('order_line')
    def _check_single_order_line(self):
        for order in self:
            if len(order.order_line) > 1:
                raise ValidationError("Only one order line is allowed per sale order for commission clarity.")

    def _check_partner_po_cancellation_required(self, partner_id):
        """Check if partner has existing POs that need cancellation before new commission calculation."""
        if not partner_id:
            return True
        
        existing_pos = self.env['purchase.order'].search([
            ('partner_id', '=', partner_id.id),
            ('origin_so_id', '=', self.id),
            ('state', '!=', 'cancel')
        ])
        
        if existing_pos:
            # Check if there are any cancelled POs for this partner (allowing update)
            cancelled_pos = self.env['purchase.order'].search([
                ('partner_id', '=', partner_id.id),
                ('origin_so_id', '=', self.id),
                ('state', '=', 'cancel')
            ])
            
            if not cancelled_pos:
                raise ValidationError(
                    f"Cannot update commission calculation for partner '{partner_id.name}' "
                    f"without first cancelling existing purchase orders: {', '.join(existing_pos.mapped('name'))}. "
                    f"Please cancel the related POs before updating commission settings."
                )
        
        return True

    def _check_po_creation_constraints(self):
        """Check if new PO creation is allowed based on cancellation logic."""
        self.ensure_one()
        
        # Get all commission partners
        commission_partners = []
        
        # External partners
        if self.broker_partner_id:
            commission_partners.append(self.broker_partner_id)
        if self.referrer_partner_id:
            commission_partners.append(self.referrer_partner_id)
        if self.cashback_partner_id:
            commission_partners.append(self.cashback_partner_id)
        if self.other_external_partner_id:
            commission_partners.append(self.other_external_partner_id)
        
        # Internal partners
        if self.agent1_partner_id:
            commission_partners.append(self.agent1_partner_id)
        if self.agent2_partner_id:
            commission_partners.append(self.agent2_partner_id)
        if self.manager_partner_id:
            commission_partners.append(self.manager_partner_id)
        if self.director_partner_id:
            commission_partners.append(self.director_partner_id)
        
        # Legacy partners
        if self.consultant_id:
            commission_partners.append(self.consultant_id)
        if self.manager_id:
            commission_partners.append(self.manager_id)
        if self.director_id:
            commission_partners.append(self.director_id)
        if self.second_agent_id:
            commission_partners.append(self.second_agent_id)
        
        # Check each partner for existing POs
        for partner in commission_partners:
            existing_pos = self.env['purchase.order'].search([
                ('partner_id', '=', partner.id),
                ('origin_so_id', '=', self.id),
                ('state', 'not in', ['draft', 'cancel'])
            ])
            
            if existing_pos and not self.commission_processed:
                # Allow creation only if there are cancelled POs (indicating updates are allowed)
                cancelled_pos = self.env['purchase.order'].search([
                    ('partner_id', '=', partner.id),
                    ('origin_so_id', '=', self.id),
                    ('state', '=', 'cancel')
                ])
                
                if not cancelled_pos:
                    raise ValidationError(
                        f"Cannot create new purchase orders for partner '{partner.name}' "
                        f"because confirmed POs already exist: {', '.join(existing_pos.mapped('name'))}. "
                        f"To update commissions, first cancel the existing POs."
                    )
        
        return True

    def _calculate_commission_amount(self, rate, commission_type, order):
        if commission_type == 'fixed':
            return rate
        elif commission_type == 'percent_unit_price':
            if order.order_line:
                return (rate / 100.0) * order.order_line[0].price_unit
            return 0.0
        elif commission_type == 'percent_untaxed_total':
            return (rate / 100.0) * order.amount_untaxed
        return 0.0

    @api.depends('amount_total', 'consultant_comm_percentage', 'manager_comm_percentage', 
                 'director_comm_percentage', 'second_agent_comm_percentage',
                 'broker_rate', 'broker_commission_type', 'referrer_rate', 'referrer_commission_type',
                 'cashback_rate', 'cashback_commission_type', 'other_external_rate', 'other_external_commission_type',
                 'agent1_rate', 'agent1_commission_type', 'agent2_rate', 'agent2_commission_type',
                 'manager_rate', 'manager_commission_type', 'director_rate', 'director_commission_type',
                 'order_line.price_unit', 'order_line.price_subtotal', 'amount_untaxed')
    def _compute_commissions(self):
        """Compute commission amounts and company shares."""
        for order in self:
            base_amount = order.amount_total

            # Legacy commission calculations (removed default computation to prevent conflicts)
            # Only calculate if explicitly set by user
            if order.consultant_id and order.consultant_comm_percentage > 0:
                order.salesperson_commission = (order.consultant_comm_percentage / 100) * base_amount
            else:
                order.salesperson_commission = 0.0
                
            if order.manager_id and order.manager_comm_percentage > 0:
                order.manager_commission = (order.manager_comm_percentage / 100) * base_amount
            else:
                order.manager_commission = 0.0
                
            if order.second_agent_id and order.second_agent_comm_percentage > 0:
                order.second_agent_commission = (order.second_agent_comm_percentage / 100) * base_amount
            else:
                order.second_agent_commission = 0.0
                
            if order.director_id and order.director_comm_percentage > 0:
                order.director_commission = (order.director_comm_percentage / 100) * base_amount
            else:
                order.director_commission = 0.0

            # External commissions (modern structure)
            order.broker_amount = self._calculate_commission_amount(order.broker_rate, order.broker_commission_type, order)
            order.referrer_amount = self._calculate_commission_amount(order.referrer_rate, order.referrer_commission_type, order)
            order.cashback_amount = self._calculate_commission_amount(order.cashback_rate, order.cashback_commission_type, order)
            order.other_external_amount = self._calculate_commission_amount(order.other_external_rate, order.other_external_commission_type, order)

            # Internal commissions (modern structure)
            order.agent1_amount = self._calculate_commission_amount(order.agent1_rate, order.agent1_commission_type, order)
            order.agent2_amount = self._calculate_commission_amount(order.agent2_rate, order.agent2_commission_type, order)
            order.manager_amount = self._calculate_commission_amount(order.manager_rate, order.manager_commission_type, order)
            order.director_amount = self._calculate_commission_amount(order.director_rate, order.director_commission_type, order)

            # Calculate totals
            order.total_external_commission_amount = (
                order.broker_amount + order.referrer_amount + 
                order.cashback_amount + order.other_external_amount
            )

            order.total_internal_commission_amount = (
                order.agent1_amount + order.agent2_amount + 
                order.manager_amount + order.director_amount +
                order.salesperson_commission + order.manager_commission + 
                order.second_agent_commission + order.director_commission
            )

            order.total_commission_amount = (
                order.total_external_commission_amount + order.total_internal_commission_amount
            )

            # Company share calculations
            order.company_share = base_amount - order.total_commission_amount
            order.net_company_share = order.company_share

    @api.depends('amount_total')
    def _compute_sales_value(self):
        for order in self:
            order.sales_value = order.amount_total

    @api.constrains('consultant_comm_percentage', 'manager_comm_percentage', 
                    'second_agent_comm_percentage', 'director_comm_percentage')
    def _check_commission_percentages(self):
        """Validate commission percentages."""
        for order in self:
            # Check legacy percentages
            total_percentage = (order.consultant_comm_percentage + 
                              order.manager_comm_percentage + 
                              order.second_agent_comm_percentage + 
                              order.director_comm_percentage)
            
            if total_percentage > 100:
                raise ValidationError("Total commission percentages cannot exceed 100%")
            
            for percentage in [order.consultant_comm_percentage, order.manager_comm_percentage,
                             order.second_agent_comm_percentage, order.director_comm_percentage]:
                if percentage < 0:
                    raise ValidationError("Commission percentages cannot be negative")

    def _get_or_create_commission_product(self, commission_type="Sales Commission"):
        """Get or create commission product."""
        product = self.env['product.product'].search([
            ('name', '=', commission_type),
            ('type', '=', 'service')
        ], limit=1)
        
        if not product:
            product = self.env['product.product'].create({
                'name': commission_type,
                'type': 'service',
                'categ_id': self.env.ref('product.product_category_all').id,
                'list_price': 0.0,
                'standard_price': 0.0,
                'sale_ok': False,
                'purchase_ok': True,
                'detailed_type': 'service',
            })
            _logger.info(f"Created commission product: {commission_type}")
        
        return product

    def _prepare_purchase_order_vals(self, partner, product, amount, description):
        """Prepare values for purchase order creation."""
        if not partner:
            raise UserError("Partner is required for purchase order creation")
        
        if amount <= 0:
            raise UserError("Commission amount must be greater than zero")
        
        # Prepare base values
        vals = {
            'partner_id': partner.id,
            'date_order': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'origin': self.name,
            'description': description,
            'origin_so_id': self.id,
            'commission_posted': False,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': description,
                'product_qty': 1.0,
                'product_uom': product.uom_id.id,
                'price_unit': amount,
                'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
            })]
        }
        
        # Add vendor reference from customer reference if available
        if self.client_order_ref:
            vals['partner_ref'] = self.client_order_ref
            _logger.info(
                f"Adding vendor reference '{self.client_order_ref}' to commission PO for {partner.name}"
            )
        
        return vals

    def _get_all_commission_partners(self):
        """Get all commission partner IDs from this sale order."""
        self.ensure_one()
        partner_ids = []
        
        # Legacy commission partners
        if self.consultant_id:
            partner_ids.append(self.consultant_id.id)
        if self.manager_id:
            partner_ids.append(self.manager_id.id)
        if self.director_id:
            partner_ids.append(self.director_id.id)
        if self.second_agent_id:
            partner_ids.append(self.second_agent_id.id)
        
        # External commission partners
        if self.broker_partner_id:
            partner_ids.append(self.broker_partner_id.id)
        if self.referrer_partner_id:
            partner_ids.append(self.referrer_partner_id.id)
        if self.cashback_partner_id:
            partner_ids.append(self.cashback_partner_id.id)
        if self.other_external_partner_id:
            partner_ids.append(self.other_external_partner_id.id)
        
        # Internal commission partners
        if self.agent1_partner_id:
            partner_ids.append(self.agent1_partner_id.id)
        if self.agent2_partner_id:
            partner_ids.append(self.agent2_partner_id.id)
        if self.manager_partner_id:
            partner_ids.append(self.manager_partner_id.id)
        if self.director_partner_id:
            partner_ids.append(self.director_partner_id.id)
        
        return list(set(partner_ids))  # Remove duplicates

    def action_view_commission_pos(self):
        """Action to view commission purchase orders."""
        self.ensure_one()
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        
        if self.purchase_order_count == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = self.purchase_order_ids[0].id
        else:
            action['domain'] = [('id', 'in', self.purchase_order_ids.ids)]
            action['context'] = {
                'default_origin_so_id': self.id,
                'search_default_commission_pos': 1,
            }
        
        action['context'].update({
            'create': False,  # Don't allow creating POs from this view
        })
        
        return action

    def _get_commission_entries(self):
        """Get all commission entries that need purchase orders."""
        self.ensure_one()
        commissions = []

        # Legacy commissions
        if self.consultant_id and self.salesperson_commission > 0:
            commissions.append({
                'partner': self.consultant_id,
                'amount': self.salesperson_commission,
                'description': f"Consultant Commission for SO: {self.name}"
            })

        if self.manager_id and self.manager_commission > 0:
            commissions.append({
                'partner': self.manager_id,
                'amount': self.manager_commission,
                'description': f"Manager Commission for SO: {self.name}"
            })

        if self.second_agent_id and self.second_agent_commission > 0:
            commissions.append({
                'partner': self.second_agent_id,
                'amount': self.second_agent_commission,
                'description': f"Second Agent Commission for SO: {self.name}"
            })

        if self.director_id and self.director_commission > 0:
            commissions.append({
                'partner': self.director_id,
                'amount': self.director_commission,
                'description': f"Director Commission for SO: {self.name}"
            })

        # External commissions
        if self.broker_partner_id and self.broker_amount > 0:
            commissions.append({
                'partner': self.broker_partner_id,
                'amount': self.broker_amount,
                'description': f"Broker Commission for SO: {self.name}"
            })

        if self.referrer_partner_id and self.referrer_amount > 0:
            commissions.append({
                'partner': self.referrer_partner_id,
                'amount': self.referrer_amount,
                'description': f"Referrer Commission for SO: {self.name}"
            })

        if self.cashback_partner_id and self.cashback_amount > 0:
            commissions.append({
                'partner': self.cashback_partner_id,
                'amount': self.cashback_amount,
                'description': f"Cashback for SO: {self.name}"
            })

        if self.other_external_partner_id and self.other_external_amount > 0:
            commissions.append({
                'partner': self.other_external_partner_id,
                'amount': self.other_external_amount,
                'description': f"Other External Commission for SO: {self.name}"
            })

        # Internal commissions
        if self.agent1_partner_id and self.agent1_amount > 0:
            commissions.append({
                'partner': self.agent1_partner_id,
                'amount': self.agent1_amount,
                'description': f"Agent 1 Commission for SO: {self.name}"
            })

        if self.agent2_partner_id and self.agent2_amount > 0:
            commissions.append({
                'partner': self.agent2_partner_id,
                'amount': self.agent2_amount,
                'description': f"Agent 2 Commission for SO: {self.name}"
            })

        if self.manager_partner_id and self.manager_amount > 0:
            commissions.append({
                'partner': self.manager_partner_id,
                'amount': self.manager_amount,
                'description': f"Manager Commission for SO: {self.name}"
            })

        if self.director_partner_id and self.director_amount > 0:
            commissions.append({
                'partner': self.director_partner_id,
                'amount': self.director_amount,
                'description': f"Director Commission for SO: {self.name}"
            })

        return commissions

    def _create_commission_purchase_orders(self):
        """Create purchase orders for all applicable commissions."""
        self.ensure_one()
        
        if self.commission_processed:
            raise UserError("Commissions have already been processed for this order.")
        
        if self.amount_total <= 0:
            raise UserError("Cannot process commissions for orders with zero or negative amounts.")
        
        # Check PO creation constraints (cancellation logic)
        self._check_po_creation_constraints()
        
        # Update status
        self.commission_status = 'calculated'
        
        try:
            # Get commission product
            commission_product = self._get_or_create_commission_product()
            created_pos = []

            # Get all commission entries
            commissions = self._get_commission_entries()

            # Create purchase orders
            for commission in commissions:
                po_vals = self._prepare_purchase_order_vals(
                    partner=commission['partner'],
                    product=commission_product,
                    amount=commission['amount'],
                    description=commission['description']
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po)
                _logger.info(f"Created commission PO: {po.name}")

            # Mark as processed
            self.commission_processed = True
            
            if created_pos:
                message = f"Successfully created {len(created_pos)} commission purchase orders with total amount {sum(po.amount_total for po in created_pos)}"
                self.message_post(body=message)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.commission_status = 'draft'
                raise UserError("No commissions were created. Please check commission settings.")
                
        except Exception as e:
            self.commission_status = 'draft'
            _logger.error(f"Error creating commission purchase orders: {str(e)}")
            raise UserError(f"Failed to process commissions: {str(e)}")

    def action_process_commissions(self):
        """Manual action to process commissions."""
        for order in self:
            order._create_commission_purchase_orders()
        return True

    def action_confirm_commissions(self):
        """Confirm commissions: set status to 'confirmed' if commissions are processed."""
        for order in self:
            if not order.commission_processed:
                raise UserError("You must calculate/process commissions before confirming.")
            order.commission_status = 'confirmed'
            order.message_post(body="Commissions confirmed.")
        return True

    def action_reset_commissions(self):
        """Reset commission status to draft and allow recalculation."""
        for order in self:
            # Check if any POs are already confirmed
            confirmed_pos = order.purchase_order_ids.filtered(
                lambda po: po.state not in ['draft', 'cancel']
            )
            if confirmed_pos:
                raise UserError(
                    f"Cannot reset commissions because purchase orders are already confirmed: "
                    f"{', '.join(confirmed_pos.mapped('name'))}"
                )
            
            # Cancel and delete draft POs
            draft_pos = order.purchase_order_ids.filtered(lambda po: po.state == 'draft')
            if draft_pos:
                draft_pos.button_cancel()
                draft_pos.unlink()
            
            order.commission_status = 'draft'
            order.commission_processed = False
            order.message_post(body="Commission status reset to draft. Purchase orders deleted.")
        return True

    def action_cancel_partner_pos(self, partner_id):
        """Cancel all purchase orders for a specific partner (used for commission updates)."""
        self.ensure_one()
        if not partner_id:
            raise UserError("Partner ID is required to cancel purchase orders.")
        
        partner_pos = self.purchase_order_ids.filtered(
            lambda po: po.partner_id.id == partner_id and po.state not in ['cancel']
        )
        
        if not partner_pos:
            return True  # No POs to cancel
        
        # Check if any are already confirmed
        confirmed_pos = partner_pos.filtered(lambda po: po.state not in ['draft', 'sent'])
        if confirmed_pos:
            raise UserError(
                f"Cannot cancel confirmed purchase orders for partner: "
                f"{', '.join(confirmed_pos.mapped('name'))}. "
                f"Please handle these manually through the Purchase module."
            )
        
        # Cancel draft/sent POs
        cancelable_pos = partner_pos.filtered(lambda po: po.state in ['draft', 'sent'])
        if cancelable_pos:
            cancelable_pos.button_cancel()
            self.message_post(
                body=f"Cancelled {len(cancelable_pos)} purchase orders for partner "
                     f"{self.env['res.partner'].browse(partner_id).name}: "
                     f"{', '.join(cancelable_pos.mapped('name'))}"
            )
        
        return True

    def action_confirm(self):
        """Override Sale Order confirmation."""
        result = super(SaleOrder, self).action_confirm()
        
        # Auto-process commissions on confirmation if configured
        auto_process = self.env['ir.config_parameter'].sudo().get_param(
            'commission_ax.auto_process_on_confirm', default=False
        )
        
        if auto_process and auto_process.lower() == 'true':
            for order in self:
                if not order.commission_processed:
                    try:
                        order._create_commission_purchase_orders()
                    except Exception as e:
                        _logger.warning(f"Auto commission processing failed for {order.name}: {str(e)}")
        
        return result

    def write(self, vals):
        """Override write to recompute commissions when relevant fields change."""
        # Check partner PO cancellation requirements before updating commission fields
        commission_partner_fields = [
            'broker_partner_id', 'referrer_partner_id', 'cashback_partner_id', 
            'other_external_partner_id', 'agent1_partner_id', 'agent2_partner_id',
            'manager_partner_id', 'director_partner_id',
            'consultant_id', 'manager_id', 'director_id', 'second_agent_id'
        ]
        
        # Check if any commission partner fields are being changed
        if any(field in vals for field in commission_partner_fields):
            for order in self:
                for field in commission_partner_fields:
                    if field in vals:
                        old_partner_id = getattr(order, field, False)
                        new_partner_id = vals.get(field)
                        
                        # If partner is changing and there are existing POs, check cancellation requirement
                        if old_partner_id and old_partner_id != new_partner_id:
                            old_partner = self.env['res.partner'].browse(old_partner_id)
                            order._check_partner_po_cancellation_required(old_partner)
        
        result = super(SaleOrder, self).write(vals)
        
        # Reset commission processing if commission-related fields are changed
        commission_fields = [
            'consultant_id', 'consultant_comm_percentage',
            'manager_id', 'manager_comm_percentage',
            'second_agent_id', 'second_agent_comm_percentage',
            'director_id', 'director_comm_percentage',
            'broker_partner_id', 'broker_rate', 'broker_commission_type',
            'referrer_partner_id', 'referrer_rate', 'referrer_commission_type',
            'cashback_partner_id', 'cashback_rate', 'cashback_commission_type',
            'other_external_partner_id', 'other_external_rate', 'other_external_commission_type',
            'agent1_partner_id', 'agent1_rate', 'agent1_commission_type',
            'agent2_partner_id', 'agent2_rate', 'agent2_commission_type',
            'manager_partner_id', 'manager_rate', 'manager_commission_type',
            'director_partner_id', 'director_rate', 'director_commission_type'
        ]
        
        if any(field in vals for field in commission_fields):
            for order in self:
                if order.commission_processed and order.commission_status != 'draft':
                    order.write({
                        'commission_processed': False,
                        'commission_status': 'draft'
                    })
                    order.message_post(
                        body="Commission settings changed. Please recalculate commissions. "
                             "Note: If you changed partner assignments, ensure related POs are cancelled first."
                    )
        
        return result

    @api.model
    def _cron_auto_process_commissions(self):
        """Scheduled action to auto-process commissions for invoiced orders."""
        orders = self.search([
            ('state', 'in', ['sale', 'done']),
            ('commission_processed', '=', False),
            ('invoice_status', '=', 'invoiced')
        ])
        
        for order in orders:
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            if posted_invoices:
                try:
                    order._create_commission_purchase_orders()
                    _logger.info(f"Auto-processed commissions for order {order.name}")
                except Exception as e:
                    _logger.error(f"Failed to auto-process commissions for {order.name}: {str(e)}")

    def unlink(self):
        """Override unlink to handle related purchase orders."""
        for order in self:
            if order.purchase_order_ids:
                confirmed_pos = order.purchase_order_ids.filtered(
                    lambda po: po.state not in ['draft', 'cancel']
                )
                if confirmed_pos:
                    raise UserError(
                        f"Cannot delete sale order {order.name} because it has "
                        f"confirmed commission purchase orders: {', '.join(confirmed_pos.mapped('name'))}"
                    )
                draft_pos = order.purchase_order_ids.filtered(lambda po: po.state == 'draft')
                draft_pos.button_cancel()
        
        return super(SaleOrder, self).unlink()