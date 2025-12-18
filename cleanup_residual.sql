-- Clean up residual data from crm_executive_dashboard

-- Remove menu items
DELETE FROM ir_ui_menu WHERE name LIKE '%Executive Dashboard%' OR name LIKE '%crm_executive%';

-- Remove views
DELETE FROM ir_ui_view WHERE name LIKE '%crm_executive%';

-- Remove actions
DELETE FROM ir_actions_act_window WHERE name LIKE '%Executive Dashboard%' OR res_model LIKE '%crm_executive%';
DELETE FROM ir_actions_server WHERE name LIKE '%crm_executive%';
DELETE FROM ir_actions_client WHERE name LIKE '%crm_executive%';

-- Remove model access rights
DELETE FROM ir_model_access WHERE name LIKE '%crm_executive%';

-- Remove security groups if any
DELETE FROM res_groups WHERE name LIKE '%Executive Dashboard%';

-- Remove any scheduled actions
DELETE FROM ir_cron WHERE name LIKE '%crm_executive%';

-- Remove assets if any
DELETE FROM ir_asset WHERE path LIKE '%crm_executive%';

-- Verify module is uninstalled
SELECT name, state FROM ir_module_module WHERE name='crm_executive_dashboard';
