-- Get client action details
SELECT 
    id, 
    name->>'en_US' as action_name,
    type,
    tag
FROM ir_actions 
WHERE id = 1038;

-- Verify crm.lead model has the required methods
SELECT 
    COUNT(*) as lead_count,
    COUNT(CASE WHEN type = 'opportunity' THEN 1 END) as opportunity_count,
    COUNT(CASE WHEN probability = 100 THEN 1 END) as won_count,
    SUM(CASE WHEN type = 'opportunity' AND probability > 0 AND probability < 100 THEN expected_revenue ELSE 0 END) as expected_revenue,
    SUM(CASE WHEN probability = 100 THEN expected_revenue ELSE 0 END) as won_revenue
FROM crm_lead;

-- Check if dashboard JavaScript asset is loaded
SELECT 
    name->>'en_US' as asset_name,
    path
FROM ir_asset 
WHERE path LIKE '%crm_dashboard%'
LIMIT 10;
