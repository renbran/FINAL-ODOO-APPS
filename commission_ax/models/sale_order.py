from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_comm_percentage = fields.Float(string="Consultant Commission (%)", default=0.0)
    salesperson_commission = fields.Monetary(string="Consultant Commission Amount", compute="_compute_commissions", store=True)

    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_comm_percentage = fields.Float(string="Manager Commission (%)", default=0.0)
    manager_commission = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_id = fields.Many2one('res.partner', string="Director")
    director_comm_percentage = fields.Float(string="Director Commission (%)", default=3.0)
    director_commission = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)

    company_share = fields.Monetary(string="Company Share", compute="_compute_commissions", store=True)
    net_company_share = fields.Monetary(string="Net Company Share", compute="_compute_commissions", store=True)

    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    commission_processed = fields.Boolean(string="Commissions Processed", default=False)
    commission_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Commission Processing Status", default='not_started')

    @api.depends('amount_total', 'consultant_comm_percentage', 'manager_comm_percentage', 'director_comm_percentage')
    def _compute_commissions(self):
        """Compute commission amounts and company shares."""
        for order in self:
            # Consultant Commission
            order.salesperson_commission = (order.consultant_comm_percentage / 100) * order.amount_total

            # Manager Commission
            order.manager_commission = (order.manager_comm_percentage / 100) * order.amount_total

            # Company Share
            total_commissions = order.salesperson_commission + order.manager_commission
            order.company_share = order.amount_total - total_commissions

            # Director Commission
            if not order.director_comm_percentage:
                order.director_comm_percentage = 3.0  # Default to 3%
            order.director_commission = (order.director_comm_percentage / 100) * order.company_share

            # Net Company Share
            order.net_company_share = order.company_share - order.director_commission

    def _get_commission_product(self, xml_id):
        """Helper method to get commission product or create one if not found."""
        try:
            product = self.env.ref(xml_id)
        except ValueError:
            # Handle case where product is not found by XML ID
            product = self.env['product.product'].search([('name', '=', xml_id.split('.')[-1].replace('_', ' ').title())], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': xml_id.split('.')[-1].replace('_', ' ').title(),
                    'type': 'service',
                    'list_price': 100.0,  # Default price, adjust if needed
                })
        return product

    def _prepare_purchase_order_vals(self, partner, product, amount, description):
        """Prepare values for auto-creation of Purchase Orders."""
        return {
            'partner_id': partner.id,
            'date_order': fields.Date.today(),
            'order_line': [
                (0, 0, {
                    'product_id': product.id,
                    'name': description,
                    'product_qty': 1.0,
                    'product_uom': product.uom_id.id,
                    'price_unit': amount,
                })
            ],
            'origin_so_id': self.id,
        }

    def _auto_generate_purchase_orders(self):
        """Auto-generate Purchase Orders for commissions."""
        self.ensure_one()
        
        # Update commission status
        self.commission_status = 'in_progress'
        
        # Get commission products or create if they don't exist
        product_consultant = self._get_commission_product('product.product_Sales_Commission')
        product_manager = self._get_commission_product('product.product_Sales_Commission')
        product_director = self._get_commission_product('product.product_Sales_Commission')

        # Consultant Commission
        if self.consultant_id and self.salesperson_commission > 0:
            po_vals = self._prepare_purchase_order_vals(
                partner=self.consultant_id,
                product=product_consultant,
                amount=self.salesperson_commission,
                description=f"Consultant Commission for SO: {self.name}",
            )
            self.env['purchase.order'].create(po_vals)

        # Manager Commission
        if self.manager_id and self.manager_commission > 0:
            po_vals = self._prepare_purchase_order_vals(
                partner=self.manager_id,
                product=product_manager,
                amount=self.manager_commission,
                description=f"Manager Commission for SO: {self.name}",
            )
            self.env['purchase.order'].create(po_vals)

        # Director Commission
        if self.director_id and self.director_commission > 0:
            po_vals = self._prepare_purchase_order_vals(
                partner=self.director_id,
                product=product_director,
                amount=self.director_commission,
                description=f"Director Commission for SO: {self.name}",
            )
            self.env['purchase.order'].create(po_vals)

        # Mark as processed
        self.commission_processed = True
        self.commission_status = 'completed'

    def action_process_commissions(self):
        """Manual action to process commissions."""
        for order in self:
            order._auto_generate_purchase_orders()
        return True

    def action_confirm(self):
        """Extend Sale Order Confirmation."""
        return super(SaleOrder, self).action_confirm()

    def _process_commissions_on_invoice_post(self, invoice):
        """Process commissions when the invoice is posted."""
        if invoice.state == 'posted' and not self.commission_processed:
            try:
                self._auto_generate_purchase_orders()
            except Exception as e:
                # Log the error and set status to not started
                self.env.cr.rollback()
                self.commission_status = 'not_started'
                raise e

    def action_invoice(self):
        """Override the action_invoice method to process commissions on invoice posting."""
        res = super(SaleOrder, self).action_invoice()
        for order in self:
            for invoice in order.invoice_ids:
                order._process_commissions_on_invoice_post(invoice)
        return res