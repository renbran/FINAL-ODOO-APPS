from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Custom Status Management
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Custom Status', 
        tracking=True, 
        copy=False
    )
    custom_status_history_ids = fields.One2many(
        'order.status.history', 
        'order_id', 
        string='Status History', 
        copy=False
    )
    
    # Responsible Users
    documentation_user_id = fields.Many2one(
        'res.users', 
        string='Documentation Responsible'
    )
    commission_user_id = fields.Many2one(
        'res.users', 
        string='Commission Responsible'
    )
    final_review_user_id = fields.Many2one(
        'res.users', 
        string='Final Review Responsible'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial status"""
        records = super(SaleOrder, self).create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        if initial_status:
            for record in records:
                record.custom_status_id = initial_status.id
                self.env['order.status.history'].create({
                    'order_id': record.id,
                    'status_id': initial_status.id,
                    'notes': _('Initial status automatically set to %s') % initial_status.name
                })
        return records
    
    def action_change_status(self):
        """Open the status change wizard"""
        self.ensure_one()
        return {
            'name': _('Change Order Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
            }
        }

    def action_approve_order(self):
        """Approve the order and move to final approved status"""
        self.ensure_one()
        # Check if current user can approve
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can approve orders."))
        
        # Find the final approved status
        approved_status = self.env['order.status'].search([('code', '=', 'approved')], limit=1)
        if not approved_status:
            raise UserError(_("Approved status not found in the system."))
        
        # Change to approved status
        self._change_status(approved_status.id, _("Order approved by %s") % self.env.user.name)
        
        # Send approval notification
        self.message_post(
            body=_("Order has been approved and is ready for confirmation."),
            subject=_("Order Approved"),
            message_type='notification'
        )
        
        return True
    
    def action_reject_order(self):
        """Reject the order and return to draft"""
        self.ensure_one()
        # Check if current user can reject
        if not self.final_review_user_id or self.final_review_user_id.id != self.env.user.id:
            if not self.env.user.has_group('order_status_override.group_order_approval_manager'):
                raise UserError(_("Only the assigned reviewer or approval managers can reject orders."))
        
        # Find the draft status
        draft_status = self.env['order.status'].search([('code', '=', 'draft')], limit=1)
        if not draft_status:
            raise UserError(_("Draft status not found in the system."))
        
        # Change to draft status
        self._change_status(draft_status.id, _("Order rejected by %s and returned to draft") % self.env.user.name)
        
        # Send rejection notification
        self.message_post(
            body=_("Order has been rejected and returned to draft status for revision."),
            subject=_("Order Rejected"),
            message_type='notification'
        )
        
        return True
    
    def action_submit_for_review(self):
        """Submit order for final review"""
        self.ensure_one()
        
        # Find the review status
        review_status = self.env['order.status'].search([('code', '=', 'review')], limit=1)
        if not review_status:
            raise UserError(_("Review status not found in the system."))
        
        # Change to review status
        self._change_status(review_status.id, _("Order submitted for review by %s") % self.env.user.name)
        
        # Send notification
        self.message_post(
            body=_("Order has been submitted for final review."),
            subject=_("Order Submitted for Review"),
            message_type='notification'
        )
        
        return True
    
    def _change_status(self, status_id, notes=None):
        """Helper method to change status and log history"""
        self.ensure_one()
        
        # Update the status
        self.custom_status_id = status_id
        
        # Create history record
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': status_id,
            'notes': notes or _('Status changed'),
            'user_id': self.env.user.id,
            'date': fields.Datetime.now()
        })
        
        return True
    
    def get_status_history(self):
        """Get formatted status history"""
        self.ensure_one()
        history = []
        for record in self.custom_status_history_ids.sorted('date', reverse=True):
            history.append({
                'status': record.status_id.name,
                'date': record.date,
                'user': record.user_id.name,
                'notes': record.notes
            })
        return history
