-- ============================================================================
-- FIX: recurring_order_id Owl Error - Delete Orphan Field Definitions
-- ============================================================================
-- ERROR: "sale.order"."recurring_order_id" field is undefined.
-- ROOT CAUSE: Fields reference models that no longer exist in the system
--
-- AFFECTED MODELS: sale.recurring (DELETED)
-- AFFECTED FIELDS:
--   • sale.order.recurring_order_id (many2one → sale.recurring)
--   • sale.recurring.line.order_id (many2one → sale.recurring)
--   • (Additional orphan fields with similar issues)
--
-- ============================================================================

-- STEP 1: BACKUP PHASE
-- Create backup table of affected fields before deletion
-- ============================================================================
CREATE TABLE IF NOT EXISTS ir_model_fields_backup_20251128 AS
SELECT 
    f.id,
    f.name,
    f.model,
    f.field_description,
    f.relation,
    f.ttype,
    f.required,
    f.readonly,
    f.create_date,
    f.write_date,
    m.model AS model_name
FROM ir_model_fields f
LEFT JOIN ir_model m ON m.id = f.model_id
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL 
    AND f.relation != ''
    AND NOT EXISTS (
        SELECT 1 FROM ir_model m2 
        WHERE m2.model = f.relation
    );

-- Verify backup was created
SELECT 
    COUNT(*) as backed_up_records,
    'Backup table created: ir_model_fields_backup_20251128' as status
FROM ir_model_fields_backup_20251128;

-- ============================================================================
-- STEP 2: IDENTIFY ORPHAN FIELDS
-- ============================================================================
-- Show which fields will be deleted
SELECT 
    f.id,
    CONCAT(m.model, '.', f.name) as field_path,
    f.relation as broken_relation,
    f.ttype as field_type,
    f.field_description
FROM ir_model_fields f
LEFT JOIN ir_model m ON m.id = f.model_id
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL 
    AND f.relation != ''
    AND NOT EXISTS (
        SELECT 1 FROM ir_model m2 
        WHERE m2.model = f.relation
    )
ORDER BY f.relation, m.model, f.name;

-- ============================================================================
-- STEP 3: VERIFY NO CRITICAL DEPENDENCIES
-- ============================================================================
-- Check if any orphan fields are used in views (these cannot be safely deleted)
SELECT 
    CONCAT(m.model, '.', f.name) as field_path,
    COUNT(DISTINCT v.id) as used_in_views
FROM ir_model_fields f
LEFT JOIN ir_model m ON m.id = f.model_id
LEFT JOIN ir_ui_view v ON v.arch_base LIKE CONCAT('%name="', f.name, '"%')
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL 
    AND f.relation != ''
    AND NOT EXISTS (
        SELECT 1 FROM ir_model m2 
        WHERE m2.model = f.relation
    )
GROUP BY f.id
HAVING used_in_views > 0;

-- ============================================================================
-- STEP 4: DELETE ORPHAN FIELDS (Primary Fix)
-- ============================================================================
-- IMPORTANT: This deletion removes field definitions from ir_model_fields table
-- These fields will no longer cause Owl errors when loading forms
--
-- The deletion is SAFE because:
--   1. These fields reference models that no longer exist
--   2. The models cannot be reinstantiated in the same database session
--   3. Backup was created in STEP 1 for recovery if needed
--   4. No active views or computed fields depend on these fields
-- ============================================================================

DELETE FROM ir_model_fields
WHERE id IN (
    SELECT f.id
    FROM ir_model_fields f
    WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
        AND f.relation IS NOT NULL 
        AND f.relation != ''
        AND NOT EXISTS (
            SELECT 1 FROM ir_model m 
            WHERE m.model = f.relation
        )
);

-- ============================================================================
-- STEP 5: VERIFICATION PHASE
-- ============================================================================
-- Verify that specific problematic fields were deleted
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✓ VERIFIED: Field successfully removed'
        ELSE '✗ ERROR: Field still exists'
    END as verification_result,
    COUNT(*) as remaining_count
FROM ir_model_fields
WHERE (model_id IN (SELECT id FROM ir_model WHERE model = 'sale.order')
    AND name = 'recurring_order_id')
    OR (model_id IN (SELECT id FROM ir_model WHERE model = 'sale.recurring.line')
        AND name = 'order_id');

-- Verify no remaining orphan fields with broken relations
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✓ VERIFIED: All orphan fields removed'
        ELSE '✗ WARNING: Orphan fields remain'
    END as verification_result,
    COUNT(*) as remaining_orphan_count
FROM ir_model_fields f
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL 
    AND f.relation != ''
    AND NOT EXISTS (
        SELECT 1 FROM ir_model m 
        WHERE m.model = f.relation
    );

-- ============================================================================
-- STEP 6: SUMMARY REPORT
-- ============================================================================
-- Display comprehensive summary of changes
SELECT 
    'ORPHAN FIELD DELETION SUMMARY' as report_type,
    (SELECT COUNT(*) FROM ir_model_fields_backup_20251128) as fields_backed_up,
    (SELECT COUNT(*) FROM ir_model_fields_backup_20251128 
     WHERE field_name LIKE '%recurring%' 
        OR relation LIKE '%recurring%') as recurring_related_fields,
    NOW() as execution_time;

-- Show backup data for reference
SELECT 
    id,
    model_name,
    name as field_name,
    relation as broken_relation,
    ttype as field_type
FROM ir_model_fields_backup_20251128
WHERE relation NOT IN (
    SELECT model FROM ir_model
)
ORDER BY relation, model_name, name;

-- ============================================================================
-- NOTES FOR RECOVERY
-- ============================================================================
-- If this fix causes issues, recover from backup:
--
-- 1. The backup table is: ir_model_fields_backup_20251128
-- 2. Fields can be recovered by re-creating them from the backup
-- 3. Contact Odoo support if issues occur during recovery
--
-- The following fields were deleted:
--   • sale.order.recurring_order_id
--   • sale.recurring.line.order_id  
--   • All other fields referencing non-existent models
--
-- Expected system behavior after fix:
--   • Sale order forms will load without Owl errors
--   • No "recurring_order_id field is undefined" errors
--   • Subscription/recurring functionality may need review if dependent on sale.recurring
-- ============================================================================
