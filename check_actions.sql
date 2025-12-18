-- List all ir_actions tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'ir_actions%';

-- Check for dashboard in all actions
SELECT 'act_window' as type, id, name FROM ir_act_window WHERE name ILIKE '%dashboard%'
UNION ALL
SELECT 'client' as type, id, name FROM ir_act_client WHERE tag = 'crm_dashboard';

-- Find CRM menus
SELECT id, name, action FROM ir_ui_menu 
WHERE name IN ('CRM', 'Dashboard') 
LIMIT 20;
