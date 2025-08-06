# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OrderStatusChangeWizard(models.TransientModel):
    _name = 'order.status.change.wizard'
    _description = 'Change Order Status Wizard'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    current_status_id = fields.Many2one('order.status', string='Current Status', readonly=True)
    new_status_id = fields.Many2one('order.status', string='New Status', required=True)
    notes = fields.Text(string='Notes', placeholder="Add notes about this status change...")
    
    # Helper fields for UI logic
    requires_documentation_user = fields.Boolean(
        compute='_compute_required_assignments',
        string="Requires Documentation User"
    )
    requires_commission_user = fields.Boolean(
        compute='_compute_required_assignments',
        string="Requires Commission User"
    )
    requires_review_user = fields.Boolean(
        compute='_compute_required_assignments',
        string="Requires Review User"
    )
    
    # Assignment fields (shown conditionally)
    documentation_user_id = fields.Many2one(
        'res.users',
        string='Documentation User',
        related='order_id.documentation_user_id',
        readonly=False
    )
    commission_user_id = fields.Many2one(
        'res.users',
        string='Commission User',
        related='order_id.commission_user_id',
        readonly=False
    )
    final_review_user_id = fields.Many2one(
        'res.users',
        string='Final Review User',
        related='order_id.final_review_user_id',
        readonly=False
    )
    
    @api.depends('new_status_id')
    def _compute_required_assignments(self):
        """Compute which user assignments are required for the new status"""
        for wizard in self:
            wizard.requires_documentation_user = (
                wizard.new_status_id.responsible_type == 'documentation'
            )
            wizard.requires_commission_user = (
                wizard.new_status_id.responsible_type == 'commission'
            )
            wizard.requires_review_user = (
                wizard.new_status_id.responsible_type == 'final_review'
            )
    
    @api.onchange('current_status_id')
    def _onchange_current_status(self):
        """Limit available statuses based on current status"""
        if self.current_status_id:
            # If next statuses are defined, use them; otherwise allow all non-current
            if self.current_status_id.next_status_ids:
                domain = [('id', 'in', self.current_status_id.next_status_ids.ids)]
            else:
                domain = [('id', '!=', self.current_status_id.id), ('active', '=', True)]
            
            return {'domain': {'new_status_id': domain}}
        return {'domain': {'new_status_id': [('active', '=', True)]}}
    
    @api.onchange('new_status_id')
    def _onchange_new_status(self):
        """Auto-suggest notes based on status transition"""
        if self.new_status_id and self.current_status_id:
            suggestions = {
                'documentation_progress': "Documentation process initiated. Please prepare all required documents.",
                'commission_progress': "Commission calculation in progress. Please verify commission rates and calculations.",
                'final_review': "Order submitted for final review. Please review all documentation and calculations.",
                'approved': "Order approved for processing. Ready for confirmation.",
                'draft': "Order returned to draft status for revision."
            }
            
            if self.new_status_id.code in suggestions:
                self.notes = suggestions[self.new_status_id.code]
    
    def change_status(self):
        """Apply status change with validation"""
        self.ensure_one()
        
        # Validate transition is allowed
        if (self.current_status_id.next_status_ids and 
            self.new_status_id.id not in self.current_status_id.next_status_ids.ids):
            raise UserError(_("The selected status transition is not allowed. Please choose a valid next status."))
        
        # Validate required assignments
        self._validate_assignments()
        
        # Update assignments on the sale order
        self._update_assignments()
        
        # Apply the new status
        self.order_id._change_status(self.new_status_id.id, self.notes)
        
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Status Changed'),
                'message': _('Order status changed to %s successfully.') % self.new_status_id.name,
                'type': 'success',
            }
        }
    
    def _validate_assignments(self):
        """Validate required user assignments are present"""
        if self.requires_documentation_user and not self.documentation_user_id:
            raise UserError(_("Documentation user must be assigned for this status."))
        
        if self.requires_commission_user and not self.commission_user_id:
            raise UserError(_("Commission user must be assigned for this status."))
        
        if self.requires_review_user and not self.final_review_user_id:
            raise UserError(_("Final review user must be assigned for this status."))
    
    def _update_assignments(self):
        """Update user assignments on the sale order"""
        vals = {}
        
        if self.requires_documentation_user and self.documentation_user_id:
            vals['documentation_user_id'] = self.documentation_user_id.id
            
        if self.requires_commission_user and self.commission_user_id:
            vals['commission_user_id'] = self.commission_user_id.id
            
        if self.requires_review_user and self.final_review_user_id:
            vals['final_review_user_id'] = self.final_review_user_id.id
        
        if vals:
            self.order_id.write(vals)