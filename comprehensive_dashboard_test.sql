-- ===========================================
-- CRM DASHBOARD COMPREHENSIVE TEST
-- ===========================================

\echo '===================='
\echo 'TEST 1: Module Status'
\echo '===================='
SELECT 
    id, 
    name, 
    state,
    latest_version
FROM ir_module_module 
WHERE name = 'crm_dashboard';

\echo ''
\echo '===================='
\echo 'TEST 2: Dashboard Menu'
\echo '===================='
SELECT 
    m.id as menu_id,
    m.name->>'en_US' as menu_name,
    m.action,
    m.sequence,
    m.parent_id
FROM ir_ui_menu m
WHERE m.id = 742;

\echo ''
\echo '===================='
\echo 'TEST 3: Dashboard Action'
\echo '===================='
SELECT 
    id,
    name->>'en_US' as action_name,
    type,
    binding_model_id,
    binding_type
FROM ir_actions
WHERE id = 1038;

\echo ''
\echo '========================'
\echo 'TEST 4: CRM Data Summary'
\echo '========================'
SELECT 
    'Total Records' as metric,
    COUNT(*) as count,
    '-' as amount
FROM crm_lead
UNION ALL
SELECT 
    'Leads',
    COUNT(*),
    '-'
FROM crm_lead WHERE type = 'lead'
UNION ALL
SELECT 
    'Opportunities',
    COUNT(*),
    '-'
FROM crm_lead WHERE type = 'opportunity'
UNION ALL
SELECT 
    'Won Opportunities',
    COUNT(*),
    CONCAT('$', ROUND(SUM(expected_revenue)::numeric, 2))
FROM crm_lead WHERE probability = 100 AND type = 'opportunity'
UNION ALL
SELECT 
    'Lost Opportunities',
    COUNT(*),
    '-'
FROM crm_lead WHERE probability = 0 AND active = false AND type = 'opportunity'
UNION ALL
SELECT 
    'Open Opportunities',
    COUNT(*),
    CONCAT('$', ROUND(SUM(expected_revenue)::numeric, 2))
FROM crm_lead WHERE probability > 0 AND probability < 100 AND type = 'opportunity';

\echo ''
\echo '============================'
\echo 'TEST 5: Revenue Distribution'
\echo '============================'
SELECT 
    CASE 
        WHEN expected_revenue IS NULL THEN 'NULL'
        WHEN expected_revenue = 0 THEN 'ZERO'
        WHEN expected_revenue > 0 THEN 'HAS_VALUE'
    END as revenue_status,
    COUNT(*) as count,
    CONCAT('$', ROUND(SUM(COALESCE(expected_revenue, 0))::numeric, 2)) as total_revenue
FROM crm_lead 
WHERE type = 'opportunity'
GROUP BY revenue_status
ORDER BY count DESC;

\echo ''
\echo '========================'
\echo 'TEST 6: Stage Analysis'
\echo '========================'
SELECT 
    s.name->>'en_US' as stage_name,
    s.sequence,
    s.is_won,
    COUNT(l.id) as opportunity_count,
    CONCAT('$', ROUND(SUM(COALESCE(l.expected_revenue, 0))::numeric, 2)) as total_revenue
FROM crm_stage s
LEFT JOIN crm_lead l ON l.stage_id = s.id AND l.type = 'opportunity'
GROUP BY s.id, s.name, s.sequence, s.is_won
ORDER BY s.sequence;

\echo ''
\echo '================================='
\echo 'TEST 7: Users with Sales Targets'
\echo '================================='
SELECT 
    u.login,
    u.sales as sales_target,
    COUNT(l.id) as opportunities,
    CONCAT('$', ROUND(SUM(COALESCE(l.expected_revenue, 0))::numeric, 2)) as total_revenue
FROM res_users u
LEFT JOIN crm_lead l ON l.user_id = u.id AND l.type = 'opportunity'
WHERE u.sales IS NOT NULL AND u.sales > 0
GROUP BY u.id, u.login, u.sales
ORDER BY u.sales DESC
LIMIT 10;

\echo ''
\echo '======================================'
\echo 'TEST 8: Dashboard JavaScript Assets'
\echo '====================================='
SELECT 
    bundle->>'en_US' as bundle_name,
    path,
    sequence
FROM ir_asset
WHERE path LIKE '%crm_dashboard%'
ORDER BY sequence
LIMIT 10;

\echo ''
\echo '===================================='
\echo 'TEST 9: Opportunities with Deadlines'
\echo '===================================='
SELECT 
    CASE 
        WHEN date_deadline IS NULL THEN 'NO_DEADLINE'
        WHEN date_deadline < CURRENT_DATE THEN 'OVERDUE'
        WHEN date_deadline = CURRENT_DATE THEN 'TODAY'
        WHEN date_deadline > CURRENT_DATE THEN 'FUTURE'
    END as deadline_status,
    COUNT(*) as count
FROM crm_lead
WHERE type = 'opportunity' AND active = true
GROUP BY deadline_status
ORDER BY count DESC;

\echo ''
\echo '================================'
\echo 'TEST 10: Dashboard View Records'
\echo '================================'
SELECT 
    v.id,
    v.name->>'en_US' as view_name,
    v.type,
    v.model,
    v.mode
FROM ir_ui_view v
WHERE v.model = 'crm.lead' 
  AND (v.name->>'en_US' ILIKE '%dashboard%' OR v.key LIKE '%dashboard%')
LIMIT 5;

\echo ''
\echo '==============================='
\echo 'DASHBOARD TEST SUMMARY'
\echo '==============================='
\echo 'All database queries completed.'
\echo 'If all tests show data, the dashboard should render properly.'
\echo ''
\echo 'Next: Login to https://stagingtry.cloudpepper.site/'
\echo 'Navigate to: CRM > Dashboard'
\echo 'Verify tiles display data and filters work.'
\echo '==============================='
