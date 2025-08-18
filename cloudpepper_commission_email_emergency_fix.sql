-- EMERGENCY COMMISSION EMAIL FIX FOR CLOUDPEPPER
-- Fix Date: 2025-08-18 15:51:41
-- Problem: Computed fields not accessible in email templates
-- Solution: Make commission fields stored and fix templates

-- Step 1: Fix commission_ax purchase.order fields to be stored
UPDATE ir_model_fields 
SET store = TRUE 
WHERE model = 'purchase.order' 
AND name IN ('agent1_partner_id', 'agent2_partner_id', 'project_id', 'unit_id')
AND store = FALSE;

-- Step 2: Update commission email templates with safe field access
UPDATE mail_template 
SET body_html = REPLACE(
    REPLACE(
        REPLACE(
            body_html,
            '<t t-out="object.agent1_partner_id.name"/>',
            '<t t-if="hasattr(object, ''agent1_partner_id'') and object.agent1_partner_id"><t t-out="object.agent1_partner_id.name"/></t><t t-elif="hasattr(object, ''origin_so_id'') and object.origin_so_id and hasattr(object.origin_so_id, ''agent1_partner_id'') and object.origin_so_id.agent1_partner_id"><t t-out="object.origin_so_id.agent1_partner_id.name"/></t><t t-else=""><t t-out="object.partner_id.name"/></t>'
        ),
        '<t t-out="object.project_id.name">',
        '<t t-if="hasattr(object, ''project_id'') and object.project_id"><t t-out="object.project_id.name"/></t><t t-elif="hasattr(object, ''origin_so_id'') and object.origin_so_id and hasattr(object.origin_so_id, ''project_id'') and object.origin_so_id.project_id"><t t-out="object.origin_so_id.project_id.name"/></t><t t-else="">Deal'
    ),
    '<t t-out="object.unit_id.name"/>',
    '<t t-if="hasattr(object, ''unit_id'') and object.unit_id"><t t-out="object.unit_id.name"/></t><t t-elif="hasattr(object, ''origin_so_id'') and object.origin_so_id and hasattr(object.origin_so_id, ''unit_id'') and object.origin_so_id.unit_id"><t t-out="object.origin_so_id.unit_id.name"/></t>'
)
WHERE body_html LIKE '%COMMISSION PAYOUT%'
AND body_html LIKE '%agent1_partner_id%';

-- Step 3: Trigger recomputation of commission fields
UPDATE purchase_order 
SET write_date = NOW() 
WHERE origin_so_id IS NOT NULL;

-- Step 4: Enable all commission-related templates
UPDATE mail_template 
SET active = TRUE 
WHERE body_html LIKE '%COMMISSION%' 
AND model IN ('purchase.order', 'sale.order')
AND active = FALSE;

-- Step 5: Check and log results
INSERT INTO ir_logging (name, level, message, type, create_date, create_uid)
VALUES (
    'commission_email_fix', 
    'INFO', 
    'Emergency commission email template fix applied - agent1_partner_id field access resolved',
    'server',
    NOW(),
    1
);

COMMIT;