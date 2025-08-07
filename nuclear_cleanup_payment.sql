
-- NUCLEAR CLEANUP for payment_account_enhanced module
-- This will completely remove ALL traces of the module from database

-- 1. Disable foreign key checks temporarily (if supported)
SET session_replication_role = replica;

-- 2. Remove from module registry
DELETE FROM ir_module_module WHERE name = 'payment_account_enhanced';

-- 3. Remove ALL model data for this module
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';

-- 4. Remove ALL views created by this module
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';
DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%';

-- 5. Remove ALL templates/QWeb data
DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%';

-- 6. Remove menu items
DELETE FROM ir_ui_menu WHERE action LIKE '%payment_account_enhanced%';

-- 7. Remove translations
DELETE FROM ir_translation WHERE src LIKE '%payment_account_enhanced%';
DELETE FROM ir_translation WHERE name LIKE '%payment_account_enhanced%';

-- 8. Remove server actions
DELETE FROM ir_actions_server WHERE name LIKE '%payment_account_enhanced%';

-- 9. Remove report actions
DELETE FROM ir_actions_report WHERE report_name LIKE '%payment_account_enhanced%';

-- 10. Remove access rules
DELETE FROM ir_model_access WHERE name LIKE '%payment_account_enhanced%';

-- 11. Remove record rules
DELETE FROM ir_rule WHERE name LIKE '%payment_account_enhanced%';

-- 12. Remove sequences
DELETE FROM ir_sequence WHERE code LIKE '%payment_account_enhanced%';

-- 13. Remove cron jobs
DELETE FROM ir_cron WHERE name LIKE '%payment_account_enhanced%';

-- 14. Remove attachments
DELETE FROM ir_attachment WHERE res_model LIKE '%payment_account_enhanced%';

-- 15. Clear asset cache completely
DELETE FROM ir_attachment WHERE name LIKE '%.assets_%';
DELETE FROM ir_attachment WHERE name LIKE 'web.assets_%';

-- 16. Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- 17. Vacuum to clean up
VACUUM ANALYZE;

-- Verification
SELECT 'NUCLEAR CLEANUP COMPLETE - All traces removed' as status;
SELECT COUNT(*) as remaining_traces FROM ir_model_data WHERE module = 'payment_account_enhanced';
