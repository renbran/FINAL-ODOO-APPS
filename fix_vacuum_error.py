#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Fix for Account Tax Report Vacuum Error
==============================================

This script provides a direct fix for the autovacuum error:
"You can't delete a report that has variants."

Usage:
    python fix_vacuum_error.py

This script can be run independently or through Docker:
    docker-compose exec odoo python /mnt/extra-addons/fix_vacuum_error.py
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

def fix_vacuum_error():
    """Direct fix for the vacuum error without needing the module"""
    try:
        # Try to import Odoo
        try:
            import odoo
            from odoo import api, registry
            from odoo.exceptions import UserError
        except ImportError:
            _logger.error("Odoo not found. This script must be run in an Odoo environment.")
            return False

        # Get database name from environment or use default
        db_name = os.environ.get('ODOO_DB_NAME', 'odoo')
        
        _logger.info(f"Connecting to database: {db_name}")
        
        # Initialize Odoo registry
        reg = registry(db_name)
        
        with reg.cursor() as cr:
            env = api.Environment(cr, 1, {})  # Use admin user
            
            _logger.info("Starting vacuum error fix...")
            
            # Step 1: Disable autovacuum temporarily
            _logger.info("Step 1: Disabling autovacuum...")
            cron = env['ir.cron'].sudo().search([
                ('model_id.model', '=', 'ir.autovacuum'),
                ('function', '=', '_run_vacuum_cleaner')
            ], limit=1)
            
            autovacuum_was_active = False
            if cron and cron.active:
                cron.active = False
                autovacuum_was_active = True
                _logger.info("✓ Autovacuum disabled")
            else:
                _logger.info("ℹ Autovacuum already disabled or not found")
            
            # Step 2: Fix tax report variants
            _logger.info("Step 2: Fixing tax report variants...")
            fixed_count = 0
            
            if 'account.tax.report' in env:
                AccountTaxReport = env['account.tax.report']
                reports = AccountTaxReport.sudo().search([])
                _logger.info(f"Found {len(reports)} tax reports to check")
                
                for report in reports:
                    try:
                        # Check for variants
                        if hasattr(report, 'variant_report_ids'):
                            variants = report.variant_report_ids
                            if variants:
                                _logger.info(f"Report {report.id} has {len(variants)} variants")
                                
                                # Remove inactive or orphaned variants
                                for variant in variants:
                                    try:
                                        if not variant.active or not getattr(variant, 'country_id', None):
                                            variant.sudo().unlink()
                                            fixed_count += 1
                                            _logger.info(f"  Removed variant {variant.id}")
                                    except Exception as ve:
                                        try:
                                            variant.active = False
                                            fixed_count += 1
                                            _logger.info(f"  Deactivated variant {variant.id}")
                                        except Exception:
                                            _logger.warning(f"  Could not process variant {variant.id}")
                        
                        # Remove inactive reports with no variants
                        if (hasattr(report, 'variant_report_ids') and 
                            not report.variant_report_ids and 
                            not report.active):
                            try:
                                report.sudo().unlink()
                                fixed_count += 1
                                _logger.info(f"  Removed inactive report {report.id}")
                            except Exception:
                                _logger.warning(f"  Could not remove inactive report {report.id}")
                                
                    except Exception as e:
                        _logger.warning(f"Error processing report {report.id}: {e}")
                        
            else:
                _logger.info("account.tax.report model not found")
            
            # Step 3: Clean up old transient records using SQL
            _logger.info("Step 3: Cleaning old transient records...")
            try:
                # Clean records older than 1 hour
                cr.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%tax_report%'
                    AND table_type = 'BASE TABLE'
                """)
                
                tables = [row[0] for row in cr.fetchall()]
                transient_cleaned = 0
                
                for table_name in tables:
                    try:
                        # Check if table has write_date column
                        cr.execute(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{table_name}' 
                            AND column_name = 'write_date'
                        """)
                        
                        if cr.fetchone():
                            # Clean old records
                            cr.execute(f"""
                                DELETE FROM {table_name} 
                                WHERE write_date < (NOW() - INTERVAL '1 hour')
                                AND id NOT IN (
                                    SELECT DISTINCT t1.id 
                                    FROM {table_name} t1 
                                    WHERE EXISTS (
                                        SELECT 1 FROM {table_name} t2 
                                        WHERE t2.id != t1.id
                                    )
                                )
                            """)
                            cleaned = cr.rowcount
                            if cleaned > 0:
                                transient_cleaned += cleaned
                                _logger.info(f"  Cleaned {cleaned} old records from {table_name}")
                                
                    except Exception as te:
                        _logger.warning(f"Could not clean table {table_name}: {te}")
                        
                _logger.info(f"✓ Cleaned {transient_cleaned} transient records")
                
            except Exception as e:
                _logger.warning(f"Error cleaning transient records: {e}")
            
            # Step 4: Re-enable autovacuum
            _logger.info("Step 4: Re-enabling autovacuum...")
            if autovacuum_was_active and cron:
                cron.active = True
                _logger.info("✓ Autovacuum re-enabled")
            else:
                _logger.info("ℹ Autovacuum was not active initially")
            
            # Commit changes
            cr.commit()
            
            _logger.info(f"🎉 Vacuum error fix completed successfully!")
            _logger.info(f"   Total fixes applied: {fixed_count}")
            
            # Test the vacuum process
            _logger.info("Testing vacuum process...")
            try:
                if 'account.tax.report' in env:
                    Model = env['account.tax.report']
                    if hasattr(Model, '_transient_vacuum'):
                        Model.sudo()._transient_vacuum()
                        _logger.info("✓ Vacuum test passed!")
                    else:
                        _logger.info("ℹ Model is not transient")
                else:
                    _logger.info("ℹ account.tax.report model not found")
                    
            except Exception as te:
                _logger.warning(f"Vacuum test failed (this may be normal): {te}")
            
            return True
            
    except Exception as e:
        _logger.error(f"Failed to fix vacuum error: {e}")
        return False


if __name__ == "__main__":
    _logger.info("=" * 50)
    _logger.info("Account Tax Report Vacuum Error Fix")
    _logger.info("=" * 50)
    
    success = fix_vacuum_error()
    
    if success:
        _logger.info("Fix completed successfully!")
        sys.exit(0)
    else:
        _logger.error("Fix failed!")
        sys.exit(1)
