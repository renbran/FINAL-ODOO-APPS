-- QUICK ONE-LINER FIX for constraint violation
-- Copy and paste this single command into your PostgreSQL console:

DELETE FROM ir_model_data WHERE module = 'base' AND name = 'module_payment_account_enhanced';

-- That's it! This removes the specific record causing the constraint violation.
-- After running this, restart Odoo and try installing the module again.
