-- Find client actions (correct table name in Odoo 17)
SELECT id, name, tag, target 
FROM ir_act_client 
WHERE id = 1221 OR tag LIKE '%dashboard%';

-- Check CRM menu structure
SELECT m.id, m.name::text, m.action, m.parent_id
FROM ir_ui_menu m
WHERE m.parent_id = 859 OR m.id = 859
ORDER BY m.sequence;

-- Check what module provides the dashboard
SELECT imd.name, imd.model, imd.res_id, imd.module
FROM ir_model_data imd
WHERE imd.model = 'ir.act.client' AND imd.res_id = 1221;

-- Find the dashboard template/view
SELECT id, name, arch_db, type
FROM ir_ui_view
WHERE name LIKE '%crm%dashboard%' OR arch_db LIKE '%CRMDashboard%'
LIMIT 5;
