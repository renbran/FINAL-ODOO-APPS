-- Test currency display in CRM dashboard data
SELECT 
    'Won Opportunities' as metric,
    COUNT(*) as count,
    CONCAT(
        (SELECT symbol FROM res_currency WHERE id = 129),
        ' ',
        ROUND(SUM(expected_revenue)::numeric, 2)
    ) as amount
FROM crm_lead 
WHERE probability = 100 AND type = 'opportunity'
UNION ALL
SELECT 
    'Open Opportunities',
    COUNT(*),
    CONCAT(
        (SELECT symbol FROM res_currency WHERE id = 129),
        ' ',
        ROUND(SUM(expected_revenue)::numeric, 2)
    )
FROM crm_lead 
WHERE probability > 0 AND probability < 100 AND type = 'opportunity'
UNION ALL
SELECT 
    'Total Pipeline Value',
    COUNT(*),
    CONCAT(
        (SELECT symbol FROM res_currency WHERE id = 129),
        ' ',
        ROUND(SUM(expected_revenue)::numeric, 2)
    )
FROM crm_lead 
WHERE type = 'opportunity' AND expected_revenue > 0;
