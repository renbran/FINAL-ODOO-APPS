-- Find CRM Dashboard Action
SELECT id, name::text, res_model, view_mode 
FROM ir_act_window 
WHERE name::text LIKE '%CRM%' AND name::text LIKE '%Dashboard%';

-- Find the client action for dashboard
SELECT id, name, tag, target, params 
FROM ir_actions_client 
WHERE tag LIKE '%dashboard%' OR name LIKE '%Dashboard%';

-- Check if there's a specific CRM dashboard action
SELECT id, name::text, res_model 
FROM ir_act_window 
WHERE res_model = 'crm.lead' OR name::text LIKE '%crm%dashboard%';

-- Find menu pointing to CRM dashboard
SELECT m.id, m.name::text, m.action, m.sequence, m.parent_id,
       (SELECT name::text FROM ir_ui_menu WHERE id = m.parent_id) as parent_name
FROM ir_ui_menu m
WHERE m.action LIKE '%1221%' OR m.name::text LIKE '%Strategic Dashboard%';
