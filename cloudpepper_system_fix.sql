-- CloudPepper System Fix SQL Script
-- Run this on your CloudPepper database to fix system errors

-- Fix 1: Remove problematic tax report variants that cause vacuum errors
BEGIN;

-- First, find and remove tax report variants
DELETE FROM account_report 
WHERE parent_id IN (
    SELECT id FROM account_report 
    WHERE name ILIKE '%tax%' AND model = 'kit.account.tax.report'
);

-- Then remove the main tax reports
DELETE FROM account_report 
WHERE name ILIKE '%tax%' AND model = 'kit.account.tax.report';

-- Clean up orphaned report data
DELETE FROM ir_model_data 
WHERE model = 'kit.account.tax.report' 
AND res_id NOT IN (SELECT id FROM account_report);

COMMIT;

-- Fix 2: Disable custom_background module causing font errors
BEGIN;

-- Mark custom_background module as uninstalled to prevent font errors
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE name = 'custom_background' AND state = 'installed';

-- Remove custom_background model data that might cause issues
DELETE FROM ir_model_data 
WHERE module = 'custom_background';

-- Clean up custom_background related views
DELETE FROM ir_ui_view 
WHERE name ILIKE '%custom_background%';

COMMIT;

-- Fix 3: Clean up transient model data
BEGIN;

-- Clean up old transient records (older than 1 hour)
DELETE FROM kit_account_tax_report 
WHERE create_date < NOW() - INTERVAL '1 hour';

-- Clean up account report wizard data
DELETE FROM account_report_wizard 
WHERE create_date < NOW() - INTERVAL '1 hour';

-- Clean up any other transient wizard data
DELETE FROM account_tax_report_wizard 
WHERE create_date < NOW() - INTERVAL '1 hour';

COMMIT;

-- Fix 4: Reset autovacuum configuration to prevent future errors
BEGIN;

-- Update ir_cron job for autovacuum to be less aggressive
UPDATE ir_cron 
SET interval_number = 24, 
    interval_type = 'hours',
    active = true
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);

-- Ensure vacuum doesn't run on problematic models
INSERT INTO ir_config_parameter (key, value, create_date, create_uid, write_date, write_uid)
VALUES 
    ('base.autovacuum.kit_account_tax_report', 'False', NOW(), 1, NOW(), 1),
    ('base.autovacuum.custom_background', 'False', NOW(), 1, NOW(), 1)
ON CONFLICT (key) DO UPDATE SET value = 'False';

COMMIT;

-- Verification queries
SELECT 'Tax Reports Check' as fix_status, count(*) as remaining_count 
FROM account_report WHERE name ILIKE '%tax%';

SELECT 'Custom Background Module' as fix_status, state 
FROM ir_module_module WHERE name = 'custom_background';

SELECT 'Autovacuum Config' as fix_status, count(*) as config_count
FROM ir_config_parameter WHERE key LIKE 'base.autovacuum%';
