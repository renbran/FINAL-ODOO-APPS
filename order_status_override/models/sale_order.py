from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import json

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Custom Status Management
    custom_status_id = fields.Many2one(
        'order.status', 
        string='Workflow Status', 
        tracking=True, 
        copy=False,
        help='Current status in the OSUS workflow process'
    )
    custom_status_history_ids = fields.One2many(
        'order.status.history', 
        'order_id', 
        string='Status History', 
        copy=False
    )
    
    # Enhanced User Assignments
    documentation_user_id = fields.Many2one(
        'res.users', 
        string='Documentation Responsible',
        help='User responsible for documentation stage'
    )
    commission_user_id = fields.Many2one(
        'res.users', 
        string='Commission Responsible',
        help='User responsible for commission calculation stage'
    )
    final_review_user_id = fields.Many2one(
        'res.users', 
        string='Final Review Responsible',
        help='User responsible for final review and approval'
    )
    
    # Commission Integration Fields
    commission_calculated = fields.Boolean(
        string='Commission Calculated',
        default=False,
        help='Whether commission has been calculated for this order'
    )
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        currency_field='currency_id',
        compute='_compute_total_commission',
        store=True,
        help='Total commission amount from commission_ax integration'
    )
    
    # Deal Summary Fields  
    deal_summary = fields.Text(
        string='Deal Summary',
        help='Summary of the deal including key metrics'
    )
    deal_metrics = fields.Text(
        string='Deal Metrics JSON',
        help='JSON field storing deal metrics for dashboard'
    )
    
    # Enhanced Workflow Fields
    workflow_progress = fields.Float(
        string='Workflow Progress',
        compute='_compute_workflow_progress',
        help='Progress percentage through the workflow'
    )
    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
        help='Whether current status requires approval'
    )
    
    # Digital Signature Fields
    documentation_signature = fields.Binary(
        string='Documentation Signature',
        attachment=True,
        help='Digital signature for documentation completion'
    )
    commission_signature = fields.Binary(
        string='Commission Signature', 
        attachment=True,
        help='Digital signature for commission approval'
    )
    final_approval_signature = fields.Binary(
        string='Final Approval Signature',
        attachment=True, 
        help='Digital signature for final approval'
    )
    
    # Payment tracking field (fixed for CloudPepper compatibility)
    total_payment_amount = fields.Monetary(
        string='Total Payment Amount',
        currency_field='currency_id',
        default=0.0,
        help='Total payment amount for this order'
    )
    
    @api.depends('external_commission_ids', 'internal_commission_ids')
    def _compute_total_commission(self):
        """Compute total commission from commission_ax module"""
        for order in self:
            total_external = sum(order.external_commission_ids.mapped('amount_fixed'))
            total_internal = sum(order.internal_commission_ids.mapped('amount_fixed'))
            order.total_commission_amount = total_external + total_internal
    
    @api.depends('custom_status_id')
    def _compute_workflow_progress(self):
        """Compute workflow progress percentage"""
        for order in self:
            if not order.custom_status_id:
                order.workflow_progress = 0.0
                continue
                
            status_sequence = order.custom_status_id.sequence
            max_sequence = self.env['order.status'].search([], order='sequence desc', limit=1).sequence
            
            if max_sequence:
                order.workflow_progress = (status_sequence / max_sequence) * 100
            else:
                order.workflow_progress = 0.0
    
    @api.depends('custom_status_id')
    def _compute_requires_approval(self):
        """Compute if current status requires approval"""
        for order in self:
            order.requires_approval = (
                order.custom_status_id and 
                order.custom_status_id.code in ['final_review', 'approved']
            )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial status and initialize workflow"""
        records = super(SaleOrder, self).create(vals_list)
        initial_status = self.env['order.status'].search([('is_initial', '=', True)], limit=1)
        
        for record in records:
            if initial_status:
                record.custom_status_id = initial_status.id
                record._create_status_history(
                    initial_status.id,
                    _('Order created and workflow initialized')
                )
                record._initialize_deal_metrics()
                
        return records
    
    def _create_status_history(self, status_id, notes=None):
        """Create status history record"""
        self.ensure_one()
        self.env['order.status.history'].create({
            'order_id': self.id,
            'status_id': status_id,
            'notes': notes or _('Status changed'),
            'user_id': self.env.user.id,
            'date': fields.Datetime.now()
        })
    
    def _initialize_deal_metrics(self):
        """Initialize deal metrics for dashboard tracking"""
        self.ensure_one()
        metrics = {
            'created_date': fields.Datetime.now().isoformat(),
            'initial_amount': self.amount_total,
            'workflow_started': True,
            'commission_calculated': False,
            'approval_pending': False,
        }
        self.deal_metrics = json.dumps(metrics)
    
    # Enhanced Workflow Action Methods
    def action_change_status(self):
        """Open enhanced status change wizard"""
        self.ensure_one()
        return {
            'name': _('Change Workflow Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.status.change.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_current_status_id': self.custom_status_id.id,
                'show_advanced_options': True,
            }
        }

    def action_approve_order(self):
        """Enhanced approve order with digital signature support"""
        self.ensure_one()
        
        # Check permissions
        if not self._can_approve_order():
            raise UserError(_("You don't have permission to approve this order."))
        
        # Find approved status
        approved_status = self.env['order.status'].search([('code', '=', 'approved')], limit=1)
        if not approved_status:
            raise UserError(_("Approved status not found in the system."))
        
        # Change to approved status
        self._change_status(approved_status.id, _("Order approved by %s") % self.env.user.name)
        
        # Update deal metrics
        self._update_deal_metrics('approved')
        
        # Send notifications
        self._send_workflow_notification(
            'order_approved',
            _("Order Approved"),
            _("Order has been approved and is ready for posting.")
        )
        
        return True
    
    def action_post_order(self):
        """Post order - final workflow stage"""
        self.ensure_one()
        
        # Check if order can be posted
        if not self._can_post_order():
            raise UserError(_("Order cannot be posted in current state."))
        
        # Find posted status
        posted_status = self.env['order.status'].search([('code', '=', 'posted')], limit=1)
        if not posted_status:
            raise UserError(_("Posted status not found in the system."))
        
        # Confirm the sale order first
        if self.state == 'draft':
            self.action_confirm()
        
        # Change to posted status
        self._change_status(posted_status.id, _("Order posted by %s") % self.env.user.name)
        
        # Update deal metrics
        self._update_deal_metrics('posted')
        
        # Generate final commission purchase orders
        if self.commission_calculated:
            self._generate_commission_purchase_orders()
        
        # Send final notifications
        self._send_workflow_notification(
            'order_posted',
            _("Order Posted"),
            _("Order has been posted and finalized.")
        )
        
        return True
    
    def action_reject_order(self):
        """Enhanced reject order with reason tracking"""
        self.ensure_one()
        
        # Check permissions
        if not self._can_reject_order():
            raise UserError(_("You don't have permission to reject this order."))
        
        # Open rejection reason wizard
        return {
            'name': _('Reject Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'order.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            }
        }
    
    def action_return_to_previous(self):
        """Enhanced return to previous stage with workflow validation"""
        self.ensure_one()
        
        current_code = self.custom_status_id.code
        
        # Enhanced previous status mapping
        previous_status_map = {
            'documentation_progress': 'draft',
            'commission_progress': 'documentation_progress', 
            'final_review': 'commission_progress',
            'approved': 'final_review',
            'review': 'commission_progress',
            'rejected': 'draft',
        }
        
        if current_code not in previous_status_map:
            raise UserError(_("Cannot return to previous stage from current status."))
        
        # Check if user can perform this action
        if not self._can_return_to_previous():
            raise UserError(_("You don't have permission to return this order to previous stage."))
        
        # Find the previous status
        previous_code = previous_status_map[current_code]
        previous_status = self.env['order.status'].search([('code', '=', previous_code)], limit=1)
        if not previous_status:
            raise UserError(_("Previous status '%s' not found in the system.") % previous_code)
        
        # Reset relevant data based on target status
        self._reset_workflow_data(previous_code)
        
        # Change to previous status
        self._change_status(previous_status.id, _("Order returned to %s by %s") % (previous_status.name, self.env.user.name))
        
        # Update deal metrics
        self._update_deal_metrics('returned_to_previous')
        
        # Send notification
        self._send_workflow_notification(
            'order_returned',
            _("Order Returned to Previous Stage"),
            _("Order has been returned to %s stage") % previous_status.name
        )
        
        return True
    
    def action_request_documentation(self):
        """Enhanced documentation request with assignment"""
        self.ensure_one()
        
        # Find documentation status
        doc_status = self.env['order.status'].search([('code', '=', 'documentation_progress')], limit=1)
        if not doc_status:
            raise UserError(_("Documentation progress status not found in the system."))
        
        # Auto-assign documentation user if not set
        if not self.documentation_user_id:
            default_doc_user = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('order_status_override.group_order_documentation').id)
            ], limit=1)
            if default_doc_user:
                self.documentation_user_id = default_doc_user.id
        
        # Change to documentation status
        self._change_status(doc_status.id, _("Documentation process started by %s") % self.env.user.name)
        
        # Update deal metrics
        self._update_deal_metrics('documentation_started')
        
        # Create activity for documentation user
        if self.documentation_user_id:
            self._create_workflow_activity(
                'Documentation Required',
                _("Please complete documentation for order %s") % self.name,
                self.documentation_user_id.id
            )
        
        # Send notification
        self._send_workflow_notification(
            'documentation_started',
            _("Documentation Started"),
            _("Documentation process has been initiated.")
        )
        
        return True
    
    def action_start_commission_calculation(self):
        """Start commission calculation stage with commission_ax integration"""
        self.ensure_one()
        
        # Check if documentation is complete
        if not self._is_documentation_complete():
            raise UserError(_("Documentation must be completed before commission calculation."))
        
        # Find commission status
        commission_status = self.env['order.status'].search([('code', '=', 'commission_progress')], limit=1)
        if not commission_status:
            raise UserError(_("Commission progress status not found in the system."))
        
        # Auto-assign commission user if not set
        if not self.commission_user_id:
            default_commission_user = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('order_status_override.group_order_commission').id)
            ], limit=1)
            if default_commission_user:
                self.commission_user_id = default_commission_user.id
        
        # Initialize commission data from commission_ax
        self._initialize_commission_data()
        
        # Change to commission status
        self._change_status(commission_status.id, _("Commission calculation started by %s") % self.env.user.name)
        
        # Update deal metrics
        self._update_deal_metrics('commission_started')
        
        # Create activity for commission user
        if self.commission_user_id:
            self._create_workflow_activity(
                'Commission Calculation Required',
                _("Please calculate commissions for order %s") % self.name,
                self.commission_user_id.id
            )
        
        # Send notification
        self._send_workflow_notification(
            'commission_started',
            _("Commission Calculation Started"),
            _("Commission calculation process has been initiated.")
        )
        
        return True
    
    def action_submit_for_review(self):
        """Enhanced submit for review with validation"""
        self.ensure_one()
        
        # Validate commission calculations
        if not self.commission_calculated:
            raise UserError(_("Commission calculations must be completed before submitting for review."))
        
        # Find review status
        review_status = self.env['order.status'].search([('code', '=', 'final_review')], limit=1)
        if not review_status:
            raise UserError(_("Final review status not found in the system."))
        
        # Auto-assign review user if not set
        if not self.final_review_user_id:
            default_review_user = self.env['res.users'].search([
                ('groups_id', 'in', self.env.ref('order_status_override.group_order_final_review').id)
            ], limit=1)
            if default_review_user:
                self.final_review_user_id = default_review_user.id
        
        # Change to review status
        self._change_status(review_status.id, _("Order submitted for final review by %s") % self.env.user.name)
        
        # Update deal metrics
        self._update_deal_metrics('submitted_for_review')
        
        # Create activity for review user
        if self.final_review_user_id:
            self._create_workflow_activity(
                'Final Review Required',
                _("Please review order %s for final approval") % self.name,
                self.final_review_user_id.id
            )
        
        # Send notification
        self._send_workflow_notification(
            'submitted_for_review',
            _("Order Submitted for Review"),
            _("Order has been submitted for final review.")
        )
        
        return True
    
    # Helper Methods for Workflow Management
    def _change_status(self, status_id, notes=None):
        """Enhanced helper method to change status with comprehensive logging"""
        self.ensure_one()
        
        old_status = self.custom_status_id.name if self.custom_status_id else 'None'
        new_status = self.env['order.status'].browse(status_id)
        
        # Update the status
        self.custom_status_id = status_id
        
        # Create comprehensive history record
        self._create_status_history(status_id, notes)
        
        # Log the change
        _logger.info(
            "Order %s: Status changed from '%s' to '%s' by user %s", 
            self.name, old_status, new_status.name, self.env.user.name
        )
        
        # Update deal summary
        self._update_deal_summary()
        
        return True
    
    def _update_deal_summary(self):
        """Update deal summary with current order information"""
        self.ensure_one()
        
        summary_parts = []
        summary_parts.append(f"Order: {self.name}")
        summary_parts.append(f"Customer: {self.partner_id.name}")
        summary_parts.append(f"Amount: {self.amount_total:,.2f} {self.currency_id.name}")
        summary_parts.append(f"Status: {self.custom_status_id.name}")
        
        if self.commission_calculated:
            summary_parts.append(f"Commission: {self.total_commission_amount:,.2f} {self.currency_id.name}")
        
        summary_parts.append(f"Progress: {self.workflow_progress:.1f}%")
        
        self.deal_summary = "\n".join(summary_parts)
    
    def _update_deal_metrics(self, event_type):
        """Update deal metrics JSON for dashboard tracking"""
        self.ensure_one()
        
        try:
            metrics = json.loads(self.deal_metrics) if self.deal_metrics else {}
        except:
            metrics = {}
        
        # Update metrics based on event type
        metrics['last_update'] = fields.Datetime.now().isoformat()
        metrics['current_status'] = self.custom_status_id.code
        metrics['workflow_progress'] = self.workflow_progress
        
        if event_type == 'documentation_started':
            metrics['documentation_started_date'] = fields.Datetime.now().isoformat()
        elif event_type == 'commission_started':
            metrics['commission_started_date'] = fields.Datetime.now().isoformat()
        elif event_type == 'submitted_for_review':
            metrics['review_submitted_date'] = fields.Datetime.now().isoformat()
        elif event_type == 'approved':
            metrics['approved_date'] = fields.Datetime.now().isoformat()
            metrics['approval_pending'] = False
        elif event_type == 'posted':
            metrics['posted_date'] = fields.Datetime.now().isoformat()
            metrics['completed'] = True
        
        self.deal_metrics = json.dumps(metrics)
    
    def _send_workflow_notification(self, notification_type, subject, body):
        """Send workflow notifications via email and internal messaging"""
        self.ensure_one()
        
        # Post internal message
        self.message_post(
            body=body,
            subject=subject,
            message_type='notification'
        )
        
        # Send email to relevant users based on notification type
        recipients = self._get_notification_recipients(notification_type)
        
        if recipients:
            template = self.env.ref(f'order_status_override.email_template_{notification_type}', False)
            if template:
                for recipient in recipients:
                    template.with_context(recipient_user=recipient).send_mail(self.id, force_send=True)
    
    def _get_notification_recipients(self, notification_type):
        """Get list of users to notify based on notification type"""
        self.ensure_one()
        
        recipients = []
        
        if notification_type == 'documentation_started' and self.documentation_user_id:
            recipients.append(self.documentation_user_id)
        elif notification_type == 'commission_started' and self.commission_user_id:
            recipients.append(self.commission_user_id)
        elif notification_type == 'submitted_for_review' and self.final_review_user_id:
            recipients.append(self.final_review_user_id)
        elif notification_type in ['order_approved', 'order_posted']:
            # Notify all assigned users
            recipients.extend([
                user for user in [
                    self.documentation_user_id,
                    self.commission_user_id, 
                    self.final_review_user_id
                ] if user
            ])
        
        return recipients
    
    def _create_workflow_activity(self, summary, note, user_id):
        """Create workflow activity for assigned users"""
        self.ensure_one()
        
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': summary,
            'note': note,
            'user_id': user_id,
            'res_id': self.id,
            'res_model_id': self.env.ref('sale.model_sale_order').id,
            'date_deadline': fields.Date.context_today(self),
        })
    
    # Permission Check Methods
    def _can_approve_order(self):
        """Check if current user can approve the order"""
        self.ensure_one()
        
        # Check if assigned reviewer
        if self.final_review_user_id and self.final_review_user_id.id == self.env.user.id:
            return True
        
        # Check if approval manager
        if self.env.user.has_group('order_status_override.group_order_approval_manager'):
            return True
        
        return False
    
    def _can_reject_order(self):
        """Check if current user can reject the order"""
        return self._can_approve_order()  # Same permissions for approval and rejection
    
    def _can_post_order(self):
        """Check if order can be posted"""
        self.ensure_one()
        
        # Must be in approved status
        if self.custom_status_id.code != 'approved':
            return False
        
        # Check if user has posting permissions
        if not self.env.user.has_group('order_status_override.group_order_posting'):
            return False
        
        return True
    
    def _can_return_to_previous(self):
        """Check if current user can return order to previous stage"""
        self.ensure_one()
        
        # Managers can always return
        if self.env.user.has_group('order_status_override.group_order_workflow_manager'):
            return True
        
        # Assigned users can return from their stage
        current_code = self.custom_status_id.code
        
        if current_code == 'documentation_progress' and self.documentation_user_id.id == self.env.user.id:
            return True
        elif current_code == 'commission_progress' and self.commission_user_id.id == self.env.user.id:
            return True
        elif current_code == 'final_review' and self.final_review_user_id.id == self.env.user.id:
            return True
        
        return False
    
    # Commission Integration Methods (commission_ax integration)
    def _initialize_commission_data(self):
        """Initialize commission data from commission_ax module"""
        self.ensure_one()
        
        # Create default external commission if none exist
        if not self.external_commission_ids:
            self.env['sale.order.external.commission'].create({
                'order_id': self.id,
                'commission_group': 'broker',
                'calculation_method': 'percentage',
                'rate_amount': 0.0,
            })
        
        # Create default internal commission if none exist  
        if not self.internal_commission_ids:
            self.env['sale.order.internal.commission'].create({
                'order_id': self.id,
                'commission_group': 'agent_1',
                'calculation_method': 'percentage', 
                'rate_amount': 0.0,
            })
    
    def _is_documentation_complete(self):
        """Check if documentation is complete"""
        self.ensure_one()
        
        # Check if documentation signature exists
        if not self.documentation_signature:
            return False
        
        # Add additional documentation completion checks here
        # (e.g., required fields, attachments, etc.)
        
        return True
    
    def _reset_workflow_data(self, target_status_code):
        """Reset workflow data when returning to previous stage"""
        self.ensure_one()
        
        if target_status_code == 'draft':
            # Reset all workflow data
            self.documentation_signature = False
            self.commission_signature = False
            self.final_approval_signature = False
            self.commission_calculated = False
            
        elif target_status_code == 'documentation_progress':
            # Reset commission and approval data
            self.commission_signature = False
            self.final_approval_signature = False
            self.commission_calculated = False
            
        elif target_status_code == 'commission_progress':
            # Reset only approval data
            self.final_approval_signature = False
    
    def _generate_commission_purchase_orders(self):
        """Generate purchase orders for commission payments"""
        self.ensure_one()
        
        try:
            # Use commission_ax module's purchase order generation
            if hasattr(self, 'action_create_commission_purchase_orders'):
                self.action_create_commission_purchase_orders()
            
            _logger.info("Commission purchase orders generated for order %s", self.name)
            
        except Exception as e:
            _logger.error("Failed to generate commission purchase orders for order %s: %s", self.name, str(e))
    
    # API Methods for JavaScript Integration
    @api.model
    def get_workflow_data(self, order_id):
        """Get workflow data for JavaScript components"""
        order = self.browse(order_id)
        
        if not order.exists():
            return {'success': False, 'message': 'Order not found'}
        
        workflow_steps = self.env['order.status'].search([], order='sequence')
        
        return {
            'success': True,
            'current_status': {
                'id': order.custom_status_id.id,
                'code': order.custom_status_id.code,
                'name': order.custom_status_id.name,
            },
            'workflow_steps': [{
                'id': step.id,
                'code': step.code,
                'name': step.name,
                'sequence': step.sequence,
            } for step in workflow_steps],
            'assigned_users': {
                'documentation': order.documentation_user_id.name if order.documentation_user_id else None,
                'commission': order.commission_user_id.name if order.commission_user_id else None,
                'final_review': order.final_review_user_id.name if order.final_review_user_id else None,
            },
            'can_transition': order._can_transition_status(),
            'next_actions': order._get_available_actions(),
        }
    
    def _can_transition_status(self):
        """Check if status can be transitioned"""
        self.ensure_one()
        
        # Add business logic for status transition permissions
        current_code = self.custom_status_id.code
        
        # Basic permission checks
        if current_code == 'posted':
            return False  # Cannot transition from final status
        
        return True
    
    def _get_available_actions(self):
        """Get list of available workflow actions"""
        self.ensure_one()
        
        actions = []
        current_code = self.custom_status_id.code
        
        if current_code == 'draft':
            actions.append('action_request_documentation')
        elif current_code == 'documentation_progress':
            actions.extend(['action_start_commission_calculation', 'action_return_to_previous'])
        elif current_code == 'commission_progress':
            actions.extend(['action_submit_for_review', 'action_return_to_previous'])
        elif current_code == 'final_review':
            actions.extend(['action_approve_order', 'action_reject_order', 'action_return_to_previous'])
        elif current_code == 'approved':
            actions.extend(['action_post_order', 'action_return_to_previous'])
        
        return actions
    
    def get_status_history(self):
        """Get formatted status history for display"""
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
    
    @api.model
    def get_commission_calculation_data(self, order_id):
        """Get commission calculation data for JavaScript components"""
        order = self.browse(order_id)
        
        if not order.exists():
            return {'success': False, 'message': 'Order not found'}
        
        # Get commission data from commission_ax module
        external_commissions = []
        internal_commissions = []
        
        if hasattr(order, 'external_commission_ids'):
            external_commissions = [{
                'id': comm.id,
                'commission_group': comm.commission_group,
                'calculation_method': comm.calculation_method,
                'rate_amount': comm.rate_amount,
                'amount_fixed': comm.amount_fixed,
                'partner_name': comm.partner_id.name if comm.partner_id else '',
            } for comm in order.external_commission_ids]
        
        if hasattr(order, 'internal_commission_ids'):
            internal_commissions = [{
                'id': comm.id,
                'commission_group': comm.commission_group,
                'calculation_method': comm.calculation_method,
                'rate_amount': comm.rate_amount,
                'amount_fixed': comm.amount_fixed,
                'user_name': comm.user_id.name if comm.user_id else '',
            } for comm in order.internal_commission_ids]
        
        total_external = sum(comm['amount_fixed'] for comm in external_commissions)
        total_internal = sum(comm['amount_fixed'] for comm in internal_commissions)
        total_commission = total_external + total_internal
        
        return {
            'success': True,
            'data': {
                'external_commissions': external_commissions,
                'internal_commissions': internal_commissions,
                'total_external': total_external,
                'total_internal': total_internal,
                'total_commission': total_commission,
                'order_total': order.amount_total,
                'commission_percentage': (total_commission / order.amount_total * 100) if order.amount_total else 0,
            }
        }
    
    @api.model
    def get_commission_calculation_methods(self):
        """Get available commission calculation methods"""
        return [
            {'value': 'percentage', 'label': _('Percentage')},
            {'value': 'fixed', 'label': _('Fixed Amount')},
            {'value': 'price_unit', 'label': _('Price Unit')},
        ]
    
    @api.model
    def preview_commission_calculation(self, order_id):
        """Preview commission calculation without saving"""
        order = self.browse(order_id)
        
        if not order.exists():
            return {'success': False, 'message': 'Order not found'}
        
        try:
            # Trigger commission calculation preview
            if hasattr(order, 'calculate_commission_preview'):
                result = order.calculate_commission_preview()
                return {'success': True, 'data': result}
            else:
                # Fallback calculation
                return self.get_commission_calculation_data(order_id)
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @api.model
    def apply_commission_calculations(self, order_id):
        """Apply commission calculations to the order"""
        order = self.browse(order_id)
        
        if not order.exists():
            return {'success': False, 'message': 'Order not found'}
        
        try:
            # Apply commission calculations
            if hasattr(order, 'apply_commission_calculations'):
                order.apply_commission_calculations()
            
            # Mark commission as calculated
            order.commission_calculated = True
            
            # Update deal metrics
            order._update_deal_metrics('commission_calculated')
            
            return {
                'success': True, 
                'message': _('Commission calculations applied successfully')
            }
            
        except Exception as e:
            _logger.error("Failed to apply commission calculations: %s", str(e))
            return {'success': False, 'message': str(e)}
    
    def action_commission_completed(self):
        """Mark commission calculation as completed and ready for review"""
        self.ensure_one()
        
        if not self.commission_calculated:
            raise UserError(_("Commission calculations must be completed first."))
        
        # Auto-transition to review if configured
        auto_transition = self.env['ir.config_parameter'].sudo().get_param(
            'order_status_override.auto_transition_to_review', 'False'
        )
        
        if auto_transition == 'True':
            return self.action_submit_for_review()
        
        return True
    
    # Dashboard and Reporting Methods
    @api.model
    def get_workflow_dashboard_data(self):
        """Get dashboard data for workflow analytics"""
        
        # Get status distribution
        status_data = self.env['order.status'].search([])
        status_distribution = []
        
        for status in status_data:
            count = self.search_count([('custom_status_id', '=', status.id)])
            if count > 0:
                status_distribution.append({
                    'status': status.name,
                    'code': status.code,
                    'count': count,
                    'color': status.color,
                })
        
        # Get recent activity
        recent_orders = self.search([
            ('custom_status_id', '!=', False)
        ], order='write_date desc', limit=10)
        
        recent_activity = [{
            'order_name': order.name,
            'partner_name': order.partner_id.name,
            'status': order.custom_status_id.name,
            'amount': order.amount_total,
            'currency': order.currency_id.name,
            'progress': order.workflow_progress,
            'last_update': order.write_date,
        } for order in recent_orders]
        
        # Calculate performance metrics
        total_orders = self.search_count([('custom_status_id', '!=', False)])
        completed_orders = self.search_count([('custom_status_id.code', '=', 'posted')])
        pending_approval = self.search_count([('custom_status_id.code', '=', 'final_review')])
        
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        return {
            'status_distribution': status_distribution,
            'recent_activity': recent_activity,
            'metrics': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'pending_approval': pending_approval,
                'completion_rate': completion_rate,
            }
        }
    
    # Validation Methods
    @api.constrains('custom_status_id', 'commission_calculated')
    def _check_workflow_constraints(self):
        """Validate workflow constraints"""
        for order in self:
            if order.custom_status_id.code == 'final_review' and not order.commission_calculated:
                raise ValidationError(_("Commission must be calculated before submitting for final review."))
            
            if order.custom_status_id.code == 'posted' and order.state != 'sale':
                raise ValidationError(_("Order must be confirmed before posting."))
    
    @api.constrains('documentation_user_id', 'commission_user_id', 'final_review_user_id')
    def _check_user_assignments(self):
        """Validate user assignments"""
        for order in self:
            current_code = order.custom_status_id.code
            
            if current_code == 'documentation_progress' and not order.documentation_user_id:
                raise ValidationError(_("Documentation user must be assigned for documentation stage."))
            
            if current_code == 'commission_progress' and not order.commission_user_id:
                raise ValidationError(_("Commission user must be assigned for commission stage."))
            
            if current_code == 'final_review' and not order.final_review_user_id:
                raise ValidationError(_("Final review user must be assigned for review stage."))
