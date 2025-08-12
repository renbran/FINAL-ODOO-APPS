# -*- coding: utf-8 -*-
#############################################################################
#
#    Account Move Integration for Payment Approval
#    Copyright (C) 2025 OSUS Properties
#
#############################################################################

from odoo import fields, models, api, _


class AccountMove(models.Model):
    """Extend Account Move for payment approval integration"""
    _inherit = "account.move"
    
    # Payment approval related fields
    has_approval_payments = fields.Boolean(
        string='Has Approval Payments',
        compute='_compute_has_approval_payments',
        help="Whether this move has associated payments in approval workflow"
    )
    
    approval_payment_count = fields.Integer(
        string='Approval Payments',
        compute='_compute_has_approval_payments',
        help="Number of payments in approval workflow"
    )
    
    pending_approval_amount = fields.Monetary(
        string='Pending Approval Amount',
        compute='_compute_has_approval_payments',
        help="Total amount of payments pending approval"
    )
    
    @api.depends('payment_id', 'line_ids.payment_id')
    def _compute_has_approval_payments(self):
        """Compute approval payment statistics"""
        for move in self:
            # Get all payments related to this move
            payments = move.payment_id
            if not payments:
                # Check for payments in line_ids
                payment_lines = move.line_ids.filtered(lambda l: l.payment_id)
                payments = payment_lines.mapped('payment_id')
            
            # Filter payments that require approval
            approval_payments = payments.filtered('requires_approval')
            
            move.has_approval_payments = bool(approval_payments)
            move.approval_payment_count = len(approval_payments)
            
            # Calculate pending approval amount
            pending_payments = approval_payments.filtered(
                lambda p: p.approval_state in ['submitted', 'under_review', 'approved']
            )
            move.pending_approval_amount = sum(pending_payments.mapped('amount'))
    
    def action_view_approval_payments(self):
        """Open approval payments related to this move"""
        self.ensure_one()
        
        # Get all related payments
        payments = self.payment_id
        if not payments:
            payment_lines = self.line_ids.filtered(lambda l: l.payment_id)
            payments = payment_lines.mapped('payment_id')
        
        approval_payments = payments.filtered('requires_approval')
        
        if not approval_payments:
            return
        
        if len(approval_payments) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'res_id': approval_payments.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Approval Payments'),
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', approval_payments.ids)],
                'target': 'current',
            }
