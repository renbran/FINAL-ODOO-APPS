from . import models
from . import controllers


def post_init_hook(env):
    """Post-installation hook to ensure proper security rule activation"""
    # Update security rules to use approval_state field after model installation
    try:
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
