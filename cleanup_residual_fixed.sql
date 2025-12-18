-- Clean up residual data from crm_executive_dashboard (Odoo 17 compatible)

-- Remove menu items (name is JSONB in Odoo 17)
DELETE FROM ir_ui_menu WHERE name::text LIKE '%Executive Dashboard%' OR name::text LIKE '%crm_executive%';

-- Remove views  
DELETE FROM ir_ui_view WHERE name LIKE '%crm_executive%';

-- Remove actions (correct table names for Odoo 17)
DELETE FROM ir_act_window WHERE name LIKE '%Executive Dashboard%' OR res_model LIKE '%crm_executive%';
DELETE FROM ir_act_server WHERE name LIKE '%crm_executive%';

-- Remove model access rights
DELETE FROM ir_model_access WHERE name LIKE '%crm_executive%';

-- Remove security groups (name is JSONB)
DELETE FROM res_groups WHERE name::text LIKE '%Executive Dashboard%';

-- Remove any scheduled actions (use cron_name field)
DELETE FROM ir_cron WHERE cron_name LIKE '%crm_executive%';

-- Verify module status
SELECT name, state FROM ir_module_module WHERE name='crm_executive_dashboard';
