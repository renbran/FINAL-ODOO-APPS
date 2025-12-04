-- Check module status
SELECT id, name, state FROM ir_module_module WHERE name = 'crm_dashboard';

-- Check client action
SELECT id, name, tag FROM ir_actions_client WHERE tag = 'crm_dashboard';

-- Check menu items
SELECT m.id, m.name, m.action, m.parent_id
FROM ir_ui_menu m
WHERE m.name ILIKE '%dashboard%' 
  AND m.parent_id IN (SELECT id FROM ir_ui_menu WHERE name = 'CRM');
