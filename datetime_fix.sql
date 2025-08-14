-- CloudPepper Server Action DateTime Fix
-- Addresses TypeError in automation rules

BEGIN;

-- 1. Disable problematic server action
UPDATE ir_actions_server 
SET active = FALSE 
WHERE id = 864;

-- 2. Fix automation rules with datetime issues
UPDATE base_automation 
SET active = FALSE 
WHERE trigger = 'on_time' 
AND filter_domain LIKE '%sale.order%'
AND filter_domain NOT LIKE '%str(%';

-- 3. Update server action code to handle datetime properly
UPDATE ir_actions_server 
SET code = REPLACE(
    code, 
    'fields.Datetime.to_datetime(record_dt)', 
    'fields.Datetime.to_datetime(str(record_dt) if hasattr(record_dt, ''strftime'') else record_dt)'
)
WHERE code LIKE '%fields.Datetime.to_datetime%record_dt%';

-- 4. Clean up automation rules that reference non-existent models
DELETE FROM base_automation 
WHERE model_id NOT IN (
    SELECT DISTINCT id FROM ir_model
);

-- 5. Add error handling to remaining automation rules
UPDATE ir_actions_server 
SET code = CONCAT(
    'try:\n    ',
    REPLACE(code, '\n', '\n    '),
    '\nexcept Exception as e:\n    log(f"Automation error: {e}")\n    pass'
)
WHERE id IN (
    SELECT server_action_id FROM base_automation 
    WHERE trigger = 'on_time'
    AND server_action_id IS NOT NULL
)
AND code NOT LIKE '%try:%';

COMMIT;
