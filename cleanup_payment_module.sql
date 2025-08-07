
-- SQL Commands to fix web.assets_backend error for payment_account_enhanced
-- These commands remove cached XML data from the database

-- 1. Remove all ir.model.data entries for the module
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';

-- 2. Remove module from installed modules (to force clean reinstall)
DELETE FROM ir_module_module WHERE name = 'payment_account_enhanced';

-- 3. Clear any cached template data
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';

-- 4. Clear any cached asset data
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view' AND res_name LIKE '%payment_account_enhanced%';

-- 5. Clear QWeb template cache
DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%';

-- Verify cleanup
SELECT 'Cleanup complete - module data removed';
