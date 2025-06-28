from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Purchase Orders")

    x_sale_value = fields.Float(string="Sale Value")
    untaxed_total = fields.Float(string="Untaxed Total", readonly=True, 
                                compute='_compute_untaxed_total', store=True)
    
    project_id = fields.Many2one('project.project', string="Project", readonly=False)
    x_unit1 = fields.Many2one('property.unit', string="Unit", readonly=False)
    commission_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], default='pending', string="Commission Status")
    commission_processed = fields.Boolean(string="Commission Processed")

    # Total and shares
    total_commission_amount = fields.Float(string="Total Commission Amount", compute='_compute_total_commission', store=True)
    company_share = fields.Float(string="Company Share", compute='_compute_company_share', store=True)
    net_company_share = fields.Float(string="Net Company Share", compute='_compute_company_share', store=True)

    # External Party
    external_party_id = fields.Many2one('res.partner', string="External Party", ondelete='set null')
    external_party_calculation_type = fields.Selection([
        ('percentage', 'Percentage'), 
        ('fixed', 'Fixed'),
        ('by_sales_value', 'By Sales Value')
    ], string="Calculation Type")
    external_party_percentage = fields.Float(string="Rate (%)")
    external_party_fixed_amount = fields.Float(string="Fixed Amount")
    external_party_commission = fields.Float(string="Commission Amount", compute='_compute_external_party_commission', store=True)
    external_party_base_amount = fields.Float(string="Base Amount")

    # Consultant
    consultant_id = fields.Many2one('res.partner', string="Consultant", ondelete='set null')
    consultant_calculation_type = fields.Selection([
        ('percentage', 'Percentage'), 
        ('fixed', 'Fixed'),
        ('by_untaxed', 'By Untaxed Amount')
    ], string="Calculation Type")
    consultant_percentage = fields.Float(string="Rate (%)")
    consultant_fixed_amount = fields.Float(string="Fixed Amount")
    consultant_commission = fields.Float(string="Commission Amount", compute='_compute_consultant_commission', store=True)
    consultant_base_amount = fields.Float(string="Base Amount")

    # Second Agent
    second_agent_id = fields.Many2one('res.partner', string="Second Agent", ondelete='set null')
    second_agent_calculation_type = fields.Selection([
        ('percentage', 'Percentage'), 
        ('fixed', 'Fixed'),
        ('by_sales_value', 'By Sales Value'),
        ('by_untaxed', 'By Untaxed Amount')
    ], string="Calculation Type")
    second_agent_percentage = fields.Float(string="Rate (%)")
    second_agent_fixed_amount = fields.Float(string="Fixed Amount")
    second_agent_commission = fields.Float(string="Commission Amount", compute='_compute_second_agent_commission', store=True)
    second_agent_base_amount = fields.Float(string="Base Amount")

    # Manager
    manager_id = fields.Many2one('res.partner', string="Manager", ondelete='set null')
    manager_calculation_type = fields.Selection([
        ('percentage', 'Percentage'), 
        ('fixed', 'Fixed'),
        ('by_sales_value', 'By Sales Value'),
        ('by_untaxed', 'By Untaxed Amount')
    ], string="Calculation Type")
    manager_percentage = fields.Float(string="Rate (%)")
    manager_fixed_amount = fields.Float(string="Fixed Amount")
    manager_commission = fields.Float(string="Commission Amount", compute='_compute_manager_commission', store=True)
    manager_base_amount = fields.Float(string="Base Amount")

    # Director
    director_id = fields.Many2one('res.partner', string="Director", ondelete='set null')
    director_calculation_type = fields.Selection([
        ('percentage', 'Percentage'), 
        ('fixed', 'Fixed'),
        ('by_sales_value', 'By Sales Value'),
        ('by_untaxed', 'By Untaxed Amount')
    ], string="Calculation Type")
    director_percentage = fields.Float(string="Rate (%)")
    director_fixed_amount = fields.Float(string="Fixed Amount")
    director_commission = fields.Float(string="Commission Amount", compute='_compute_director_commission', store=True)
    director_base_amount = fields.Float(string="Base Amount")

    @api.depends('amount_untaxed')
    def _compute_untaxed_total(self):
        for order in self:
            order.untaxed_total = order.amount_untaxed

    @api.depends('external_party_calculation_type', 'external_party_percentage', 'external_party_fixed_amount', 
                'external_party_base_amount', 'x_sale_value', 'untaxed_total')
    def _compute_external_party_commission(self):
        for order in self:
            if not order.external_party_id or not order.external_party_id.exists():
                order.external_party_commission = 0.0
                continue
                
            if order.external_party_calculation_type == 'percentage':
                base = order.external_party_base_amount or 0.0
                order.external_party_commission = base * (order.external_party_percentage / 100.0)
            elif order.external_party_calculation_type == 'fixed':
                order.external_party_commission = order.external_party_fixed_amount or 0.0
            elif order.external_party_calculation_type == 'by_sales_value':
                order.external_party_commission = order.x_sale_value * (order.external_party_percentage / 100.0)
            else:
                order.external_party_commission = 0.0

    @api.depends('consultant_calculation_type', 'consultant_percentage', 'consultant_fixed_amount', 
                'consultant_base_amount', 'x_sale_value', 'untaxed_total')
    def _compute_consultant_commission(self):
        for order in self:
            if not order.consultant_id or not order.consultant_id.exists():
                order.consultant_commission = 0.0
                continue
                
            if order.consultant_calculation_type == 'percentage':
                base = order.consultant_base_amount or 0.0
                order.consultant_commission = base * (order.consultant_percentage / 100.0)
            elif order.consultant_calculation_type == 'fixed':
                order.consultant_commission = order.consultant_fixed_amount or 0.0
            elif order.consultant_calculation_type == 'by_untaxed':
                order.consultant_commission = order.untaxed_total * (order.consultant_percentage / 100.0)
            else:
                order.consultant_commission = 0.0

    @api.depends('second_agent_calculation_type', 'second_agent_percentage', 'second_agent_fixed_amount', 
                'second_agent_base_amount', 'x_sale_value', 'untaxed_total')
    def _compute_second_agent_commission(self):
        for order in self:
            if not order.second_agent_id or not order.second_agent_id.exists():
                order.second_agent_commission = 0.0
                continue
                
            if order.second_agent_calculation_type == 'percentage':
                base = order.second_agent_base_amount or 0.0
                order.second_agent_commission = base * (order.second_agent_percentage / 100.0)
            elif order.second_agent_calculation_type == 'fixed':
                order.second_agent_commission = order.second_agent_fixed_amount or 0.0
            elif order.second_agent_calculation_type == 'by_sales_value':
                order.second_agent_commission = order.x_sale_value * (order.second_agent_percentage / 100.0)
            elif order.second_agent_calculation_type == 'by_untaxed':
                order.second_agent_commission = order.untaxed_total * (order.second_agent_percentage / 100.0)
            else:
                order.second_agent_commission = 0.0

    @api.depends('manager_calculation_type', 'manager_percentage', 'manager_fixed_amount', 
                'manager_base_amount', 'x_sale_value', 'untaxed_total')
    def _compute_manager_commission(self):
        for order in self:
            if not order.manager_id or not order.manager_id.exists():
                order.manager_commission = 0.0
                continue
                
            if order.manager_calculation_type == 'percentage':
                base = order.manager_base_amount or 0.0
                order.manager_commission = base * (order.manager_percentage / 100.0)
            elif order.manager_calculation_type == 'fixed':
                order.manager_commission = order.manager_fixed_amount or 0.0
            elif order.manager_calculation_type == 'by_sales_value':
                order.manager_commission = order.x_sale_value * (order.manager_percentage / 100.0)
            elif order.manager_calculation_type == 'by_untaxed':
                order.manager_commission = order.untaxed_total * (order.manager_percentage / 100.0)
            else:
                order.manager_commission = 0.0

    @api.depends('director_calculation_type', 'director_percentage', 'director_fixed_amount', 
                'director_base_amount', 'x_sale_value', 'untaxed_total')
    def _compute_director_commission(self):
        for order in self:
            if not order.director_id or not order.director_id.exists():
                order.director_commission = 0.0
                continue
                
            if order.director_calculation_type == 'percentage':
                base = order.director_base_amount or 0.0
                order.director_commission = base * (order.director_percentage / 100.0)
            elif order.director_calculation_type == 'fixed':
                order.director_commission = order.director_fixed_amount or 0.0
            elif order.director_calculation_type == 'by_sales_value':
                order.director_commission = order.x_sale_value * (order.director_percentage / 100.0)
            elif order.director_calculation_type == 'by_untaxed':
                order.director_commission = order.untaxed_total * (order.director_percentage / 100.0)
            else:
                order.director_commission = 0.0

    @api.depends('external_party_commission', 'consultant_commission', 'second_agent_commission',
                'manager_commission', 'director_commission')
    def _compute_total_commission(self):
        for order in self:
            order.total_commission_amount = sum([
                order.external_party_commission,
                order.consultant_commission,
                order.second_agent_commission,
                order.manager_commission,
                order.director_commission
            ])

    @api.depends('x_sale_value', 'total_commission_amount')
    def _compute_company_share(self):
        for order in self:
            # Ensure commissions don't exceed the total amount
            total_available = max(order.x_sale_value, order.amount_total)
            
            if order.total_commission_amount > total_available:
                # Scale down commissions proportionally
                scale_factor = total_available / order.total_commission_amount if order.total_commission_amount else 0
                order.company_share = 0
            else:
                order.company_share = total_available - order.total_commission_amount
                
            order.net_company_share = order.company_share

    def action_process_commissions(self):
        for order in self:
            # Verify base amounts before processing
            self._verify_and_update_commissions()
            
            # Create purchase orders for each role with commission amount
            self._create_commission_purchase_orders()

            order.commission_status = 'completed'
            order.commission_processed = True
    
    def _verify_and_update_commissions(self):
        """Verify and adjust commission amounts if needed"""
        self.ensure_one()
        total_available = max(self.x_sale_value, self.amount_total)
        
        if self.total_commission_amount > total_available:
            # If commissions exceed available amount, scale down proportionally
            scale_factor = total_available / self.total_commission_amount if self.total_commission_amount else 0
            return scale_factor
        return 1.0
            
    def _create_commission_purchase_orders(self):
        """Create purchase orders for each role that has a commission amount."""
        self.ensure_one()
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']
        ProductProduct = self.env['product.product']
        
        # Get or create a product for commissions
        commission_product = ProductProduct.search([('name', '=', 'Commission Payment')], limit=1)
        if not commission_product:
            commission_product = ProductProduct.create({
                'name': 'Commission Payment',
                'type': 'service',
                'purchase_ok': True,
                'sale_ok': False,
            })
        
        # Apply scale factor if needed
        scale_factor = self._verify_and_update_commissions()
            
        # List of commission recipients
        commission_recipients = [
            {
                'partner': self.external_party_id, 
                'amount': self.external_party_commission * scale_factor,
                'title': 'External Party'
            },
            {
                'partner': self.consultant_id, 
                'amount': self.consultant_commission * scale_factor,
                'title': 'Consultant'
            },
            {
                'partner': self.second_agent_id, 
                'amount': self.second_agent_commission * scale_factor,
                'title': 'Second Agent'
            },
            {
                'partner': self.manager_id, 
                'amount': self.manager_commission * scale_factor,
                'title': 'Manager'
            },
            {
                'partner': self.director_id, 
                'amount': self.director_commission * scale_factor,
                'title': 'Director'
            },
        ]
        
        for recipient in commission_recipients:
            if recipient['partner'] and recipient['partner'].exists() and recipient['amount'] > 0:
                # Create detailed description from project_id and x_unit1 if they exist
                project_name = self.project_id.name if self.project_id else ""
                unit_name = self.x_unit1.name if self.x_unit1 else ""
                
                reference_details = f"{self.name}"
                if project_name:
                    reference_details += f" - {project_name}"
                if unit_name:
                    reference_details += f" - {unit_name}"
                
                description = f"Commission for {reference_details} - {recipient['title']}"
                
                # Create purchase order
                po_vals = {
                    'partner_id': recipient['partner'].id,
                    'origin_so_id': self.id,
                    'origin': self.name,
                    'notes': description,
                    'date_order': fields.Datetime.now(),
                }
                
                purchase_order = PurchaseOrder.create(po_vals)
                
                # Create purchase order line
                po_line_vals = {
                    'order_id': purchase_order.id,
                    'product_id': commission_product.id,
                    'name': description,
                    'product_qty': 1,
                    'product_uom': commission_product.uom_id.id,
                    'price_unit': recipient['amount'],
                    'date_planned': fields.Datetime.now(),
                }
                PurchaseOrderLine.create(po_line_vals)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    origin_so_id = fields.Many2one('sale.order', string='Source Sale Order', ondelete='set null')
    commission_details = fields.Char(string='Commission Details')
    commission_posted = fields.Boolean(string='Commission Posted', default=False)
    
    @api.model
    def _check_related_invoices(self):
        """
        Scheduled action to process commissions when related invoices are posted
        """
        sale_orders = self.env['sale.order'].search([
            ('commission_status', '=', 'pending'),
            ('invoice_ids.state', '=', 'posted')
        ])
        
        for order in sale_orders:
            order.action_process_commissions()