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
                lambda p: p.voucher_state in ['submitted', 'under_review', 'approved']
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

    # Additional fields for enhanced tracking
    fully_reconciled = fields.Boolean(
        string='Fully Reconciled',
        compute='_compute_reconciliation_status',
        help="Whether all lines in this move are fully reconciled"
    )
    
    total_matched_amount = fields.Monetary(
        string='Total Matched Amount',
        compute='_compute_reconciliation_status',
        help="Total amount that has been reconciled"
    )
    
    total_outstanding_amount = fields.Monetary(
        string='Total Outstanding Amount',
        compute='_compute_reconciliation_status',
        help="Total amount still outstanding"
    )
    
    reconciliation_summary = fields.Html(
        string='Reconciliation Summary',
        compute='_compute_reconciliation_summary',
        help="HTML summary of reconciliation status"
    )
    
    approval_timeline = fields.Json(
        string='Approval Timeline',
        compute='_compute_approval_timeline',
        help="Timeline data for approval workflow visualization"
    )

    @api.depends('line_ids.full_reconcile_id', 'line_ids.matched_debit_ids', 'line_ids.matched_credit_ids')
    def _compute_reconciliation_status(self):
        """Compute reconciliation status information"""
        for move in self:
            reconciled_lines = move.line_ids.filtered('full_reconcile_id')
            partially_reconciled_lines = move.line_ids.filtered(
                lambda l: l.matched_debit_ids or l.matched_credit_ids
            )
            
            move.fully_reconciled = len(reconciled_lines) == len(move.line_ids.filtered(lambda l: l.account_id.reconcile))
            
            # Calculate matched amounts
            matched_amount = sum(reconciled_lines.mapped('debit')) + sum(reconciled_lines.mapped('credit'))
            move.total_matched_amount = matched_amount / 2  # Avoid double counting
            
            # Calculate outstanding amounts
            outstanding_lines = move.line_ids.filtered(
                lambda l: l.account_id.reconcile and not l.full_reconcile_id
            )
            move.total_outstanding_amount = sum(outstanding_lines.mapped('amount_residual'))

    def _compute_reconciliation_summary(self):
        """Generate HTML reconciliation summary"""
        for move in self:
            html_content = []
            html_content.append('<div class="o_reconciliation_summary_content">')
            
            # Reconciliation overview
            reconciled_count = len(move.line_ids.filtered('full_reconcile_id'))
            total_reconcilable = len(move.line_ids.filtered(lambda l: l.account_id.reconcile))
            
            html_content.append(f'<h5>Reconciliation Overview</h5>')
            html_content.append(f'<p><strong>Reconciled Lines:</strong> {reconciled_count}/{total_reconcilable}</p>')
            html_content.append(f'<p><strong>Status:</strong> {"Fully Reconciled" if move.fully_reconciled else "Partially Reconciled"}</p>')
            
            # Line by line breakdown
            if move.line_ids:
                html_content.append('<h6>Line Details:</h6>')
                html_content.append('<table class="table table-sm">')
                html_content.append('<thead><tr><th>Account</th><th>Amount</th><th>Status</th><th>Matched Invoice</th></tr></thead>')
                html_content.append('<tbody>')
                
                for line in move.line_ids.filtered(lambda l: l.account_id.reconcile):
                    status = "Reconciled" if line.full_reconcile_id else "Outstanding"
                    status_class = "text-success" if line.full_reconcile_id else "text-warning"
                    matched_invoice = line.matched_invoice_id.name if hasattr(line, 'matched_invoice_id') and line.matched_invoice_id else "None"
                    
                    html_content.append(
                        f'<tr>'
                        f'<td>{line.account_id.name}</td>'
                        f'<td>{abs(line.debit or line.credit):.2f}</td>'
                        f'<td><span class="{status_class}">{status}</span></td>'
                        f'<td>{matched_invoice}</td>'
                        f'</tr>'
                    )
                
                html_content.append('</tbody></table>')
            
            html_content.append('</div>')
            move.reconciliation_summary = ''.join(html_content)

    def _compute_approval_timeline(self):
        """Generate approval timeline data for visualization"""
        for move in self:
            timeline_data = []
            
            # Get related payments
            payments = move.payment_id
            if not payments:
                payment_lines = move.line_ids.filtered(lambda l: l.payment_id)
                payments = payment_lines.mapped('payment_id')
            
            approval_payments = payments.filtered('requires_approval')
            
            for payment in approval_payments:
                timeline_data.append({
                    'payment_id': payment.id,
                    'payment_name': payment.name,
                    'voucher_number': payment.voucher_number,
                    'amount': payment.amount,
                    'current_state': payment.voucher_state,
                    'timeline': [
                        {
                            'state': 'draft',
                            'date': payment.create_date.strftime('%Y-%m-%d %H:%M') if payment.create_date else None,
                            'user': payment.create_uid.name if payment.create_uid else None,
                            'completed': True
                        },
                        {
                            'state': 'submitted',
                            'date': payment.submitted_date.strftime('%Y-%m-%d %H:%M') if payment.submitted_date else None,
                            'user': payment.create_uid.name if payment.create_uid else None,
                            'completed': payment.voucher_state in ['submitted', 'under_review', 'approved', 'authorized', 'posted']
                        },
                        {
                            'state': 'under_review',
                            'date': payment.reviewed_date.strftime('%Y-%m-%d %H:%M') if payment.reviewed_date else None,
                            'user': payment.reviewer_id.name if payment.reviewer_id else None,
                            'completed': payment.voucher_state in ['under_review', 'approved', 'authorized', 'posted']
                        },
                        {
                            'state': 'approved',
                            'date': payment.approved_date.strftime('%Y-%m-%d %H:%M') if payment.approved_date else None,
                            'user': payment.approver_id.name if payment.approver_id else None,
                            'completed': payment.voucher_state in ['approved', 'authorized', 'posted']
                        },
                        {
                            'state': 'authorized',
                            'date': payment.authorized_date.strftime('%Y-%m-%d %H:%M') if payment.authorized_date else None,
                            'user': payment.authorizer_id.name if payment.authorizer_id else None,
                            'completed': payment.voucher_state in ['authorized', 'posted']
                        },
                        {
                            'state': 'posted',
                            'date': payment.post_date.strftime('%Y-%m-%d %H:%M') if hasattr(payment, 'post_date') and payment.post_date else None,
                            'user': payment.write_uid.name if payment.write_uid else None,
                            'completed': payment.voucher_state == 'posted'
                        }
                    ]
                })
            
            move.approval_timeline = timeline_data

    def action_view_reconciliation_navigator(self):
        """Open reconciliation navigator for this move"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reconciliation Navigator - %s') % self.name,
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': [('move_id', '=', self.id)],
            'context': {
                'search_default_account_reconcile': 1,
                'default_move_id': self.id,
            },
            'target': 'current',
        }

    def action_view_matched_invoices(self):
        """View invoices matched through reconciliation"""
        self.ensure_one()
        
        matched_moves = self.env['account.move']
        for line in self.line_ids:
            if line.full_reconcile_id:
                reconciled_lines = line.full_reconcile_id.reconciled_line_ids
                matched_moves |= reconciled_lines.mapped('move_id') - self
        
        if not matched_moves:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Matched Invoices'),
                    'message': _('No invoices have been matched through reconciliation.'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Matched Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', matched_moves.ids)],
            'target': 'current',
        }

    def action_refresh_approval_status(self):
        """Refresh approval status computation"""
        self._compute_has_approval_payments()
        self._compute_reconciliation_status()
        self._compute_reconciliation_summary()
        self._compute_approval_timeline()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Status Refreshed'),
                'message': _('Approval and reconciliation status has been refreshed.'),
                'type': 'success',
            }
        }


class AccountMoveLine(models.Model):
    """Enhanced Account Move Line with payment approval and reconciliation navigation"""
    _inherit = "account.move.line"
    
    # Payment tracking fields
    payment_state = fields.Selection(
        related='payment_id.state',
        string='Payment State',
        readonly=True,
        help="State of the associated payment"
    )
    
    payment_voucher_state = fields.Selection(
        related='payment_id.voucher_state',
        string='Payment Approval State',
        readonly=True,
        help="Approval state of the associated payment"
    )
    
    # Reconciliation navigation fields
    matched_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Matched Invoice',
        compute='_compute_matched_invoice',
        help="Invoice matched through reconciliation"
    )
    
    reconcile_status = fields.Selection([
        ('unreconciled', 'Unreconciled'),
        ('partially_reconciled', 'Partially Reconciled'),
        ('fully_reconciled', 'Fully Reconciled'),
    ], string='Reconcile Status', compute='_compute_reconcile_status')
    
    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_outstanding_amount',
        help="Amount still to be reconciled"
    )

    @api.depends('matched_debit_ids', 'matched_credit_ids')
    def _compute_matched_invoice(self):
        """Find the main invoice matched through reconciliation"""
        for line in self:
            matched_invoice = self.env['account.move']
            
            # Check if full_reconcile_id field exists
            if hasattr(line, 'full_reconcile_id') and line.full_reconcile_id:
                # Get all reconciled lines
                reconciled_lines = line.full_reconcile_id.reconciled_line_ids
                # Find invoice moves (excluding current move)
                invoice_moves = reconciled_lines.mapped('move_id').filtered(
                    lambda m: m != line.move_id and m.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
                )
                if invoice_moves:
                    matched_invoice = invoice_moves[0]  # Take the first one
            elif line.matched_debit_ids or line.matched_credit_ids:
                # Fallback to matched lines
                matched_lines = line.matched_debit_ids + line.matched_credit_ids
                invoice_moves = matched_lines.mapped('move_id').filtered(
                    lambda m: m != line.move_id and m.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
                )
                if invoice_moves:
                    matched_invoice = invoice_moves[0]
            
            line.matched_invoice_id = matched_invoice

    @api.depends('matched_debit_ids', 'matched_credit_ids', 'amount_residual')
    def _compute_reconcile_status(self):
        """Compute reconciliation status"""
        for line in self:
            if not line.account_id.reconcile:
                line.reconcile_status = 'unreconciled'
            elif hasattr(line, 'full_reconcile_id') and line.full_reconcile_id:
                line.reconcile_status = 'fully_reconciled'
            elif line.matched_debit_ids or line.matched_credit_ids:
                line.reconcile_status = 'partially_reconciled'
            else:
                line.reconcile_status = 'unreconciled'

    @api.depends('amount_residual')
    def _compute_outstanding_amount(self):
        """Compute outstanding amount for reconciliation"""
        for line in self:
            line.outstanding_amount = abs(line.amount_residual) if line.account_id.reconcile else 0.0

    def action_view_payment(self):
        """Navigate to associated payment"""
        self.ensure_one()
        if not self.payment_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_matched_invoice(self):
        """Navigate to matched invoice"""
        self.ensure_one()
        if not self.matched_invoice_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.matched_invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_reconciliation_history(self):
        """View reconciliation history for this line"""
        self.ensure_one()
        
        domain = []
        if self.full_reconcile_id:
            domain = [('full_reconcile_id', '=', self.full_reconcile_id.id)]
        elif self.matched_debit_ids or self.matched_credit_ids:
            matched_ids = self.matched_debit_ids.ids + self.matched_credit_ids.ids
            domain = ['|', ('matched_debit_ids', 'in', matched_ids), ('matched_credit_ids', 'in', matched_ids)]
        else:
            domain = [('id', '=', self.id)]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reconciliation History'),
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_account_reconcile': 1},
            'target': 'current',
        }

    def get_payment_approval_badge_data(self):
        """Get badge data for payment approval status"""
        self.ensure_one()
        
        payment_lines = self.line_ids.filtered(lambda l: l.payment_id)
        if not payment_lines:
            return {'status': 'no_payments', 'count': 0}
        
        payments = payment_lines.mapped('payment_id')
        approval_payments = payments.filtered('requires_approval')
        
        if not approval_payments:
            return {'status': 'no_payments', 'count': 0}
        
        # Get the most common status
        status_counts = {}
        for payment in approval_payments:
            status = payment.voucher_state
            status_counts[status] = status_counts.get(status, 0) + 1
        
        most_common_status = max(status_counts, key=status_counts.get)
        
        return {
            'status': most_common_status,
            'count': len(approval_payments),
        }
