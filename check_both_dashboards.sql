-- Check both dashboard actions
SELECT id, name::text, tag, target 
FROM ir_act_client 
WHERE id IN (1038, 1221);

-- Find their menus
SELECT m.id, m.name::text, m.action, m.parent_id,
       (SELECT name::text FROM ir_ui_menu WHERE id = m.parent_id) as parent_name
FROM ir_ui_menu m
WHERE m.action IN ('ir.actions.client,1038', 'ir.actions.client,1221');

-- Check views for both (cast name to text)
SELECT id, name::text, type, arch_fs
FROM ir_ui_view
WHERE name::text LIKE '%crm_dashboard%' OR name::text LIKE '%crm_strategic%'
ORDER BY name;

-- Check if crm_dashboard module is providing the right action
SELECT imd.name, imd.model, imd.res_id, imd.module
FROM ir_model_data imd
WHERE imd.module = 'crm_dashboard' AND imd.model IN ('ir.act.client', 'ir.ui.menu')
ORDER BY imd.model, imd.name;
