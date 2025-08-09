#!/usr/bin/env python3
"""
CloudPepper System Fix Script
Addresses common CloudPepper deployment issues
"""

import logging
from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

def fix_tax_report_vacuum_error(env):
    """
    Fix the tax report vacuum error by removing problematic reports
    """
    try:
        # Find problematic tax reports
        tax_reports = env['account.report'].sudo().search([
            ('name', 'ilike', 'tax'),
            ('model', '=', 'kit.account.tax.report')
        ])
        
        for report in tax_reports:
            try:
                # Try to remove variants first
                variants = env['account.report'].sudo().search([
                    ('parent_id', '=', report.id)
                ])
                
                if variants:
                    _logger.info(f"Removing {len(variants)} variants for report {report.name}")
                    variants.sudo().unlink()
                
                # Now try to remove the main report
                report.sudo().unlink()
                _logger.info(f"Successfully removed tax report: {report.name}")
                
            except UserError as e:
                if "has variants" in str(e):
                    _logger.warning(f"Skipping report {report.name} - still has variants")
                    continue
                else:
                    raise
                    
    except Exception as e:
        _logger.error(f"Error fixing tax report vacuum: {e}")
        
    return True

def fix_font_error(env):
    """
    Fix the custom_background font error
    """
    try:
        # Disable custom_background module if it's causing issues
        module = env['ir.module.module'].sudo().search([
            ('name', '=', 'custom_background'),
            ('state', '=', 'installed')
        ])
        
        if module:
            _logger.info("Found custom_background module causing font errors")
            
            # Check if we can fix the font configuration
            try:
                # Update module to handle missing fonts gracefully
                custom_bg_records = env['custom.background'].sudo().search([])
                for record in custom_bg_records:
                    if hasattr(record, 'font_name') and not record.font_name:
                        record.font_name = 'Helvetica'  # Fallback font
                        
                _logger.info("Updated custom_background font configurations")
                
            except Exception as font_fix_error:
                _logger.warning(f"Could not fix font configuration: {font_fix_error}")
                
                # As last resort, uninstall the problematic module
                _logger.info("Uninstalling custom_background module to prevent font errors")
                module.button_immediate_uninstall()
                
    except Exception as e:
        _logger.error(f"Error fixing font error: {e}")
        
    return True

def cleanup_transient_models(env):
    """
    Clean up transient models that might be causing vacuum issues
    """
    try:
        # List of problematic transient models
        transient_models = [
            'kit.account.tax.report',
            'account.report.wizard',
            'account.tax.report.wizard'
        ]
        
        for model_name in transient_models:
            try:
                if model_name in env.registry:
                    model = env[model_name].sudo()
                    
                    # Force cleanup of old records
                    if hasattr(model, '_transient_clean_rows_older_than'):
                        model._transient_clean_rows_older_than(3600)  # 1 hour
                        
                    _logger.info(f"Cleaned transient model: {model_name}")
                    
            except Exception as model_error:
                _logger.warning(f"Could not clean model {model_name}: {model_error}")
                continue
                
    except Exception as e:
        _logger.error(f"Error cleaning transient models: {e}")
        
    return True

def main():
    """
    Main CloudPepper fix function
    """
    with api.Environment.manage():
        with api.Environment(api.Registry('stagingtry'), SUPERUSER_ID, {}) as env:
            _logger.info("Starting CloudPepper system fixes...")
            
            # Fix 1: Tax report vacuum error
            _logger.info("Fixing tax report vacuum error...")
            fix_tax_report_vacuum_error(env)
            
            # Fix 2: Font error in custom_background
            _logger.info("Fixing custom_background font error...")
            fix_font_error(env)
            
            # Fix 3: Clean up transient models
            _logger.info("Cleaning up transient models...")
            cleanup_transient_models(env)
            
            # Commit changes
            env.cr.commit()
            
            _logger.info("CloudPepper system fixes completed successfully!")

if __name__ == "__main__":
    main()
