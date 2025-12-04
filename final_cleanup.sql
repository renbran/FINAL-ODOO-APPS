-- Final cleanup for crm_executive_dashboard

-- Remove actions with JSONB name field
DELETE FROM ir_act_window WHERE name::text LIKE '%Executive Dashboard%' OR res_model LIKE '%crm_executive%';
DELETE FROM ir_act_server WHERE name::text LIKE '%crm_executive%';

-- Verify final state
SELECT name, state FROM ir_module_module WHERE name='crm_executive_dashboard';
