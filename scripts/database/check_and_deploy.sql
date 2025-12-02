-- ============================================================================
-- RENTAL MANAGEMENT v3.4.0 DEPLOYMENT VERIFICATION SCRIPT
-- ============================================================================
-- Purpose: Check current module status and prepare for update
-- Database: scholarixv2
-- ============================================================================

-- [1] CHECK CURRENT MODULE STATUS
-- ============================================================================
SELECT 
    CONCAT(
        '=== CURRENT MODULE STATUS ===',
        CHR(10),
        'Module Name: ', name,
        CHR(10),
        'State: ', state,
        CHR(10),
        'Installed Version: ', COALESCE(installed_version, 'Not Installed'),
        CHR(10),
        'Latest Version: ', latest_version
    ) AS status_report
FROM ir_module_module
WHERE name = 'rental_management';

-- [2] CHECK IF MODULE IS ALREADY INSTALLED
-- ============================================================================
SELECT 
    CASE 
        WHEN state = 'installed' THEN '✅ Module is INSTALLED'
        WHEN state = 'uninstalled' THEN '⚠️  Module is UNINSTALLED (will be installed)'
        WHEN state = 'to install' THEN '⏳ Module is marked for installation'
        WHEN state = 'to upgrade' THEN '⏳ Module is marked for upgrade'
        ELSE '❓ Unknown state: ' || state
    END AS deployment_status,
    installed_version AS current_version,
    latest_version AS target_version,
    CASE 
        WHEN installed_version IS NULL THEN 'FRESH_INSTALL'
        WHEN installed_version < latest_version THEN 'UPGRADE_NEEDED'
        WHEN installed_version = latest_version THEN 'UP_TO_DATE'
        ELSE 'UNKNOWN'
    END AS action_type
FROM ir_module_module
WHERE name = 'rental_management';

-- [3] CHECK RELATED MODULES STATUS
-- ============================================================================
SELECT 
    name,
    state,
    installed_version,
    latest_version
FROM ir_module_module
WHERE name IN (
    'sale', 
    'account', 
    'crm', 
    'mail', 
    'web',
    'base',
    'stock',
    'purchase'
)
ORDER BY name;

-- [4] VERIFY DATABASE INTEGRITY
-- ============================================================================
-- Check if rental_management tables exist
SELECT 
    schemaname,
    tablename,
    CONCAT(
        'Table: ', tablename,
        CHR(10),
        'Schema: ', schemaname
    ) AS table_info
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'property_vendor',
    'sale_invoice',
    'payment_schedule'
)
ORDER BY tablename;

-- [5] COUNT RECORDS IN KEY TABLES
-- ============================================================================
SELECT 
    'property_vendor' AS table_name,
    COUNT(*) AS record_count,
    MAX(create_date) AS last_created
FROM property_vendor
UNION ALL
SELECT 
    'sale_invoice',
    COUNT(*),
    MAX(create_date)
FROM sale_invoice
UNION ALL
SELECT 
    'payment_schedule',
    COUNT(*),
    MAX(create_date)
FROM payment_schedule;

-- [6] CHECK FOR ANY DATA ISSUES
-- ============================================================================
-- Orphaned payment_responsible_id references (this was previously fixed)
SELECT 
    COUNT(*) AS orphaned_payment_refs
FROM sale_invoice si
LEFT JOIN res_partner rp ON si.payment_responsible_id = rp.id
WHERE si.payment_responsible_id IS NOT NULL
AND rp.id IS NULL;

-- [7] MODULE DEPENDENCIES VERIFICATION
-- ============================================================================
SELECT 
    m.name AS module_name,
    m.state,
    CASE 
        WHEN dep.name IS NULL THEN '✅ All dependencies satisfied'
        ELSE '❌ Depends on: ' || dep.name
    END AS dependency_status
FROM ir_module_module m
LEFT JOIN ir_module_module_dependency dep_rel 
    ON m.id = dep_rel.module_id
LEFT JOIN ir_module_module dep 
    ON dep_rel.depends_id = dep.id 
    AND dep.state != 'installed'
WHERE m.name = 'rental_management'
LIMIT 1;

