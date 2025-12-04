-- ========================================
-- OSUSPROPERTIES DATABASE CLEANUP SCRIPT
-- Date: November 27, 2025
-- Purpose: Remove residual data from uninstalled modules
-- ========================================

-- BACKUP RECOMMENDATION: Create backup before running
-- pg_dump -U odoo -d osusproperties -F c -f osusproperties_backup_$(date +%Y%m%d).dump

BEGIN;

-- 1. Clean up orphaned ir_model_data records
-- These are external IDs from uninstalled modules
DELETE FROM ir_model_data 
WHERE module NOT IN (
    SELECT name FROM ir_module_module WHERE state = 'installed'
) AND module != 'base';

-- 2. Clean up orphaned ir_attachment records
-- Remove attachments linked to non-existent models
DELETE FROM ir_attachment 
WHERE res_model NOT IN (
    SELECT model FROM ir_model
) AND res_model IS NOT NULL;

-- 3. Clean up orphaned mail_message records
DELETE FROM mail_message 
WHERE model NOT IN (
    SELECT model FROM ir_model
) AND model IS NOT NULL;

-- 4. Clean up orphaned mail_followers
DELETE FROM mail_followers 
WHERE res_model NOT IN (
    SELECT model FROM ir_model
);

-- 5. Clean up orphaned ir_cron jobs from uninstalled modules
DELETE FROM ir_cron 
WHERE id IN (
    SELECT c.id FROM ir_cron c
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.cron' AND imd.res_id = c.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    ) OR imd.module IS NULL
);

-- 6. Clean up orphaned ir_ui_view records
DELETE FROM ir_ui_view 
WHERE id IN (
    SELECT v.id FROM ir_ui_view v
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.ui.view' AND imd.res_id = v.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

-- 7. Clean up orphaned ir_ui_menu records
DELETE FROM ir_ui_menu 
WHERE id IN (
    SELECT m.id FROM ir_ui_menu m
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.ui.menu' AND imd.res_id = m.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

-- 8. Clean up orphaned ir_actions (all types)
DELETE FROM ir_act_window 
WHERE id IN (
    SELECT a.id FROM ir_act_window a
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.actions.act_window' AND imd.res_id = a.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

DELETE FROM ir_act_server 
WHERE id IN (
    SELECT a.id FROM ir_act_server a
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.actions.server' AND imd.res_id = a.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

DELETE FROM ir_act_report_xml 
WHERE id IN (
    SELECT a.id FROM ir_act_report_xml a
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.actions.report' AND imd.res_id = a.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

-- 9. Clean up orphaned ir_model_fields
DELETE FROM ir_model_fields 
WHERE model_id NOT IN (
    SELECT id FROM ir_model
) OR model_id IN (
    SELECT m.id FROM ir_model m
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.model' AND imd.res_id = m.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

-- 10. Clean up orphaned ir_rule records
DELETE FROM ir_rule 
WHERE id IN (
    SELECT r.id FROM ir_rule r
    LEFT JOIN ir_model_data imd ON imd.model = 'ir.rule' AND imd.res_id = r.id
    WHERE imd.module NOT IN (
        SELECT name FROM ir_module_module WHERE state = 'installed'
    )
);

-- 11. Clean up orphaned ir_model_constraint records
DELETE FROM ir_model_constraint 
WHERE module::text NOT IN (
    SELECT name FROM ir_module_module WHERE state = 'installed'
);

-- 12. Clean up orphaned ir_model_relation records
DELETE FROM ir_model_relation 
WHERE module::text NOT IN (
    SELECT name FROM ir_module_module WHERE state = 'installed'
);

-- 13. Clean up orphaned ir_translation records
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_translation') THEN
        DELETE FROM ir_translation 
        WHERE module NOT IN (
            SELECT name FROM ir_module_module WHERE state = 'installed'
        ) AND module IS NOT NULL;
    END IF;
END $$;

-- 14. Clean up orphaned workflow records (if exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wkf') THEN
        DELETE FROM wkf WHERE osv NOT IN (SELECT model FROM ir_model);
    END IF;
END $$;

-- 15. Remove uninstalled module records completely
DELETE FROM ir_module_module_dependency 
WHERE module_id IN (
    SELECT id FROM ir_module_module WHERE state = 'uninstalled'
);

-- Keep the module records for reinstallation purposes
-- DELETE FROM ir_module_module WHERE state = 'uninstalled';

COMMIT;

-- Generate cleanup report
SELECT 
    'Cleanup Complete' as status,
    (SELECT COUNT(*) FROM ir_model_data WHERE module NOT IN (SELECT name FROM ir_module_module WHERE state = 'installed')) as remaining_orphaned_data,
    (SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed') as installed_modules,
    (SELECT COUNT(*) FROM ir_module_module WHERE state = 'uninstalled') as uninstalled_modules,
    (SELECT pg_size_pretty(pg_database_size(current_database()))) as database_size;

-- ========================================
-- POST-CLEANUP VERIFICATION QUERIES
-- ========================================

-- Check remaining orphaned records
-- SELECT module, COUNT(*) as count 
-- FROM ir_model_data 
-- WHERE module NOT IN (SELECT name FROM ir_module_module WHERE state = 'installed')
-- GROUP BY module 
-- ORDER BY count DESC 
-- LIMIT 20;

-- Check database size
-- SELECT pg_size_pretty(pg_database_size('osusproperties'));

-- Check table sizes
-- SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
-- LIMIT 20;
