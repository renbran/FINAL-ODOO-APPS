-- CloudPepper Autovacuum Emergency Fix
-- Run with: psql -d osustst -f autovacuum_fix.sql

BEGIN;

-- 1. Disable problematic transient models
UPDATE ir_model 
SET transient = FALSE 
WHERE model = 'kit.account.tax.report' 
AND transient = TRUE;

-- 2. Clean up orphaned tax report variants
DELETE FROM account_tax_report_line 
WHERE report_id IN (
    SELECT atr.id 
    FROM account_tax_report atr
    WHERE atr.parent_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM account_tax_report parent 
        WHERE parent.id = atr.parent_id
    )
);

-- 3. Remove duplicate tax reports
WITH report_duplicates AS (
    SELECT id, 
           ROW_NUMBER() OVER (
               PARTITION BY COALESCE(name, ''), COALESCE(country_id, 0) 
               ORDER BY id
           ) as rn
    FROM account_tax_report 
    WHERE parent_id IS NULL
)
DELETE FROM account_tax_report 
WHERE id IN (
    SELECT id FROM report_duplicates WHERE rn > 1
);

-- 4. Adjust autovacuum settings
UPDATE ir_config_parameter 
SET value = '48' 
WHERE key = 'database.transient_age_limit';

-- 5. Disable autovacuum cron temporarily
UPDATE ir_cron 
SET active = FALSE 
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);

COMMIT;

-- Re-enable autovacuum with safer interval
UPDATE ir_cron 
SET active = TRUE,
    interval_number = 2,
    interval_type = 'days'
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);
