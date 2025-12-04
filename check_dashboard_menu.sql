-- Check module status
SELECT id, name, state FROM ir_module_module WHERE name = 'crm_dashboard';

-- Check client action
SELECT id, name, tag FROM ir_actions_act_window WHERE name ILIKE '%dashboard%';

-- Check menu items for CRM
SELECT m.id, m.name::text, m.action, m.parent_id
FROM ir_ui_menu m
WHERE m.name::text ILIKE '%dashboard%' 
  AND m.parent_id IN (SELECT id FROM ir_ui_menu WHERE name::text = 'CRM');

-- Get all CRM menu items
SELECT id, name::text, action FROM ir_ui_menu 
WHERE parent_id IN (SELECT id FROM ir_ui_menu WHERE name::text = 'CRM')
ORDER BY sequence;
