# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Extend the SALE_ORDER_STATE to include 'done'
EXTENDED_SALE_ORDER_STATE = [
    ('draft', 'Quotation'),
    ('sent', 'Quotation Sent'),
    ('sale', 'Sales Order'),
    ('done', 'Completed'),
    ('cancel', 'Cancelled'),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Override state field to add 'done' option
    state = fields.Selection(
        selection=EXTENDED_SALE_ORDER_STATE,
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        tracking=3,
        default='draft'
    )

    # Custom workflow state field
    custom_state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Custom State',
       default='draft',
       tracking=True,
       help='Custom workflow state for enhanced order tracking'
    )

    # Simple workflow control fields
    is_locked = fields.Boolean(
        string='Is Locked',
        compute='_compute_is_locked',
        store=True,
        help='True if order is locked for editing'
    )

    can_unlock = fields.Boolean(
        string='Can Unlock',
        compute='_compute_can_unlock',
        help='True if current user can unlock orders'
    )

    has_due = fields.Boolean(
        string='Has Due Amounts',
        compute='_compute_has_due',
        help='True if order has overdue amounts'
    )

    is_warning = fields.Boolean(
        string='Has Warnings',
        compute='_compute_is_warning',
        help='True if there are validation warnings for this order'
    )

    # Simple compute methods
    @api.depends('state', 'custom_state')
    def _compute_is_locked(self):
        """Simple lock computation - order is locked when state is done or custom_state is completed"""
        for order in self:
            order.is_locked = order.state == 'done' or order.custom_state == 'completed'

    def _compute_can_unlock(self):
        """Check if user can unlock orders"""
        can_unlock = self.env.user.has_group('sales_team.group_sale_manager')
        for order in self:
            order.can_unlock = can_unlock

    def _compute_has_due(self):
        """Simple due amount computation"""
        for order in self:
            # Simple check for overdue invoices
            overdue_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.amount_residual > 0
            )
            order.has_due = bool(overdue_invoices)

    def _compute_is_warning(self):
        """Simple warning computation"""
        for order in self:
            # Simple warning checks
            has_warnings = False

            # Warning if no order lines
            if not order.order_line:
                has_warnings = True

            # Warning if customer has no payment terms and amount > 0
            if order.amount_total > 0 and not order.partner_id.property_payment_term_id:
                has_warnings = True

            order.is_warning = has_warnings

    # Simple workflow methods
    def action_move_to_documentation(self):
        """Move order to documentation stage"""
        self.ensure_one()
        if self.is_locked:
            raise UserError(_('Cannot modify a completed/locked order. Please unlock it first.'))
        self.custom_state = 'documentation'
        return True

    def action_move_to_calculation(self):
        """Move order to calculation stage"""
        self.ensure_one()
        if self.is_locked:
            raise UserError(_('Cannot modify a completed/locked order. Please unlock it first.'))
        self.custom_state = 'calculation'
        return True

    def action_move_to_approved(self):
        """Move order to approved stage"""
        self.ensure_one()
        if self.is_locked:
            raise UserError(_('Cannot modify a completed/locked order. Please unlock it first.'))
        self.custom_state = 'approved'
        return True

    def action_complete_order(self):
        """Mark order as completed and lock it"""
        self.ensure_one()
        if self.state not in ('sale', 'done'):
            raise UserError(_('Only confirmed sales orders can be marked as completed.'))
        
        # Set state to done and custom_state to completed
        self.write({
            'state': 'done',
            'custom_state': 'completed',
            'locked': True  # Use Odoo's built-in locked field as well
        })
        return True

    def action_unlock_order(self):
        """Unlock order for editing - Admin/Manager only"""
        self.ensure_one()
        if not self.can_unlock:
            raise UserError(_('You do not have permission to unlock orders. Please contact your manager.'))

        # Unlock the order by setting it back to sale state
        self.write({
            'state': 'sale',
            'custom_state': 'approved',
            'locked': False
        })
        return True

    def action_set_to_draft(self):
        """Reset order to draft state"""
        self.ensure_one()
        if not self.can_unlock and self.is_locked:
            raise UserError(_('You do not have permission to unlock completed orders. Please contact your manager.'))
        
        self.write({
            'state': 'draft',
            'custom_state': 'draft',
            'locked': False
        })
        return True

    def write(self, vals):
        """Override write to prevent modifications on locked orders"""
        # Allow state changes and unlock operations
        allowed_fields = {'state', 'custom_state', 'locked', 'is_locked', 'message_main_attachment_id'}
        
        # Check if trying to modify a locked order with non-allowed fields
        if vals.keys() - allowed_fields:
            for order in self:
                if order.is_locked and order.state == 'done':
                    # Check if user can unlock
                    if not order.can_unlock:
                        raise UserError(_('This order is locked and cannot be modified. Please unlock it first or contact your manager.'))
        
        return super(SaleOrder, self).write(vals)
