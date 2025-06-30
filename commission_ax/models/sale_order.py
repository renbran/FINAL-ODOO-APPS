from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Existing fields
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_comm_percentage = fields.Float(string="Consultant Commission (%)", default=0.0)
    salesperson_commission = fields.Monetary(string="Consultant Commission Amount", compute="_compute_commissions", store=True)

    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_comm_percentage = fields.Float(string="Manager Commission (%)", default=0.0)
    manager_commission = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_id = fields.Many2one('res.partner', string="Director")
    director_comm_percentage = fields.Float(string="Director Commission (%)", default=3.0)
    director_commission = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)

    # New fields for Second Agent
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    second_agent_comm_percentage = fields.Float(string="Second Agent Commission (%)", default=0.0)
    second_agent_commission = fields.Monetary(string="Second Agent Commission Amount", compute="_compute_commissions", store=True)

    company_share = fields.Monetary(string="Company Share", compute="_compute_commissions", store=True)
    net_company_share = fields.Monetary(string="Net Company Share", compute="_compute_commissions", store=True)

    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    commission_processed = fields.Boolean(string="Commissions Processed", default=False)
    commission_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Commission Processing Status", default='not_started')

    @api.depends('amount_total', 'consultant_comm_percentage', 'manager_comm_percentage', 'director_comm_percentage', 'second_agent_comm_percentage')
    def _compute_commissions(self):
        """Compute commission amounts and company shares."""
        for order in self:
            # Consultant Commission
            order.salesperson_commission = (order.consultant_comm_percentage / 100) * order.amount_total

            # Manager Commission
            order.manager_commission = (order.manager_comm_percentage / 100) * order.amount_total

            # Second Agent Commission
            order.second_agent_commission = (order.second_agent_comm_percentage / 100) * order.amount_total

            # Company Share
            total_commissions = order.salesperson_commission + order.manager_commission + order.second_agent_commission
            order.company_share = order.amount_total - total_commissions

            # Director Commission
            if not order.director_comm_percentage:
                order.director_comm_percentage = 3.0  # Default to 3%
            order.director_commission = (order.director_comm_percentage / 100) * order.company_share

            # Net Company Share
            order.net_company_share = order.company_share - order.director_commission

    def _get_commission_product(self):
        """Helper method to get commission product or create one if not found."""
        try:
            # Try to find existing commission product
            product = self.env.ref('commission_ax.product_sales_commission', raise_if_not_found=False)
            if not product:
                # Search for any commission product
                product = self.env['product.product'].search([
                    ('name', 'ilike', 'commission'),
                    ('type', '=', 'service')
                ], limit=1)
            
            if not product:
                # Create a new commission product
                product = self.env['product.product'].create({
                    'name': 'Sales Commission',
                    'type': 'service',
                    'list_price': 0.0,
                    'standard_price': 0.0,
                    'categ_id': self.env.ref('product.product_category_all').id,
                    'purchase_ok': True,
                    'sale_ok': False,
                })
                _logger.info(f"Created new commission product: {product.name}")
        except Exception as e:
            _logger.error(f"Error getting commission product: {str(e)}")
            # Fallback: create a simple service product
            product = self.env['product.product'].create({
                'name': 'Sales Commission',
                'type': 'service',
                'list_price': 0.0,
            })
        
        return product

    def _prepare_purchase_order_vals(self, partner, product, amount, description):
        """Prepare values for auto-creation of Purchase Orders."""
        return {
            'partner_id': partner.id,
            'date_order': fields.Date.today(),
            'description': description,
            'origin_so_id': self.id,
            'order_line': [
                (0, 0, {
                    'product_id': product.id,
                    'name': description,
                    'product_qty': 1.0,
                    'product_uom': product.uom_id.id,
                    'price_unit': amount,
                    'date_planned': fields.Date.today(),
                })
            ],
        }

    def _auto_generate_purchase_orders(self):
        """Auto-generate Purchase Orders for commissions."""
        self.ensure_one()
        
        if self.commission_processed:
            raise UserError("Commissions have already been processed for this sale order.")
        
        # Update commission status
        self.commission_status = 'in_progress'
        
        try:
            # Get commission product
            commission_product = self._get_commission_product()

            created_pos = []

            # Consultant Commission
            if self.consultant_id and self.salesperson_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.consultant_id,
                    product=commission_product,
                    amount=self.salesperson_commission,
                    description=f"Consultant Commission for SO: {self.name}",
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po.name)

            # Manager Commission
            if self.manager_id and self.manager_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.manager_id,
                    product=commission_product,
                    amount=self.manager_commission,
                    description=f"Manager Commission for SO: {self.name}",
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po.name)

            # Second Agent Commission
            if self.second_agent_id and self.second_agent_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.second_agent_id,
                    product=commission_product,
                    amount=self.second_agent_commission,
                    description=f"Second Agent Commission for SO: {self.name}",
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po.name)

            # Director Commission
            if self.director_id and self.director_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.director_id,
                    product=commission_product,
                    amount=self.director_commission,
                    description=f"Director Commission for SO: {self.name}",
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po.name)

            # Mark as processed
            self.commission_processed = True
            self.commission_status = 'completed'
            
            _logger.info(f"Created commission POs for SO {self.name}: {', '.join(created_pos)}")
            
        except Exception as e:
            self.commission_status = 'not_started'
            _logger.error(f"Error processing commissions for SO {self.name}: {str(e)}")
            raise UserError(f"Error processing commissions: {str(e)}")

    def action_process_commissions(self):
        """Manual action to process commissions."""
        for order in self:
            order._auto_generate_purchase_orders()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Commissions processed successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_confirm(self):
        """Extend Sale Order Confirmation."""
        result = super(SaleOrder, self).action_confirm()
        # Optionally auto-process commissions on confirmation
        # Uncomment the line below if you want automatic commission processing
        # self._auto_generate_purchase_orders()
        return result

    def _process_commissions_on_invoice_post(self, invoice):
        """Process commissions when the invoice is posted."""
        if invoice.state == 'posted' and not self.commission_processed:
            try:
                self._auto_generate_purchase_orders()
            except Exception as e:
                # Log the error and set status to not started
                self.commission_status = 'not_started'
                _logger.error(f"Error processing commissions on invoice post for SO {self.name}: {str(e)}")
                # Don't raise error here to prevent blocking invoice posting