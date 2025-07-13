# -*- coding: utf-8 -*-
"""
Post-migration script for commission fields refactoring
This script helps migrate data from old commission structure to new simplified structure
"""

import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Migration script for commission fields refactoring"""
    _logger.info("Starting commission fields migration...")
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Check if we're migrating from old structure
        cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='external_commission_type'")
        has_old_structure = bool(cr.fetchone())
        
        if has_old_structure:
            _logger.info("Old commission structure detected. Starting migration...")
            
            # Migrate external commission fields
            migrate_external_commissions(cr, env)
            
            # Migrate internal commission fields
            migrate_internal_commissions(cr, env)
            
            # Clean up old fields (optional - you might want to keep them for a while)
            # cleanup_old_fields(cr)
            
            _logger.info("Commission fields migration completed successfully!")
        else:
            _logger.info("No old commission structure detected. Migration skipped.")

def migrate_external_commissions(cr, env):
    """Migrate external commission data to new structure"""
    _logger.info("Migrating external commission data...")
    
    # Get all sale orders with external commission data
    sale_orders = env['sale.order'].search([
        '|', 
        ('external_percentage', '>', 0),
        ('external_fixed_amount', '>', 0)
    ])
    
    for order in sale_orders:
        try:
            # Migrate old external partner commission to broker/agency
            if order.external_partner_id:
                order.broker_agency_partner_id = order.external_partner_id
                
                if order.external_commission_type == 'fixed':
                    order.broker_agency_amount = order.external_fixed_amount
                else:
                    order.broker_agency_rate = order.external_percentage
            
            # Trigger recalculation
            order._compute_commission_summary()
            
        except Exception as e:
            _logger.error(f"Error migrating external commission for order {order.name}: {str(e)}")

def migrate_internal_commissions(cr, env):
    """Migrate internal commission data to new structure"""
    _logger.info("Migrating internal commission data...")
    
    # Get all sale orders with internal commission data
    sale_orders = env['sale.order'].search([
        '|', '|', '|',
        ('agent1_fixed', '>', 0),
        ('agent2_fixed', '>', 0),
        ('manager_fixed', '>', 0),
        ('director_fixed', '>', 0)
    ])
    
    for order in sale_orders:
        try:
            # Migrate agent1 commission
            if hasattr(order, 'agent1_fixed') and order.agent1_fixed:
                if order.agent1_commission_type == 'fixed':
                    order.agent1_amount = order.agent1_fixed
                else:
                    order.agent1_rate = order.agent1_rate or 0
            
            # Migrate agent2 commission
            if hasattr(order, 'agent2_fixed') and order.agent2_fixed:
                if order.agent2_commission_type == 'fixed':
                    order.agent2_amount = order.agent2_fixed
                else:
                    order.agent2_rate = order.agent2_rate or 0
            
            # Migrate manager commission
            if hasattr(order, 'manager_fixed') and order.manager_fixed:
                if order.manager_commission_type == 'fixed':
                    order.manager_amount = order.manager_fixed
                else:
                    order.manager_rate = order.manager_rate or 0
            
            # Migrate director commission
            if hasattr(order, 'director_fixed') and order.director_fixed:
                if order.director_commission_type == 'fixed':
                    order.director_amount = order.director_fixed
                else:
                    order.director_rate = order.director_rate or 0
            
            # Trigger recalculation
            order._compute_commission_summary()
            
        except Exception as e:
            _logger.error(f"Error migrating internal commission for order {order.name}: {str(e)}")

def cleanup_old_fields(cr):
    """Clean up old commission fields (use with caution)"""
    _logger.info("Cleaning up old commission fields...")
    
    old_fields = [
        'external_commission_type',
        'external_percentage', 
        'external_fixed_amount',
        'external_commission_amount',
        'internal_commission_type',
        'agent1_commission_type',
        'agent1_fixed',
        'agent1_commission',
        'agent2_commission_type', 
        'agent2_fixed',
        'agent2_commission',
        'manager_commission_type',
        'manager_fixed', 
        'manager_commission',
        'director_commission_type',
        'director_fixed',
        'director_commission',
        'show_external_percentage',
        'show_external_fixed_amount',
        'show_agent1_rate',
        'show_agent1_fixed',
        'show_agent2_rate',
        'show_agent2_fixed',
        'show_manager_rate',
        'show_manager_fixed',
        'show_director_rate',
        'show_director_fixed'
    ]
    
    for field in old_fields:
        try:
            cr.execute(f"ALTER TABLE sale_order DROP COLUMN IF EXISTS {field}")
            _logger.info(f"Dropped old field: {field}")
        except Exception as e:
            _logger.warning(f"Could not drop field {field}: {str(e)}")
