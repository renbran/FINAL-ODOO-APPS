-- Emergency CloudPepper Commission Email Fix
-- Execute these commands in CloudPepper database

-- Step 1: Backup problematic templates
CREATE TABLE mail_template_backup_emergency AS 
SELECT *, NOW() as backup_date 
FROM mail_template 
WHERE body_html LIKE '%object.agent1_partner_id%' 
AND active = true;

-- Step 2: Disable problematic templates
UPDATE mail_template 
SET active = false 
WHERE body_html LIKE '%object.agent1_partner_id%' 
AND model = 'purchase.order'
AND active = true;

-- Step 3: Disable related automation rules
UPDATE base_automation 
SET active = false 
WHERE model_id IN (
    SELECT id FROM ir_model WHERE model = 'purchase.order'
)
AND filter_domain LIKE '%agent1_partner_id%';

-- Step 4: Verify changes
SELECT name, model, active 
FROM mail_template 
WHERE body_html LIKE '%object.agent1_partner_id%';
