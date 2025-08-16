# -*- coding: utf-8 -*-
"""
Payment Workflow Model - Centralized workflow management
Handles workflow transitions, validations, and business rules
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class PaymentWorkflow(models.Model):
    """
    Payment Workflow Engine
    
    Centralizes workflow logic for payment vouchers including:
    - State transition validation
    - Permission checking
    - Activity management
    - Notification handling
    """
    _name = 'payment.workflow'
    _description = 'Payment Approval Workflow Engine'

    # ================================
    # WORKFLOW CONFIGURATION
    # ================================
    
    # Define valid state transitions
    VALID_TRANSITIONS = {
        'draft': ['review', 'cancel'],
        'review': ['approve', 'draft', 'cancel'],
        'approve': ['authorize', 'review', 'cancel'],
        'authorize': ['paid', 'approve', 'cancel'],
        'paid': [],
        'cancel': ['draft']
    }
    
    # Define required groups for each action
    ACTION_GROUPS = {
        'review': 'payment_approval_pro.group_payment_reviewer',
        'approve': 'payment_approval_pro.group_payment_approver',
        'authorize': 'payment_approval_pro.group_payment_authorizer',
        'cancel': 'payment_approval_pro.group_payment_manager',
        'reset': 'payment_approval_pro.group_payment_manager',
    }

    @api.model
    def validate_transition(self, voucher, target_state):
        """
        Validate if state transition is allowed
        
        Args:
            voucher: payment.voucher record
            target_state: target state to transition to
            
        Returns:
            bool: True if transition is valid
            
        Raises:
            ValidationError: If transition is not allowed
        """
        current_state = voucher.state
        
        if target_state not in self.VALID_TRANSITIONS.get(current_state, []):
            current_label = dict(voucher._fields['state'].selection).get(current_state)
            target_label = dict(voucher._fields['state'].selection).get(target_state)
            
            raise ValidationError(
                _("Invalid state transition from '%s' to '%s' for voucher %s") % 
                (current_label, target_label, voucher.voucher_number)
            )
        
        return True
    
    @api.model
    def check_user_permissions(self, action, user=None):
        """
        Check if user has permission for specific action
        
        Args:
            action: action to check (review, approve, authorize, etc.)
            user: user to check (default: current user)
            
        Returns:
            bool: True if user has permission
            
        Raises:
            UserError: If user doesn't have permission
        """
        if user is None:
            user = self.env.user
        
        required_group = self.ACTION_GROUPS.get(action)
        if not required_group:
            return True  # No specific permission required
        
        if not user.has_group(required_group):
            group_name = self.env.ref(required_group).name
            raise UserError(
                _("You don't have permission to perform this action. Required group: %s") % group_name
            )
        
        return True
    
    @api.model
    def process_transition(self, voucher, target_state, user=None, context=None):
        """
        Process complete state transition with validation
        
        Args:
            voucher: payment.voucher record
            target_state: target state
            user: user performing action (default: current user)
            context: additional context data
            
        Returns:
            dict: Result of transition
        """
        if user is None:
            user = self.env.user
        
        if context is None:
            context = {}
        
        # Validate transition
        self.validate_transition(voucher, target_state)
        
        # Check permissions based on target state
        action_map = {
            'review': 'review',
            'approve': 'approve', 
            'authorize': 'authorize',
            'cancel': 'cancel',
            'draft': 'reset'
        }
        
        action = action_map.get(target_state)
        if action:
            self.check_user_permissions(action, user)
        
        # Perform business validation
        self._validate_business_rules(voucher, target_state, context)
        
        # Execute transition
        result = self._execute_transition(voucher, target_state, user, context)
        
        _logger.info(
            f"Payment voucher {voucher.voucher_number} transitioned from "
            f"{voucher.state} to {target_state} by user {user.name}"
        )
        
        return result
    
    def _validate_business_rules(self, voucher, target_state, context):
        """
        Validate business rules for transition
        
        Args:
            voucher: payment.voucher record
            target_state: target state
            context: additional context
        """
        # Review validation
        if target_state == 'review':
            if not voucher.partner_id:
                raise ValidationError(_("Vendor/Payee is required before review"))
            
            if not voucher.amount or voucher.amount <= 0:
                raise ValidationError(_("Valid amount is required before review"))
            
            if not voucher.journal_id:
                raise ValidationError(_("Payment journal is required before review"))
        
        # Approval validation
        elif target_state == 'approve':
            if voucher.state != 'review':
                raise ValidationError(_("Only vouchers under review can be approved"))
            
            if not voucher.reviewer_id:
                raise ValidationError(_("Voucher must have an assigned reviewer"))
        
        # Authorization validation
        elif target_state == 'authorize':
            if voucher.state != 'approve':
                raise ValidationError(_("Only approved vouchers can be authorized"))
            
            if not voucher.approver_id:
                raise ValidationError(_("Voucher must be approved before authorization"))
            
            # Check journal has sufficient balance (if configured)
            if voucher.journal_id and hasattr(voucher.journal_id, 'check_balance'):
                if voucher.journal_id.check_balance and voucher.journal_id.balance < voucher.amount:
                    raise ValidationError(_("Insufficient balance in payment journal"))
        
        # Payment validation
        elif target_state == 'paid':
            if voucher.state != 'authorize':
                raise ValidationError(_("Only authorized vouchers can be marked as paid"))
            
            if not voucher.payment_id:
                raise ValidationError(_("No payment record found for this voucher"))
    
    def _execute_transition(self, voucher, target_state, user, context):
        """
        Execute the actual state transition
        
        Args:
            voucher: payment.voucher record
            target_state: target state
            user: user performing action
            context: additional context
            
        Returns:
            dict: Transition result
        """
        update_vals = {'state': target_state}
        timestamp = fields.Datetime.now()
        
        # Set specific fields based on target state
        if target_state == 'review':
            update_vals.update({
                'review_date': timestamp,
                'reviewer_id': self._get_next_user_for_role('reviewer').id
            })
        
        elif target_state == 'approve':
            update_vals.update({
                'approval_date': timestamp,
                'approver_id': user.id
            })
        
        elif target_state == 'authorize':
            update_vals.update({
                'authorization_date': timestamp,
                'authorizer_id': user.id
            })
        
        elif target_state == 'paid':
            update_vals.update({
                'payment_posted_date': timestamp
            })
        
        elif target_state == 'draft':
            # Reset workflow fields
            update_vals.update({
                'reviewer_id': False,
                'approver_id': False,
                'authorizer_id': False,
                'review_date': False,
                'approval_date': False,
                'authorization_date': False,
                'payment_posted_date': False
            })
        
        # Update voucher
        voucher.write(update_vals)
        
        # Manage activities
        self._manage_activities(voucher, target_state, user)
        
        # Send notifications
        self._send_workflow_notifications(voucher, target_state, user, context)
        
        return {
            'success': True,
            'message': _("Voucher %s successfully transitioned to %s") % (
                voucher.voucher_number, 
                dict(voucher._fields['state'].selection).get(target_state)
            ),
            'voucher_id': voucher.id,
            'new_state': target_state
        }
    
    def _get_next_user_for_role(self, role):
        """
        Get next available user for specific role
        
        Args:
            role: role name (reviewer, approver, authorizer)
            
        Returns:
            res.users: Next available user
        """
        role_group_map = {
            'reviewer': 'payment_approval_pro.group_payment_reviewer',
            'approver': 'payment_approval_pro.group_payment_approver',
            'authorizer': 'payment_approval_pro.group_payment_authorizer'
        }
        
        group_ref = role_group_map.get(role)
        if not group_ref:
            raise ValueError(f"Unknown role: {role}")
        
        users = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref(group_ref).id),
            ('active', '=', True)
        ])
        
        if not users:
            raise UserError(_(f"No active users found for role: {role}"))
        
        # Simple round-robin assignment (can be enhanced with workload balancing)
        return users[0]
    
    def _manage_activities(self, voucher, target_state, user):
        """
        Manage activities based on state transition
        
        Args:
            voucher: payment.voucher record
            target_state: new state
            user: user performing action
        """
        # Cancel existing activities for completed states
        if target_state in ('paid', 'cancel'):
            voucher.activity_ids.action_close()
        
        # Create new activities for pending states
        elif target_state == 'review':
            voucher.activity_schedule(
                'payment_approval_pro.mail_activity_payment_review',
                user_id=voucher.reviewer_id.id,
                summary=f"Review payment voucher {voucher.voucher_number}"
            )
        
        elif target_state == 'approve':
            # Close review activities
            review_activities = voucher.activity_ids.filtered(
                lambda a: a.activity_type_id.xml_id == 'payment_approval_pro.mail_activity_payment_review'
            )
            review_activities.action_done()
            
            # Create authorization activity
            next_authorizer = self._get_next_user_for_role('authorizer')
            voucher.activity_schedule(
                'payment_approval_pro.mail_activity_payment_authorize',
                user_id=next_authorizer.id,
                summary=f"Authorize payment voucher {voucher.voucher_number}"
            )
    
    def _send_workflow_notifications(self, voucher, target_state, user, context):
        """
        Send workflow notifications
        
        Args:
            voucher: payment.voucher record
            target_state: new state
            user: user performing action
            context: additional context
        """
        notification_map = {
            'review': 'payment_approval_pro.email_template_payment_review',
            'approve': 'payment_approval_pro.email_template_payment_approved',
            'authorize': 'payment_approval_pro.email_template_payment_authorized',
            'paid': 'payment_approval_pro.email_template_payment_paid',
            'cancel': 'payment_approval_pro.email_template_payment_cancelled'
        }
        
        template_ref = notification_map.get(target_state)
        if template_ref:
            try:
                template = self.env.ref(template_ref)
                template.with_context(
                    transition_user=user,
                    **context
                ).send_mail(voucher.id, force_send=False)
            except Exception as e:
                _logger.warning(f"Failed to send notification for {target_state}: {e}")


class PaymentWorkflowHistory(models.Model):
    """
    Payment Workflow History
    
    Tracks workflow history for auditing and reporting
    """
    _name = 'payment.workflow.history'
    _description = 'Payment Workflow History'
    _order = 'create_date desc'

    voucher_id = fields.Many2one(
        'payment.voucher',
        string='Payment Voucher',
        required=True,
        ondelete='cascade'
    )
    
    from_state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approve', 'Approved'),
        ('authorize', 'Authorized'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='From State')
    
    to_state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approve', 'Approved'),
        ('authorize', 'Authorized'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='To State', required=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user
    )
    
    transition_date = fields.Datetime(
        string='Transition Date',
        required=True,
        default=fields.Datetime.now
    )
    
    notes = fields.Text(string='Notes')
    
    ip_address = fields.Char(string='IP Address')
    
    @api.model
    def log_transition(self, voucher, from_state, to_state, notes=None):
        """
        Log workflow transition for audit trail
        
        Args:
            voucher: payment.voucher record
            from_state: previous state
            to_state: new state
            notes: optional notes
        """
        vals = {
            'voucher_id': voucher.id,
            'from_state': from_state,
            'to_state': to_state,
            'notes': notes or '',
        }
        
        # Try to get IP address from request
        try:
            if hasattr(self.env, 'request') and self.env.request:
                vals['ip_address'] = self.env.request.httprequest.remote_addr
        except:
            pass
        
        return self.create(vals)
