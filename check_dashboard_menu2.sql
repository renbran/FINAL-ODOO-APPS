-- Check ir_actions table structure
SELECT 
    model,
    name->>'en_US' as name,
    type,
    id
FROM ir_actions 
WHERE name->>'en_US' ILIKE '%dashboard%'
LIMIT 10;

-- Find CRM parent menu
SELECT id, name, action FROM ir_ui_menu 
WHERE name->>'en_US' = 'CRM';

-- Find all menus under CRM
SELECT m.id, m.name->>'en_US' as menu_name, m.action, m.sequence
FROM ir_ui_menu m
WHERE m.parent_id = (SELECT id FROM ir_ui_menu WHERE name->>'en_US' = 'CRM' LIMIT 1)
ORDER BY m.sequence;
