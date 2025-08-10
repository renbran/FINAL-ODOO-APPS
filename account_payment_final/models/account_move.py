# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # Add workflow for invoices/bills
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('for_approval', 'For Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Approval State', default='draft', tracking=True,
       help="Current approval state for invoices and bills")
    
    # Workflow tracking fields
    reviewer_id = fields.Many2one('res.users', string='Reviewed By', readonly=True)
    reviewer_date = fields.Datetime(string='Review Date', readonly=True)
    
    approver_id = fields.Many2one('res.users', string='Approved By', readonly=True)
    approver_date = fields.Datetime(string='Approval Date', readonly=True)
    
    voucher_count = fields.Integer(
        string='Payment Vouchers',
        compute='_compute_voucher_count'
    )
    
    # Enhanced fields for invoice approval
    approval_remarks = fields.Text(
        string='Approval Remarks',
        help="Additional remarks for approval workflow"
    )
    
    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
        help="Whether this invoice/bill requires approval workflow"
    )
    
    @api.depends('move_type', 'amount_total', 'company_id')
    def _compute_requires_approval(self):
        """Determine if invoice/bill requires approval based on amount and type"""
        for move in self:
            if move.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                # Check if amount exceeds company threshold
                threshold = move.company_id.invoice_approval_threshold or 5000.0
                move.requires_approval = move.amount_total >= threshold
            else:
                move.requires_approval = False
    
    @api.depends('line_ids.payment_id')
    def _compute_voucher_count(self):
        """Count related payment vouchers"""
        for move in self:
            vouchers = self.env['account.payment'].search([
                '|',
                ('reconciled_invoice_ids', 'in', move.ids),
                ('reconciled_bill_ids', 'in', move.ids)
            ])
            move.voucher_count = len(vouchers)
    
    def action_view_vouchers(self):
        """View related payment vouchers"""
        self.ensure_one()
        vouchers = self.env['account.payment'].search([
            '|',
            ('reconciled_invoice_ids', 'in', self.ids),
            ('reconciled_bill_ids', 'in', self.ids)
        ])
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Payment Vouchers',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', vouchers.ids)],
            'context': {'default_partner_id': self.partner_id.id}
        }
    
    # ============================================================================
    # INVOICE/BILL APPROVAL WORKFLOW
    # ============================================================================
    
    def action_submit_for_review(self):
        """Submit invoice/bill for review workflow"""
        self.ensure_one()
        
        if self.move_type not in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            raise UserError(_("Approval workflow is only available for invoices and bills."))
        
        self._validate_invoice_data()
        
        self.write({
            'approval_state': 'under_review'
        })
        
        # Create activity for reviewers
        self._create_invoice_activities('review')
        self._send_invoice_notification('submitted')
        self._post_invoice_message("submitted for review")
        
        return self._return_success_notification(_('Invoice/Bill submitted for review.'))
    
    def action_review_approve(self):
        """Review invoice/bill and forward to approval"""
        self.ensure_one()
        self._check_invoice_permission('review')
        
        self.write({
            'approval_state': 'for_approval',
            'reviewer_id': self.env.user.id,
            'reviewer_date': fields.Datetime.now(),
        })
        
        # Create activity for approvers
        self._create_invoice_activities('approve')
        self._send_invoice_notification('reviewed')
        self._post_invoice_message("reviewed and forwarded for approval")
        
        return self._return_success_notification(_('Invoice/Bill reviewed successfully.'))
    
    def action_final_approve(self):
        """Final approval and auto-post if enabled"""
        self.ensure_one()
        self._check_invoice_permission('approve')
        
        self.write({
            'approval_state': 'approved',
            'approver_id': self.env.user.id,
            'approver_date': fields.Datetime.now(),
        })
        
        # Auto-post if enabled
        if self.company_id.auto_post_approved_invoices and self.state == 'draft':
            try:
                self.action_post()
                self.approval_state = 'posted'
                message = "approved and automatically posted"
            except Exception as e:
                _logger.warning(f"Failed to auto-post invoice {self.name}: {e}")
                message = "approved (manual posting required)"
        else:
            message = "approved and ready for posting"
        
        # Close activities
        self.activity_ids.action_done()
        
        self._send_invoice_notification('approved')
        self._post_invoice_message(message)
        
        return self._return_success_notification(_('Invoice/Bill approved successfully.'))
    
    def action_post_invoice_bill(self):
        """Manual posting of approved invoice/bill"""
        self.ensure_one()
        
        if self.approval_state != 'approved':
            raise UserError(_("Invoice/Bill must be approved before posting."))
        
        # Use standard Odoo posting
        result = self.action_post()
        
        self.write({
            'approval_state': 'posted'
        })
        
        self._post_invoice_message("manually posted to ledger")
        
        return result
    
    def action_reject_invoice_bill(self):
        """Reject invoice/bill and return to draft"""
        self.ensure_one()
        self._check_invoice_rejection_permissions()
        
        # Reset to draft
        self.write({
            'approval_state': 'draft',
            'reviewer_id': False,
            'reviewer_date': False,
            'approver_id': False,
            'approver_date': False,
        })
        
        # Close all activities
        self.activity_ids.action_done()
        
        self._send_invoice_notification('rejected')
        self._post_invoice_message("rejected and returned to draft")
        
        return self._return_success_notification(_('Invoice/Bill rejected and returned to draft.'))
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _validate_invoice_data(self):
        """Validate invoice/bill data before submission"""
        if not self.partner_id:
            raise ValidationError(_("Partner must be specified."))
        if not self.invoice_date:
            raise ValidationError(_("Invoice date must be specified."))
        if not self.invoice_line_ids:
            raise ValidationError(_("Invoice must have at least one line."))
        if self.amount_total <= 0:
            raise ValidationError(_("Invoice amount must be greater than zero."))
    
    def _check_invoice_permission(self, action):
        """Check if user has permission for invoice workflow action"""
        permission_map = {
            'review': 'payment_voucher_enhanced.group_payment_voucher_reviewer',
            'approve': 'payment_voucher_enhanced.group_invoice_approver',
        }
        
        required_group = permission_map.get(action)
        if required_group and not self.env.user.has_group(required_group):
            raise AccessError(_("You don't have permission to %s invoices/bills.") % action)
    
    def _check_invoice_rejection_permissions(self):
        """Check if user can reject at current stage"""
        current_stage = self.approval_state
        
        if current_stage == 'under_review':
            if not self.env.user.has_group('payment_voucher_enhanced.group_payment_voucher_reviewer'):
                raise AccessError(_("You don't have permission to reject at review stage."))
        elif current_stage == 'for_approval':
            if not self.env.user.has_group('payment_voucher_enhanced.group_invoice_approver'):
                raise AccessError(_("You don't have permission to reject at approval stage."))
        else:
            raise AccessError(_("Cannot reject invoice/bill in current state."))
    
    def _create_invoice_activities(self, activity_type):
        """Create activities for invoice workflow stages"""
        activity_map = {
            'review': 'payment_voucher_enhanced.group_payment_voucher_reviewer',
            'approve': 'payment_voucher_enhanced.group_invoice_approver',
        }
        
        group_ref = activity_map.get(activity_type)
        if group_ref:
            try:
                group = self.env.ref(group_ref)
                for user in group.users:
                    action_name = activity_type.title()
                    doc_type = 'Invoice' if self.move_type.startswith('out_') else 'Bill'
                    self.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=f'{action_name} {doc_type} {self.name}',
                        note=f'{doc_type} for {self.partner_id.name} - Amount: {self.currency_id.symbol or ""}{self.amount_total:,.2f}',
                        user_id=user.id,
                    )
            except Exception as e:
                _logger.warning(f"Failed to create invoice activities: {e}")
    
    def _post_invoice_message(self, action):
        """Post message to chatter for invoice workflow actions"""
        doc_type = 'Invoice' if self.move_type.startswith('out_') else 'Bill'
        body = _("%s %s %s by %s") % (
            doc_type,
            self.name,
            action,
            self.env.user.name
        )
        self.message_post(
            body=body,
            subject=_("%s %s") % (doc_type, action.title())
        )
    
    def _send_invoice_notification(self, notification_type):
        """Send email notifications for invoice workflow actions"""
        template_map = {
            'submitted': 'payment_voucher_enhanced.email_template_invoice_submitted',
            'reviewed': 'payment_voucher_enhanced.email_template_invoice_reviewed',
            'approved': 'payment_voucher_enhanced.email_template_invoice_approved',
            'rejected': 'payment_voucher_enhanced.email_template_invoice_rejected',
        }
        
        template_ref = template_map.get(notification_type)
        if template_ref and self.company_id.send_approval_notifications:
            try:
                template = self.env.ref(template_ref, raise_if_not_found=False)
                if template:
                    template.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.warning(f"Failed to send invoice notification email: {e}")
    
    def _return_success_notification(self, message):
        """Return success notification"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
    
    # ============================================================================
    # OVERRIDE STANDARD METHODS
    # ============================================================================
    
    def action_post(self):
        """Override standard post to check approval requirements"""
        for move in self:
            # Check if invoice/bill requires approval
            if (move.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'] 
                and move.requires_approval 
                and move.approval_state not in ['approved', 'posted']):
                raise UserError(
                    _("Invoice/Bill %s requires approval before posting. "
                      "Current state: %s") % (move.name, move.approval_state)
                )
        
        # Call standard post method
        result = super().action_post()
        
        # Update approval state for approved invoices
        for move in self:
            if (move.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund'] 
                and move.approval_state == 'approved'):
                move.approval_state = 'posted'
        
        return result