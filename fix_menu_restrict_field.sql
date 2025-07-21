-- Fix for ir.ui.menu restrict_user_ids field
-- Run this in your PostgreSQL database

-- Check if table exists and add column if missing
DO $$
BEGIN
    -- Add restrict_user_ids column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'ir_ui_menu' AND column_name = 'restrict_user_ids'
    ) THEN
        -- This would be done by Odoo automatically, but we can't add it manually
        -- as it's a Many2many field requiring a bridge table
        RAISE NOTICE 'restrict_user_ids field missing - need to fix via Odoo module upgrade';
    END IF;
END
$$;

-- Temporarily disable the security rule to prevent the error
UPDATE ir_rule 
SET active = false 
WHERE name = 'Restrict Menu from Users' 
  AND model_id = (SELECT id FROM ir_model WHERE model = 'ir.ui.menu');

-- Commit the changes
COMMIT;

RAISE NOTICE 'Security rule disabled. Now upgrade the hide_menu_user module in Odoo.';
