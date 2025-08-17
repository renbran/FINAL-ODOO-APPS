from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Add custom status fields if they don't exist
    order_status = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('commission', 'Commission'),
        ('final_review', 'Final Review'),
        ('approved', 'Approved'),
        ('implementation', 'Implementation'),
        ('completed', 'Completed'),
    ], string='Order Status', default='draft', tracking=True,
       help="Current status of the order in the workflow")
    
    order_status_id = fields.Many2one(
        'order.status', 
        string='Order Status Record',
        tracking=True,
        help="Custom order status for workflow management"
    )
    
    # Legacy field for backward compatibility (CloudPepper fix)
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Custom Status',
        tracking=True,
        help="Custom order status for workflow management (legacy field for compatibility)"
    )
    documentation_user_id = fields.Many2one(
        'res.users',
        string='Documentation User',
        tracking=True,
        help="User responsible for documentation stage"
    )
    commission_user_id = fields.Many2one(
        'res.users',
        string='Commission User',
        tracking=True,
        help="User responsible for commission calculation"
    )
    allocation_user_id = fields.Many2one(
        'res.users',
        string='Allocation User',
        tracking=True,
        help="User responsible for allocation stage"
    )
    final_review_user_id = fields.Many2one(
        'res.users',
        string='Final Review User',
        tracking=True,
        help="User responsible for final review"
    )
    
    # Computed fields for button visibility
    show_document_review_button = fields.Boolean(
        string='Show Document Review Button',
        compute='_compute_button_visibility',
        help="Determines if document review button should be visible"
    )
    show_commission_calculation_button = fields.Boolean(
        string='Show Commission Calculation Button',
        compute='_compute_button_visibility',
        help="Determines if commission calculation button should be visible"
    )
    show_allocation_button = fields.Boolean(
        string='Show Allocation Button',
        compute='_compute_button_visibility',
        help="Determines if allocation button should be visible"
    )
    show_final_review_button = fields.Boolean(
        string='Show Final Review Button',
        compute='_compute_button_visibility',
        help="Determines if final review button should be visible"
    )
    show_approve_button = fields.Boolean(
        string='Show Approve Button',
        compute='_compute_button_visibility',
        help="Determines if approve button should be visible"
    )
    show_post_button = fields.Boolean(
        string='Show Post Button',
        compute='_compute_button_visibility',
        help="Determines if post button should be visible"
    )
    show_reject_button = fields.Boolean(
        string='Show Reject Button',
        compute='_compute_button_visibility',
        help="Determines if reject button should be visible"
    )
    auto_assigned_users = fields.Boolean(
        string='Auto Assigned Users',
        compute='_compute_auto_assigned_users',
        help="Indicates if users have been automatically assigned"
    )
    
    @api.model
    def create(self, vals):
        """Set initial status when creating order"""
        order = super().create(vals)
        
        # Set initial status if not provided
        if not order.order_status_id:
            initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
            if initial_status:
                order.order_status_id = initial_status.id
                order.custom_status_id = initial_status.id  # Sync legacy field
        
        # Ensure both fields are synchronized
        if order.order_status_id and not order.custom_status_id:
            order.custom_status_id = order.order_status_id.id
        elif order.custom_status_id and not order.order_status_id:
            order.order_status_id = order.custom_status_id.id
        
        return order
    
    @api.onchange('order_status_id')
    def _onchange_order_status_id(self):
        """Sync custom_status_id when order_status_id changes"""
        if self.order_status_id:
            self.custom_status_id = self.order_status_id
    
    @api.onchange('custom_status_id')
    def _onchange_custom_status_id(self):
        """Sync order_status_id when custom_status_id changes"""
        if self.custom_status_id:
            self.order_status_id = self.custom_status_id
    
    @api.depends('order_status_id', 'custom_status_id', 'state')
    def _compute_button_visibility(self):
        """Compute visibility of workflow buttons based on current status"""
        for record in self:
            current_status = record.order_status_id or record.custom_status_id
            
            # Default all to False
            record.show_document_review_button = False
            record.show_commission_calculation_button = False
            record.show_allocation_button = False
            record.show_final_review_button = False
            record.show_approve_button = False
            record.show_post_button = False
            record.show_reject_button = False
            
            if not current_status:
                continue
                
            # Logic for button visibility based on status
            if current_status == 'draft':
                record.show_document_review_button = True
            elif current_status == 'document_review':
                record.show_commission_calculation_button = True
                record.show_reject_button = True
            elif current_status == 'commission_calculation':
                record.show_allocation_button = True
                record.show_reject_button = True
            elif current_status == 'allocation':
                record.show_final_review_button = True
                record.show_reject_button = True
            elif current_status == 'final_review':
                record.show_approve_button = True
                record.show_reject_button = True
            elif current_status in ['approved', 'sale']:
                record.show_post_button = True
    
    @api.depends('documentation_user_id', 'commission_user_id', 'allocation_user_id', 'final_review_user_id')
    def _compute_auto_assigned_users(self):
        """Compute if users have been automatically assigned"""
        for record in self:
            record.auto_assigned_users = bool(
                record.documentation_user_id or 
                record.commission_user_id or 
                record.allocation_user_id or 
                record.final_review_user_id
            )
    
    def _change_status(self, new_status_id, notes=None):
        """Change order status with proper validation and logging"""
        self.ensure_one()
        
        try:
            new_status = self.env['order.status'].browse(new_status_id)
            if not new_status.exists():
                raise ValidationError(_("Invalid status specified."))
            
            old_status = self.order_status_id
            
            # Update the status
            self.order_status_id = new_status.id
            self.custom_status_id = new_status.id  # Sync legacy field
            
            # Handle Odoo state mapping
            self._update_state_from_status(new_status)
            
            # Log the change
            message = _("Status changed from '%s' to '%s'") % (
                old_status.name if old_status else _('None'),
                new_status.name
            )
            if notes:
                message += _("\nNotes: %s") % notes
            
            self.message_post(body=message)
            
            _logger.info("Order %s status changed from %s to %s by user %s", 
                        self.name, 
                        old_status.name if old_status else 'None',
                        new_status.name,
                        self.env.user.name)
            
            return True
            
        except Exception as e:
            _logger.error("Failed to change status for order %s: %s", self.name, str(e))
            raise
    
    def _update_state_from_status(self, status):
        """Update Odoo standard state based on custom status"""
        state_mapping = {
            'draft': 'draft',
            'documentation_progress': 'sent',
            'commission_progress': 'sale',
            'final_review': 'sale',
            'approved': 'sale',
        }
        
        new_state = state_mapping.get(status.code)
        if new_state and new_state != self.state:
            if new_state == 'sale' and self.state in ['draft', 'sent']:
                self.action_confirm()
            elif new_state == 'sent' and self.state == 'draft':
                self.state = 'sent'
            else:
                self.state = new_state
    
    @api.model
    def get_order_status(self, order_id):
        """Get order status information for the widget"""
        try:
            order = self.browse(order_id)
            if not order.exists():
                return {'error': 'Order not found'}
            
            return {
                'status': order.state,
                'status_display': dict(order._fields['state'].selection).get(order.state, order.state),
                'order_id': order.id,
                'name': order.name,
                'partner_name': order.partner_id.name,
                'amount_total': order.amount_total,
                'currency': order.currency_id.name,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def update_status(self, new_status):
        """Update order status safely"""
        try:
            self.ensure_one()
            
            # Map widget statuses to Odoo states
            status_mapping = {
                'approved': 'sale',
                'rejected': 'cancel',
                'draft': 'draft',
                'confirmed': 'sale'
            }
            
            if new_status in status_mapping:
                odoo_state = status_mapping[new_status]
                
                # Validate state transition
                if odoo_state == 'sale' and self.state == 'draft':
                    self.action_confirm()
                elif odoo_state == 'cancel':
                    self.action_cancel()
                else:
                    self.state = odoo_state
                
                return {'success': True, 'new_status': self.state}
            else:
                raise ValidationError(f"Invalid status: {new_status}")
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Missing action methods from validation
    def action_post_order(self):
        """Post the order (mark as confirmed)"""
        self.ensure_one()
        if self.state == 'draft':
            self.action_confirm()
        return True
    
    def action_change_status(self):
        """Open status change wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Order Status',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_move_to_final_review(self):
        """Move order to final review stage"""
        self.ensure_one()
        # Custom logic for final review
        return True
    
    def action_approve_order(self):
        """Approve the order"""
        self.ensure_one()
        if self.state in ['draft', 'sent']:
            self.action_confirm()
        return True
    
    def action_quotation_send(self):
        """Send quotation email"""
        self.ensure_one()
        return self.action_quotation_send() if hasattr(super(), 'action_quotation_send') else True
    
    def action_reassign_workflow_users(self):
        """Reassign workflow users"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reassign Users',
            'res_model': 'order.user.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_move_to_post(self):
        """Move to post stage"""
        self.ensure_one()
        return self.action_confirm()
    
    def action_move_to_commission_calculation(self):
        """Move to commission calculation stage"""
        self.ensure_one()
        # Custom commission logic
        return True
    
    def action_view_order_reports(self):
        """View order reports"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order Reports',
            'res_model': 'order.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_reject_order(self):
        """Reject the order"""
        self.ensure_one()
        self.action_cancel()
        return True
    
    def action_move_to_allocation(self):
        """Move to allocation stage"""
        self.ensure_one()
        # Custom allocation logic
        return True
    
    def action_move_to_document_review(self):
        """Move to document review stage"""
        self.ensure_one()
        # Custom document review logic
        return True
    
    def action_confirm(self):
        """Confirm the sale order"""
        self.ensure_one()
        try:
            # Call the parent action_confirm
            result = super().action_confirm()
            
            # Update status to confirmed/sale if we have status management
            if self.order_status_id:
                confirmed_status = self.env['order.status'].search([
                    ('code', '=', 'confirmed')
                ], limit=1)
                if confirmed_status:
                    self._change_status(confirmed_status.id, "Order confirmed")
            
            return result
        except Exception as e:
            _logger.error("Error in action_confirm: %s", str(e))
            raise
    
    def action_move_to_final_review(self):
        """Move to final review stage"""
        self.ensure_one()
        final_review_status = self.env['order.status'].search([
            ('code', '=', 'final_review')
        ], limit=1)
        if final_review_status:
            self._change_status(final_review_status.id, "Moved to final review")
        return True
    
    def action_approve_order(self):
        """Approve the order"""
        self.ensure_one()
        approved_status = self.env['order.status'].search([
            ('code', '=', 'approved')
        ], limit=1)
        if approved_status:
            self._change_status(approved_status.id, "Order approved")
        return True
    
    def action_generate_payment_voucher(self):
        """Generate payment voucher"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Payment Voucher',
            'res_model': 'payment.voucher.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
    
    def action_view_payment_vouchers(self):
        """View payment vouchers"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Vouchers',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('ref', 'ilike', self.name)],
            'context': {'create': False}
        }
    
    def action_print_payment_voucher(self):
        """Print payment voucher"""
        self.ensure_one()
        return self.env.ref('account.action_report_payment_receipt').report_action(self)
    
    def action_send_commission_email(self):
        """Send commission email"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Commission Email',
            'res_model': 'commission.email.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
