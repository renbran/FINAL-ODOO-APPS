-- CloudPepper Emergency Database Fix
-- This script removes problematic references and allows the module to load

-- 1. Remove any existing ir.model.data records for the problematic action
DELETE FROM ir_model_data 
WHERE module = 'account_payment_approval' 
AND name = 'action_report_voucher_verification_web';

-- 2. Clear cache tables
DELETE FROM ir_cache WHERE key LIKE '%action_report_voucher_verification_web%';

-- 3. Remove any problematic ir.actions.report records
DELETE FROM ir_actions_report 
WHERE report_name = 'account_payment_approval.report_qr_verification_document'
AND name = 'Voucher Verification (Web)';

-- 4. Clear module registry cache
DELETE FROM ir_module_module_dependency 
WHERE name = 'account_payment_approval';

-- 5. Reset module state to allow reinstall
UPDATE ir_module_module 
SET state = 'to install' 
WHERE name = 'account_payment_approval' 
AND state = 'installed';

-- Commit changes
COMMIT;
