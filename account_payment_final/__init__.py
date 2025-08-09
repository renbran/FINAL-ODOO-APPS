from . import models
from . import controllers


def post_init_hook(env):
    """Post-installation hook to ensure proper security rule and view activation"""
    try:
        # Activate advanced views after successful installation
        advanced_views = [
            'account_payment_final.view_account_payment_form_advanced',
            'account_payment_final.view_account_payment_tree_advanced',
        ]
        
        for view_ref in advanced_views:
            try:
                view = env.ref(view_ref, raise_if_not_found=False)
                if view:
                    view.active = True
                    view.invalidate_recordset()
            except Exception:
                pass  # Ignore if view doesn't exist yet
        
        # Force update of security rules with proper field references
        payment_rules = [
            'account_payment_final.payment_voucher_user_own_rule',
            'account_payment_final.payment_voucher_reviewer_rule', 
            'account_payment_final.payment_voucher_approver_rule',
            'account_payment_final.payment_voucher_authorizer_rule',
            'account_payment_final.payment_voucher_poster_rule',
        ]
        
        for rule_ref in payment_rules:
            try:
                rule = env.ref(rule_ref, raise_if_not_found=False)
                if rule:
                    rule.invalidate_recordset()
            except Exception:
                pass  # Ignore if rule doesn't exist yet
                
    except Exception as e:
        # Log but don't fail installation
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info(f"Post-init hook completed with info: {e}")


def uninstall_hook(env):
    """Cleanup hook for module uninstallation"""
    pass
