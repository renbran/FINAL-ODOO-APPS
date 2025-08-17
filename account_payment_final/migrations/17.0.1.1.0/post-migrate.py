# -*- coding: utf-8 -*-
"""
Post-migration script for payment approval state sync
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration: Sync approval states with posting states"""
    _logger.info("Running payment approval state sync migration")
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    updated_count = 0
    
    # 1. Fix posted payments
    posted_payments = env['account.payment'].search([
        ('state', '=', 'posted'),
        ('approval_state', '!=', 'posted')
    ])
    
    if posted_payments:
        _logger.info("Updating %d posted payments to approval_state=posted", len(posted_payments))
        for payment in posted_payments:
            payment.write({
                'approval_state': 'posted',
                'approver_date': payment.write_date or payment.create_date,
                'authorizer_date': payment.write_date or payment.create_date,
            })
            
            # Set workflow users if missing
            if not payment.reviewer_id and payment.create_uid:
                payment.reviewer_id = payment.create_uid
                payment.reviewer_date = payment.create_date
            
            if not payment.approver_id and payment.write_uid:
                payment.approver_id = payment.write_uid
                payment.approver_date = payment.write_date or payment.create_date
            
            if not payment.authorizer_id and payment.write_uid:
                payment.authorizer_id = payment.write_uid
                payment.authorizer_date = payment.write_date or payment.create_date
                
        updated_count += len(posted_payments)
    
    # 2. Fix cancelled payments
    cancelled_payments = env['account.payment'].search([
        ('state', '=', 'cancel'),
        ('approval_state', '!=', 'cancelled')
    ])
    
    if cancelled_payments:
        _logger.info("Updating %d cancelled payments to approval_state=cancelled", len(cancelled_payments))
        cancelled_payments.write({'approval_state': 'cancelled'})
        updated_count += len(cancelled_payments)
    
    # 3. Fix draft payments
    draft_payments = env['account.payment'].search([
        ('state', '=', 'draft'),
        ('approval_state', 'not in', ['draft', 'under_review'])
    ])
    
    if draft_payments:
        _logger.info("Updating %d draft payments to approval_state=draft", len(draft_payments))
        draft_payments.write({'approval_state': 'draft'})
        updated_count += len(draft_payments)
    
    _logger.info("Payment approval state migration completed. Updated %d payments.", updated_count)
