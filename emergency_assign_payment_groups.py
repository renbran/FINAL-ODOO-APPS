#!/usr/bin/env python3
"""
EMERGENCY: Assign Payment Security Groups to Existing Users
This script ensures all existing users have appropriate payment workflow permissions
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def assign_payment_groups_to_users(cr):
    """Assign payment security groups to users to prevent permission errors"""
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    try:
        # Get payment security groups
        reviewer_group = env.ref('account_payment_final.group_payment_reviewer')
        approver_group = env.ref('account_payment_final.group_payment_approver') 
        authorizer_group = env.ref('account_payment_final.group_payment_authorizer')
        manager_group = env.ref('account_payment_final.group_payment_manager')
        
        # Get all active users
        all_users = env['res.users'].search([
            ('active', '=', True),
            ('share', '=', False)  # Internal users only
        ])
        
        _logger.info("Found %d internal users to process", len(all_users))
        
        for user in all_users:
            try:
                user_groups = user.groups_id
                groups_to_add = []
                
                # Logic: If user has accounting access, give them payment permissions
                accounting_groups = [
                    'account.group_account_user',
                    'account.group_account_manager',
                    'base.group_erp_manager'
                ]
                
                has_accounting_access = any(
                    env.ref(group_ref, raise_if_not_found=False) in user_groups 
                    for group_ref in accounting_groups
                )
                
                if has_accounting_access:
                    # Give comprehensive payment permissions to accounting users
                    if reviewer_group not in user_groups:
                        groups_to_add.append(reviewer_group.id)
                    if approver_group not in user_groups:
                        groups_to_add.append(approver_group.id)
                    if authorizer_group not in user_groups:
                        groups_to_add.append(authorizer_group.id)
                    if manager_group not in user_groups:
                        groups_to_add.append(manager_group.id)
                        
                    _logger.info("Adding payment groups to accounting user: %s", user.name)
                
                # Special handling for admin users
                elif env.ref('base.group_erp_manager', raise_if_not_found=False) in user_groups:
                    # Give all permissions to admin users
                    if reviewer_group not in user_groups:
                        groups_to_add.append(reviewer_group.id)
                    if approver_group not in user_groups:
                        groups_to_add.append(approver_group.id)
                    if authorizer_group not in user_groups:
                        groups_to_add.append(authorizer_group.id)
                    if manager_group not in user_groups:
                        groups_to_add.append(manager_group.id)
                        
                    _logger.info("Adding payment groups to admin user: %s", user.name)
                
                # For other users, give at least reviewer permissions if they created payments
                else:
                    payments_created = env['account.payment'].search_count([
                        ('create_uid', '=', user.id)
                    ])
                    
                    if payments_created > 0:
                        if reviewer_group not in user_groups:
                            groups_to_add.append(reviewer_group.id)
                        _logger.info("Adding reviewer group to payment creator: %s", user.name)
                
                # Apply the groups
                if groups_to_add:
                    user.write({
                        'groups_id': [(4, group_id) for group_id in groups_to_add]
                    })
                    _logger.info("Added %d payment groups to user %s", len(groups_to_add), user.name)
                
            except Exception as e:
                _logger.error("Failed to update user %s: %s", user.name, str(e))
                continue
        
        cr.commit()
        _logger.info("Successfully updated payment permissions for all users")
        
    except Exception as e:
        _logger.error("Failed to assign payment groups: %s", str(e))
        raise

if __name__ == "__main__":
    # This would be called from an Odoo shell or migration script
    print("Emergency payment group assignment script ready")
    print("To run: Use this in an Odoo shell or migration script")