-- [8] DEPLOYMENT DECISION
-- ============================================================================
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM ir_module_module 
            WHERE name = 'rental_management' 
            AND state = 'installed'
            AND installed_version = '3.4.0'
        ) THEN 'NO_ACTION_NEEDED: Module already at v3.4.0'
        WHEN EXISTS (
            SELECT 1 FROM ir_module_module 
            WHERE name = 'rental_management' 
            AND state = 'installed'
            AND installed_version < '3.4.0'
        ) THEN 'UPGRADE_NEEDED: Current version < 3.4.0'
        WHEN EXISTS (
            SELECT 1 FROM ir_module_module 
            WHERE name = 'rental_management' 
            AND state IN ('uninstalled', 'to install')
        ) THEN 'INSTALL_NEEDED: Module not installed'
        ELSE 'UNKNOWN: Unable to determine status'
    END AS deployment_decision
FROM (SELECT 1) AS dummy;

-- [9] BACKUP VERIFICATION
-- ============================================================================
-- Get database size for backup estimation
SELECT 
    pg_size_pretty(pg_database_size('scholarixv2')) AS database_size,
    CASE 
        WHEN pg_database_size('scholarixv2') > 1073741824 THEN 'Large (>1GB) - Estimate 2+ min backup time'
        WHEN pg_database_size('scholarixv2') > 536870912 THEN 'Medium (500MB-1GB) - Estimate 1-2 min backup time'
        ELSE 'Small (<500MB) - Estimate <1 min backup time'
    END AS backup_info;

-- [10] SAFE TO PROCEED CHECK
-- ============================================================================
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ SAFE TO PROCEED: All checks passed'
        ELSE '❌ ISSUES DETECTED: Review above results'
    END AS final_status
FROM (
    -- Check 1: Key dependencies installed
    SELECT 1 FROM ir_module_module WHERE name = 'sale' AND state = 'installed'
    INTERSECT
    SELECT 1 FROM ir_module_module WHERE name = 'account' AND state = 'installed'
    INTERSECT
    SELECT 1 FROM ir_module_module WHERE name = 'web' AND state = 'installed'
    INTERSECT
    -- Check 2: No orphaned foreign keys
    SELECT 1 FROM (
        SELECT COUNT(*) as orphaned
        FROM sale_invoice si
        LEFT JOIN res_partner rp ON si.payment_responsible_id = rp.id
        WHERE si.payment_responsible_id IS NOT NULL AND rp.id IS NULL
    ) AS check2
    WHERE orphaned = 0
) AS all_checks;

-- ============================================================================
-- POST-DEPLOYMENT VERIFICATION QUERIES (Run after update)
-- ============================================================================

-- [POST-1] VERIFY NEW FIELDS WERE ADDED
-- ============================================================================
-- SELECT COLUMN_NAME 
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'property_vendor'
-- AND COLUMN_NAME IN (
--     'payment_bank_name',
--     'payment_account_name',
--     'payment_account_number',
--     'payment_iban',
--     'payment_swift',
--     'payment_currency',
--     'dld_bank_name',
--     'dld_account_name',
--     'dld_account_number',
--     'dld_iban',
--     'dld_swift',
--     'dld_currency',
--     'admin_bank_name',
--     'admin_account_name',
--     'admin_account_number',
--     'admin_iban',
--     'admin_swift',
--     'admin_currency'
-- );

-- [POST-2] VERIFY MODULE VERSION UPDATED
-- ============================================================================
-- SELECT installed_version 
-- FROM ir_module_module 
-- WHERE name = 'rental_management' 
-- AND installed_version = '3.4.0';

-- [POST-3] TEST SPA REPORT GENERATION
-- ============================================================================
-- SELECT 
--     pv.id,
--     pv.name,
--     pv.payment_bank_name,
--     pv.dld_bank_name,
--     pv.admin_bank_name
-- FROM property_vendor pv
-- LIMIT 5;

-- ============================================================================
-- ROLLBACK CHECKLIST (If needed)
-- ============================================================================
-- 1. Stop Odoo service: systemctl stop odoo
-- 2. Restore database: gunzip -c backup.sql.gz | psql -d scholarixv2
-- 3. Restore module files: tar -xzf backup.tar.gz
-- 4. Start Odoo service: systemctl start odoo
-- 5. Verify: Check module status and logs
-- ============================================================================
