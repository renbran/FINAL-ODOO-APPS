# -*- coding: utf-8 -*-
"""
Fix Account Tax Report Vacuum Error
===================================
This script fixes the autovacuum error for account.tax.report model
by cleaning up orphaned report variants and fixing report relationships.
"""

import logging
from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def fix_account_tax_report_vacuum(env):
    """
    Fix the account tax report vacuum error by cleaning up orphaned variants
    """
    try:
        # Get all tax reports
        AccountTaxReport = env['account.tax.report']
        all_reports = AccountTaxReport.sudo().search([])
        
        _logger.info(f"Found {len(all_reports)} tax reports to check")
        
        fixed_count = 0
        for report in all_reports:
            try:
                # Check if this report has variants
                if hasattr(report, 'variant_report_ids'):
                    variant_count = len(report.variant_report_ids)
                    if variant_count > 0:
                        _logger.info(f"Report {report.id} has {variant_count} variants")
                        
                        # Try to clean up orphaned variants
                        for variant in report.variant_report_ids:
                            try:
                                # Check if variant is actually needed
                                if not variant.active or not variant.country_id:
                                    _logger.info(f"Removing orphaned variant {variant.id}")
                                    variant.sudo().unlink()
                                    fixed_count += 1
                            except Exception as ve:
                                _logger.warning(f"Could not remove variant {variant.id}: {ve}")
                                
                # If report still has no variants, it should be safe to delete
                if hasattr(report, 'variant_report_ids') and not report.variant_report_ids:
                    # Check if this is an old/orphaned report
                    if not report.active:
                        try:
                            _logger.info(f"Removing inactive report {report.id}")
                            report.sudo().unlink()
                            fixed_count += 1
                        except Exception as re:
                            _logger.warning(f"Could not remove report {report.id}: {re}")
                            
            except Exception as e:
                _logger.warning(f"Error processing report {report.id}: {e}")
                
        _logger.info(f"Fixed {fixed_count} report/variant issues")
        
        # Force garbage collection
        env.cr.commit()
        
        return fixed_count
        
    except Exception as e:
        _logger.error(f"Error fixing account tax report vacuum: {e}")
        return 0


def disable_problematic_autovacuum(env):
    """
    Temporarily disable autovacuum for problematic models
    """
    try:
        # Find the autovacuum cron job
        cron = env['ir.cron'].sudo().search([
            ('model_id.model', '=', 'ir.autovacuum'),
            ('function', '=', '_run_vacuum_cleaner')
        ], limit=1)
        
        if cron:
            _logger.info(f"Temporarily disabling autovacuum cron {cron.id}")
            cron.active = False
            env.cr.commit()
            return True
            
    except Exception as e:
        _logger.error(f"Error disabling autovacuum: {e}")
        
    return False


def re_enable_autovacuum(env):
    """
    Re-enable autovacuum after fixes
    """
    try:
        # Find the autovacuum cron job
        cron = env['ir.cron'].sudo().search([
            ('model_id.model', '=', 'ir.autovacuum'),
            ('function', '=', '_run_vacuum_cleaner')
        ], limit=1)
        
        if cron and not cron.active:
            _logger.info(f"Re-enabling autovacuum cron {cron.id}")
            cron.active = True
            env.cr.commit()
            return True
            
    except Exception as e:
        _logger.error(f"Error re-enabling autovacuum: {e}")
        
    return False


class AccountTaxReportFix(models.TransientModel):
    """
    Transient model to fix account tax report vacuum issues
    """
    _name = 'account.tax.report.fix'
    _description = 'Fix Account Tax Report Vacuum Issues'
    
    @api.model
    def fix_vacuum_issues(self):
        """
        Main method to fix vacuum issues
        """
        _logger.info("Starting account tax report vacuum fix")
        
        # Step 1: Disable autovacuum temporarily
        disable_problematic_autovacuum(self.env)
        
        # Step 2: Fix report variants
        fixed_count = fix_account_tax_report_vacuum(self.env)
        
        # Step 3: Re-enable autovacuum
        re_enable_autovacuum(self.env)
        
        _logger.info(f"Account tax report vacuum fix completed. Fixed {fixed_count} issues.")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Account tax report vacuum fix completed. Fixed {fixed_count} issues.',
                'type': 'success',
                'sticky': False,
            }
        }


# Direct execution function for manual use
def manual_fix_tax_report_vacuum():
    """
    Function to be called manually from Odoo shell or external script
    """
    import odoo
    from odoo import registry
    
    # This would be called from Odoo shell with proper env
    # Example: manual_fix_tax_report_vacuum()
    print("This function should be called from within Odoo environment")
    print("Use: env['account.tax.report.fix'].fix_vacuum_issues()")
