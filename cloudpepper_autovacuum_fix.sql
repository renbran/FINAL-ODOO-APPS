-- CloudPepper Autovacuum Fix
-- Addresses: kit.account.tax.report variant deletion issues

-- 1. Disable autovacuum for problematic models temporarily
UPDATE ir_model 
SET transient = False 
WHERE model IN ('kit.account.tax.report', 'account.tax.report')
AND transient = True;

-- 2. Clean up orphaned tax report variants
DELETE FROM account_tax_report_line 
WHERE report_id IN (
    SELECT id FROM account_tax_report 
    WHERE id NOT IN (
        SELECT DISTINCT parent_id 
        FROM account_tax_report 
        WHERE parent_id IS NOT NULL
    )
    AND parent_id IS NOT NULL
);

-- 3. Remove duplicate tax reports that might be causing conflicts
WITH duplicates AS (
    SELECT id, 
           ROW_NUMBER() OVER (PARTITION BY name, country_id ORDER BY id) as rn
    FROM account_tax_report 
    WHERE parent_id IS NULL
)
DELETE FROM account_tax_report 
WHERE id IN (
    SELECT id FROM duplicates WHERE rn > 1
);

-- 4. Reset autovacuum settings
UPDATE ir_config_parameter 
SET value = '24' 
WHERE key = 'database.transient_age_limit';

-- 5. Re-enable autovacuum with safer settings
UPDATE ir_cron 
SET active = True,
    interval_number = 1,
    interval_type = 'days'
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);

COMMIT;
