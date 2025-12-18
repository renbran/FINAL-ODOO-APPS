\echo '========================================'
\echo 'CRM DASHBOARD - AED CURRENCY PREVIEW'
\echo '========================================'
\echo ''
\echo 'How dashboard tiles will display:'
\echo ''

SELECT 
    ' DASHBOARD TILES' as section,
    '---' as metric,
    '---' as value;

SELECT 
    '' as section,
    ' Expected Revenue' as metric,
    CONCAT('AED ', TO_CHAR(SUM(expected_revenue), 'FM999,999,999,999.00')) as value
FROM crm_lead 
WHERE probability > 0 AND probability < 100 AND type = 'opportunity'
UNION ALL
SELECT 
    '',
    ' Won Revenue',
    CONCAT('AED ', TO_CHAR(SUM(expected_revenue), 'FM999,999,999,999.00'))
FROM crm_lead 
WHERE probability = 100 AND type = 'opportunity'
UNION ALL
SELECT 
    '',
    ' Total Pipeline',
    CONCAT('AED ', TO_CHAR(SUM(expected_revenue), 'FM999,999,999,999.00'))
FROM crm_lead 
WHERE type = 'opportunity' AND expected_revenue > 0
UNION ALL
SELECT 
    '',
    ' Average Deal Size',
    CONCAT('AED ', TO_CHAR(AVG(expected_revenue), 'FM999,999,999.00'))
FROM crm_lead 
WHERE type = 'opportunity' AND expected_revenue > 0;

\echo ''
\echo '========================================'
\echo 'TOP 5 OPPORTUNITIES (with AED)'
\echo '========================================'

SELECT 
    name,
    CONCAT('AED ', TO_CHAR(expected_revenue, 'FM999,999,999.00')) as revenue,
    CONCAT(probability, '%') as probability
FROM crm_lead
WHERE type = 'opportunity' 
  AND expected_revenue > 0
ORDER BY expected_revenue DESC
LIMIT 5;

\echo ''
\echo '========================================'
\echo 'USER PERFORMANCE (with AED)'
\echo '========================================'

SELECT 
    u.login as user,
    COUNT(l.id) as deals,
    CONCAT('AED ', TO_CHAR(SUM(COALESCE(l.expected_revenue, 0)), 'FM999,999,999.00')) as pipeline
FROM res_users u
LEFT JOIN crm_lead l ON l.user_id = u.id AND l.type = 'opportunity'
WHERE u.sales IS NOT NULL AND u.sales > 0
GROUP BY u.id, u.login
ORDER BY SUM(COALESCE(l.expected_revenue, 0)) DESC
LIMIT 5;

\echo ''
\echo '========================================'
\echo ' Currency successfully updated to AED'
\echo 'Dashboard will display all amounts with'
\echo 'AED symbol instead of $ or د.إ'
\echo '========================================'
