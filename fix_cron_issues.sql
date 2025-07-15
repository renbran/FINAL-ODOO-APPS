-- Fix for cron job with invalid interval_type
-- This script fixes the problematic cron job that's causing the KeyError: None

-- Update the problematic cron job to have a valid interval_type
-- CRM: Lead Assignment cron job (ID 21) has NULL interval_type
UPDATE ir_cron 
SET interval_type = 'days', 
    interval_number = 1,
    active = false  -- Keep it inactive for safety
WHERE cron_name = 'CRM: Lead Assignment' 
   OR (interval_type IS NULL AND cron_name LIKE '%Lead Assignment%');

-- Alternative: Delete the problematic cron job if it's not needed
-- DELETE FROM ir_cron WHERE cron_name = 'CRM: Lead Assignment' AND interval_type IS NULL;

-- Check for any other cron jobs with NULL interval_type
SELECT id, cron_name, interval_type, interval_number, active 
FROM ir_cron 
WHERE interval_type IS NULL;

-- Deactivate any other cron jobs with NULL interval_type for safety
UPDATE ir_cron 
SET active = false 
WHERE interval_type IS NULL;
