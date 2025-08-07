-- EMERGENCY SQL FIX FOR ASSETS BACKEND ISSUE
-- This SQL script fixes the missing web.assets_backend and cleans up payment module

BEGIN;

-- Step 1: Clean up all payment_account_enhanced references
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';
DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_attachment WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_asset WHERE path LIKE '%payment_account_enhanced%';
DELETE FROM ir_model_constraint WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_model_field WHERE model LIKE '%payment_account_enhanced%';
DELETE FROM ir_model WHERE model LIKE '%payment_account_enhanced%';
DELETE FROM ir_model_access WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_rule WHERE name LIKE '%payment_account_enhanced%';

-- Step 2: Clean up any broken view inheritance that references web.assets_backend
DELETE FROM ir_ui_view WHERE arch_db LIKE '%inherit_id="web.assets_backend"%' AND key LIKE '%payment_account_enhanced%';

-- Step 3: Ensure web.assets_backend template exists
-- First check if it's missing and recreate if necessary
DO $$
DECLARE
    assets_view_id INTEGER;
    assets_data_id INTEGER;
BEGIN
    -- Check if web.assets_backend view exists
    SELECT res_id INTO assets_view_id 
    FROM ir_model_data 
    WHERE module = 'web' AND name = 'assets_backend' AND model = 'ir.ui.view';
    
    IF assets_view_id IS NULL THEN
        -- Create the missing web.assets_backend view
        INSERT INTO ir_ui_view (name, key, type, arch, active, mode)
        VALUES (
            'assets_backend',
            'web.assets_backend',
            'qweb',
            '<t t-name="web.assets_backend">
    <t t-call="web.assets_common"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient.scss"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient_layout.scss"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/abstract_web_client.js"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/web_client.js"/>
</t>',
            true,
            'primary'
        ) RETURNING id INTO assets_view_id;
        
        -- Create the ir.model.data record
        INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
        VALUES ('assets_backend', 'web', 'ir.ui.view', assets_view_id, false);
        
        RAISE NOTICE 'Created missing web.assets_backend view with ID: %', assets_view_id;
    ELSE
        RAISE NOTICE 'web.assets_backend view already exists with ID: %', assets_view_id;
    END IF;
END $$;

-- Step 4: Clean up any orphaned module records
DELETE FROM ir_module_module WHERE name = 'payment_account_enhanced';

-- Step 5: Vacuum and analyze to optimize database
VACUUM ANALYZE;

COMMIT;

-- Report completion
SELECT 'EMERGENCY SQL FIX COMPLETED SUCCESSFULLY' as status;
