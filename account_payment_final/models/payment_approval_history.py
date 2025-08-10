# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class PaymentApprovalHistory(models.Model):
    _name = 'payment.approval.history'
    _description = 'Payment Approval History'
    _order = 'approval_date desc'
    _rec_name = 'approval_step'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        required=True,
        ondelete='cascade'
    )
    
    approval_step = fields.Selection([
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('authorized', 'Authorized'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Approval Step', required=True)
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        required=True
    )
    
    approval_date = fields.Datetime(
        string='Approval Date',
        default=fields.Datetime.now,
        required=True
    )
    
    comments = fields.Text(
        string='Comments',
        help="Additional comments or notes for this approval step"
    )
    
    previous_state = fields.Char(
        string='Previous State',
        help="Previous approval state"
    )
    
    new_state = fields.Char(
        string='New State',
        help="New approval state after this action"
    )
    
    signature = fields.Binary(
        string='Digital Signature',
        help="Digital signature for this approval step"
    )
    
    ip_address = fields.Char(
        string='IP Address',
        help="IP address from where approval was performed"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='payment_id.company_id',
        store=True
    )

    def name_get(self):
        """Enhanced name display"""
        result = []
        for record in self:
            name = f"{record.approval_step.title()} by {record.approved_by.name}"
            if record.approval_date:
                name += f" on {record.approval_date.strftime('%Y-%m-%d %H:%M')}"
            result.append((record.id, name))
        return result
