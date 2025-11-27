-- Check CRM Dashboard Module Status
SELECT name, state, latest_version, installed_version 
FROM ir_module_module 
WHERE name = 'crm_dashboard';

-- Check if CRM data exists
SELECT COUNT(*) as total_leads FROM crm_lead;
SELECT COUNT(*) as total_opportunities FROM crm_lead WHERE type = 'opportunity';
SELECT COUNT(*) as active_opportunities FROM crm_lead WHERE type = 'opportunity' AND active = true;

-- Check stages
SELECT id, name, sequence, probability, is_won, fold FROM crm_stage ORDER BY sequence;

-- Check users with CRM data
SELECT u.id, u.name, COUNT(cl.id) as lead_count 
FROM res_users u
LEFT JOIN crm_lead cl ON cl.user_id = u.id
GROUP BY u.id, u.name
HAVING COUNT(cl.id) > 0
ORDER BY lead_count DESC
LIMIT 10;

-- Check teams
SELECT id, name, invoiced_target FROM crm_team;

-- Check recent leads/opportunities
SELECT id, name, type, stage_id, user_id, expected_revenue, probability, active, date_deadline, date_closed, create_date
FROM crm_lead 
ORDER BY create_date DESC 
LIMIT 20;

-- Check if dashboard views exist
SELECT id, name, model, type FROM ir_ui_view WHERE name LIKE '%crm_dashboard%';

-- Check if dashboard actions exist
SELECT id, name::text, res_model FROM ir_act_window WHERE name::text LIKE '%Dashboard%' AND res_model LIKE '%crm%';
