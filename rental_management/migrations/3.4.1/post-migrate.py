# -*- coding: utf-8 -*-
"""
Migration to v3.4.1 - Two-Stage Payment Workflow

This migration updates existing contracts to be compatible with the new
booking requirements system.
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migrate existing contracts to v3.4.1 two-stage workflow compatibility.
    
    Updates:
    - Set invoice types for existing invoices
    - Ensure old contracts can create installments
    - Recompute booking requirements for all contracts
    """
    _logger.info("=" * 80)
    _logger.info("MIGRATION START: rental_management v3.4.1")
    _logger.info("Two-Stage Payment Workflow - Backward Compatibility Update")
    _logger.info("=" * 80)
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Step 1: Find all existing contracts
    all_contracts = env['property.vendor'].search([
        ('stage', '!=', False)
    ])
    
    _logger.info(f"Found {len(all_contracts)} total contracts in database")
    
    # Step 2: Focus on non-draft contracts (old data)
    old_contracts = all_contracts.filtered(
        lambda c: c.stage in ['booked', 'sold', 'refund', 'cancel', 'locked']
    )
    
    _logger.info(f"Processing {len(old_contracts)} existing (non-draft) contracts")
    
    migrated_count = 0
    error_count = 0
    
    for contract in old_contracts:
        try:
            _logger.info(f"Processing contract: {contract.sold_seq} (Stage: {contract.stage})")
            
            # Update invoice types based on invoice names
            if contract.sale_invoice_ids:
                # Booking invoices
                booking_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: inv.name and any(
                        keyword in inv.name.lower() 
                        for keyword in ['booking', 'reservation', 'reserve']
                    )
                )
                if booking_inv:
                    booking_inv.write({'invoice_type': 'booking'})
                    _logger.info(f"  → Set {len(booking_inv)} invoices as 'booking'")
                
                # DLD Fee invoices
                dld_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: inv.name and 'dld' in inv.name.lower()
                )
                if dld_inv:
                    dld_inv.write({'invoice_type': 'dld_fee'})
                    _logger.info(f"  → Set {len(dld_inv)} invoices as 'dld_fee'")
                
                # Admin Fee invoices
                admin_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: inv.name and 'admin' in inv.name.lower()
                )
                if admin_inv:
                    admin_inv.write({'invoice_type': 'admin_fee'})
                    _logger.info(f"  → Set {len(admin_inv)} invoices as 'admin_fee'")
                
                # Mark remaining as installments
                other_inv = contract.sale_invoice_ids.filtered(
                    lambda inv: not inv.invoice_type or inv.invoice_type == 'installment'
                )
                if other_inv:
                    other_inv.write({'invoice_type': 'installment'})
                    _logger.info(f"  → Set {len(other_inv)} invoices as 'installment'")
            
            # Force recompute of booking requirements
            # For old contracts, this should set requirements_met=True
            contract._compute_booking_requirements_met()
            
            _logger.info(f"  → Booking Requirements Met: {contract.booking_requirements_met}")
            _logger.info(f"  → Can Create Installments: {contract.can_create_installments}")
            
            migrated_count += 1
            
        except Exception as e:
            error_count += 1
            _logger.error(f"ERROR processing contract {contract.sold_seq}: {str(e)}")
            _logger.exception(e)
            continue
    
    # Step 3: Update module version in database
    _logger.info("Updating module version in database...")
    cr.execute("""
        UPDATE ir_module_module 
        SET latest_version = '3.4.1'
        WHERE name = 'rental_management'
    """)
    
    # Step 4: Summary
    _logger.info("=" * 80)
    _logger.info("MIGRATION COMPLETE: rental_management v3.4.1")
    _logger.info(f"Successfully migrated: {migrated_count}/{len(old_contracts)} contracts")
    _logger.info(f"Errors encountered: {error_count}")
    _logger.info("=" * 80)
    
    if error_count > 0:
        _logger.warning(f"⚠️  {error_count} contracts had errors during migration")
        _logger.warning("   Please review logs and fix manually if needed")
    else:
        _logger.info("✅ All contracts migrated successfully")
