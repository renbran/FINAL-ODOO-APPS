-- Fixed CRM Data Check

-- Module status
SELECT name, state, latest_version FROM ir_module_module WHERE name = 'crm_dashboard';

-- Stage structure (Odoo 17 doesn't have probability column in crm_stage)
SELECT id, name::text, sequence, is_won, fold FROM crm_stage ORDER BY sequence;

-- Check users with leads
SELECT u.id, u.login, COUNT(cl.id) as lead_count 
FROM res_users u
LEFT JOIN crm_lead cl ON cl.user_id = u.id
WHERE u.active = true
GROUP BY u.id, u.login
HAVING COUNT(cl.id) > 0
ORDER BY lead_count DESC
LIMIT 10;

-- Check probability distribution in leads
SELECT probability, COUNT(*) as count
FROM crm_lead
WHERE type = 'opportunity'
GROUP BY probability
ORDER BY probability DESC;

-- Check stages with lead counts
SELECT s.id, s.name::text, s.is_won, COUNT(l.id) as lead_count
FROM crm_stage s
LEFT JOIN crm_lead l ON l.stage_id = s.id
GROUP BY s.id, s.name, s.is_won
ORDER BY s.sequence;

-- Check if any opportunities have expected_revenue
SELECT COUNT(*) as opportunities_with_revenue,
       SUM(expected_revenue) as total_expected_revenue
FROM crm_lead 
WHERE type = 'opportunity' AND expected_revenue IS NOT NULL AND expected_revenue > 0;

-- Check won opportunities
SELECT COUNT(*) as won_opportunities,
       SUM(expected_revenue) as won_revenue
FROM crm_lead
WHERE type = 'opportunity' AND probability = 100;

-- Check dashboard menu access
SELECT m.id, m.name::text, m.action, m.parent_id 
FROM ir_ui_menu m
WHERE m.name::text LIKE '%Dashboard%' OR m.name::text LIKE '%dashboard%'
ORDER BY m.id;
