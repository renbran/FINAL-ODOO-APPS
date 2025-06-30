from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Commission fields
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_comm_percentage = fields.Float(string="Consultant Commission (%)", default=0.0)
    salesperson_commission = fields.Monetary(string="Consultant Commission Amount", compute="_compute_commissions", store=True)

    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_comm_percentage = fields.Float(string="Manager Commission (%)", default=0.0)
    manager_commission = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_id = fields.Many2one('res.partner', string="Director")
    director_comm_percentage = fields.Float(string="Director Commission (%)", default=3.0)
    director_commission = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)

    # Second Agent fields
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    second_agent_comm_percentage = fields.Float(string="Second Agent Commission (%)", default=0.0)
    second_agent_commission = fields.Monetary(string="Second Agent Commission Amount", compute="_compute_commissions", store=True)

    # Computed fields
    company_share = fields.Monetary(string="Company Share", compute="_compute_commissions", store=True)
    net_company_share = fields.Monetary(string="Net Company Share", compute="_compute_commissions", store=True)

    # Sales Value field for commission computation
    sales_value = fields.Monetary(string="Sales Value", compute="_compute_sales_value", store=True)

    # Related fields
    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    commission_processed = fields.Boolean(string="Commissions Processed", default=False)
    commission_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Commission Processing Status", default='not_started')

    @api.depends('amount_total', 'consultant_comm_percentage', 'manager_comm_percentage', 
                 'director_comm_percentage', 'second_agent_comm_percentage')
    def _compute_commissions(self):
        """Compute commission amounts and company shares."""
        for order in self:
            # Consultant Commission
            order.salesperson_commission = (order.consultant_comm_percentage / 100) * order.amount_total

            # Manager Commission
            order.manager_commission = (order.manager_comm_percentage / 100) * order.amount_total

            # Second Agent Commission
            order.second_agent_commission = (order.second_agent_comm_percentage / 100) * order.amount_total

            # Company Share (after agent commissions)
            total_agent_commissions = (order.salesperson_commission + 
                                     order.manager_commission + 
                                     order.second_agent_commission)
            order.company_share = order.amount_total - total_agent_commissions

            # Director Commission (calculated on company share)
            if not order.director_comm_percentage:
                order.director_comm_percentage = 3.0  # Default to 3%
            order.director_commission = (order.director_comm_percentage / 100) * order.company_share

            # Net Company Share (after all commissions)
            order.net_company_share = order.company_share - order.director_commission

    @api.depends('amount_total')
    def _compute_sales_value(self):
        for order in self:
            # By default, use amount_total as sales value. Adjust logic if needed.
            order.sales_value = order.amount_total

    @api.constrains('consultant_comm_percentage', 'manager_comm_percentage', 
                    'second_agent_comm_percentage', 'director_comm_percentage')
    def _check_commission_percentages(self):
        """Validate commission percentages."""
        for order in self:
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
            # Create commission product if it doesn't exist
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
        
        return {
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

    def _create_commission_purchase_orders(self):
        """Create purchase orders for all applicable commissions."""
        self.ensure_one()
        
        if self.commission_processed:
            raise UserError("Commissions have already been processed for this order.")
        
        if self.amount_total <= 0:
            raise UserError("Cannot process commissions for orders with zero or negative amounts.")
        
        # Update status
        self.commission_status = 'in_progress'
        
        try:
            # Get commission product
            commission_product = self._get_or_create_commission_product()
            created_pos = []

            # Consultant Commission
            if self.consultant_id and self.salesperson_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.consultant_id,
                    product=commission_product,
                    amount=self.salesperson_commission,
                    description=f"Consultant Commission for SO: {self.name}"
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po)
                _logger.info(f"Created consultant commission PO: {po.name}")

            # Manager Commission
            if self.manager_id and self.manager_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.manager_id,
                    product=commission_product,
                    amount=self.manager_commission,
                    description=f"Manager Commission for SO: {self.name}"
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po)
                _logger.info(f"Created manager commission PO: {po.name}")

            # Second Agent Commission
            if self.second_agent_id and self.second_agent_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.second_agent_id,
                    product=commission_product,
                    amount=self.second_agent_commission,
                    description=f"Second Agent Commission for SO: {self.name}"
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po)
                _logger.info(f"Created second agent commission PO: {po.name}")

            # Director Commission
            if self.director_id and self.director_commission > 0:
                po_vals = self._prepare_purchase_order_vals(
                    partner=self.director_id,
                    product=commission_product,
                    amount=self.director_commission,
                    description=f"Director Commission for SO: {self.name}"
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po)
                _logger.info(f"Created director commission PO: {po.name}")

            # Mark as processed
            self.commission_processed = True
            self.commission_status = 'completed'
            
            if created_pos:
                message = f"Successfully created {len(created_pos)} commission purchase orders"
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
                self.commission_status = 'not_started'
                raise UserError("No commissions were created. Please check commission settings.")
                
        except Exception as e:
            self.commission_status = 'not_started'
            _logger.error(f"Error creating commission purchase orders: {str(e)}")
            raise UserError(f"Failed to process commissions: {str(e)}")

    def action_process_commissions(self):
        """Manual action to process commissions."""
        for order in self:
            order._create_commission_purchase_orders()
        return True

    def action_confirm(self):
        """Override Sale Order confirmation."""
        result = super(SaleOrder, self).action_confirm()
        
        # Auto-process commissions on confirmation if configured
        # This can be controlled by a system parameter if needed
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

    def _action_confirm(self):
        """Override internal confirmation method."""
        result = super(SaleOrder, self)._action_confirm()
        return result

    def write(self, vals):
        """Override write to recompute commissions when relevant fields change."""
        result = super(SaleOrder, self).write(vals)
        
        # Reset commission processing if commission-related fields are changed
        commission_fields = [
            'consultant_id', 'consultant_comm_percentage',
            'manager_id', 'manager_comm_percentage',
            'second_agent_id', 'second_agent_comm_percentage',
            'director_id', 'director_comm_percentage'
        ]
        
        if any(field in vals for field in commission_fields):
            for order in self:
                if order.commission_processed:
                    order.write({
                        'commission_processed': False,
                        'commission_status': 'not_started'
                    })
                    order.message_post(
                        body="Commission settings changed. Please reprocess commissions."
                    )
        
        return result

    @api.model
    def _cron_auto_process_commissions(self):
        """Scheduled action to auto-process commissions for invoiced orders."""
        # Find confirmed sale orders with posted invoices that haven't processed commissions
        orders = self.search([
            ('state', 'in', ['sale', 'done']),
            ('commission_processed', '=', False),
            ('invoice_status', '=', 'invoiced')
        ])
        
        for order in orders:
            # Check if any invoice is posted
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
                # Check if any PO is confirmed
                confirmed_pos = order.purchase_order_ids.filtered(
                    lambda po: po.state not in ['draft', 'cancel']
                )
                if confirmed_pos:
                    raise UserError(
                        f"Cannot delete sale order {order.name} because it has "
                        f"confirmed commission purchase orders: {', '.join(confirmed_pos.mapped('name'))}"
                    )
                # Cancel draft POs
                draft_pos = order.purchase_order_ids.filtered(lambda po: po.state == 'draft')
                draft_pos.button_cancel()
        
        return super(SaleOrder, self).unlink()

    def action_confirm_commissions(self):
        """Confirm commissions: set status to 'completed' if commissions are processed, else raise error."""
        for order in self:
            if not order.commission_processed:
                raise UserError("You must calculate/process commissions before confirming.")
            order.commission_status = 'completed'
            order.message_post(body="Commissions confirmed.")
        return True

    def action_reset_commissions(self):
        """Reset commission status to draft and allow recalculation."""
        for order in self:
            order.commission_status = 'not_started'
            order.commission_processed = False
            order.message_post(body="Commission status reset to draft. Please recalculate commissions.")
        return True