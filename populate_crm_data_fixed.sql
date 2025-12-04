-- ================================================================
-- CRM Dashboard Data Population Script (Fixed for Odoo 17)
-- Database: scholarixv2
-- Date: November 27, 2025
-- Purpose: Populate missing data for CRM Dashboard functionality
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Populate Expected Revenue for Opportunities
-- ================================================================
UPDATE crm_lead 
SET expected_revenue = 
    CASE 
        WHEN probability >= 90 THEN 100000.00 + (random() * 50000)::numeric(10,2)
        WHEN probability >= 70 THEN 75000.00 + (random() * 25000)::numeric(10,2)
        WHEN probability >= 50 THEN 50000.00 + (random() * 25000)::numeric(10,2)
        WHEN probability >= 20 THEN 25000.00 + (random() * 25000)::numeric(10,2)
        WHEN probability > 0 THEN 10000.00 + (random() * 15000)::numeric(10,2)
        ELSE NULL
    END
WHERE type = 'opportunity' 
  AND expected_revenue IS NULL
  AND probability IS NOT NULL;

SELECT 
    'Opportunities with Revenue' as metric,
    COUNT(expected_revenue) as count,
    SUM(expected_revenue) as total
FROM crm_lead 
WHERE type = 'opportunity';

-- ================================================================
-- STEP 2: Create Won Opportunities (50 records)
-- ================================================================
UPDATE crm_lead 
SET stage_id = 10,  -- Closed Implementation (Won)
    probability = 100,
    active = false,
    date_closed = CURRENT_DATE - (random() * 90)::int,
    expected_revenue = COALESCE(expected_revenue, 75000.00)
WHERE id IN (
    SELECT id 
    FROM crm_lead 
    WHERE type = 'opportunity'
      AND active = true
      AND probability >= 70
      AND user_id IS NOT NULL
    ORDER BY probability DESC, expected_revenue DESC NULLS LAST
    LIMIT 50
);

SELECT 
    'Won Opportunities' as metric,
    COUNT(*) as count,
    SUM(expected_revenue) as revenue
FROM crm_lead 
WHERE type = 'opportunity' AND probability = 100;

-- ================================================================
-- STEP 3: Create Lost Opportunities (25 records)
-- ================================================================
UPDATE crm_lead 
SET stage_id = 9,  -- Not Interested
    probability = 0,
    active = false,
    date_deadline = CURRENT_DATE - (random() * 60)::int
WHERE id IN (
    SELECT id 
    FROM crm_lead 
    WHERE type = 'opportunity'
      AND active = true
      AND probability < 30
      AND user_id IS NOT NULL
    ORDER BY probability ASC
    LIMIT 25
);

SELECT 
    'Lost Opportunities' as metric,
    COUNT(*) as count
FROM crm_lead 
WHERE type = 'opportunity' AND probability = 0 AND active = false;

-- ================================================================
-- STEP 4: Set Deadlines for Active Opportunities
-- ================================================================
UPDATE crm_lead 
SET date_deadline = CURRENT_DATE + 
    CASE 
        WHEN probability >= 80 THEN (random() * 30)::int
        WHEN probability >= 50 THEN 30 + (random() * 30)::int
        WHEN probability >= 20 THEN 60 + (random() * 30)::int
        ELSE 90 + (random() * 60)::int
    END
WHERE type = 'opportunity'
  AND active = true
  AND date_deadline IS NULL;

SELECT 
    'Opportunities with Deadline' as metric,
    COUNT(*) as count
FROM crm_lead 
WHERE type = 'opportunity' AND date_deadline IS NOT NULL;

-- ================================================================
-- STEP 5: Update User Sales Targets
-- ================================================================
UPDATE res_users 
SET sales = 500000.00
WHERE id IN (
    SELECT DISTINCT user_id 
    FROM crm_lead 
    WHERE user_id IS NOT NULL
)
AND sales IS NULL;

SELECT 
    'Users with Sales Targets' as metric,
    COUNT(*) as count
FROM res_users
WHERE sales IS NOT NULL;

-- ================================================================
-- STEP 6: Final Dashboard Data Summary
-- ================================================================
SELECT 'Total Leads' as metric, COUNT(*) as value FROM crm_lead WHERE type = 'lead'
UNION ALL
SELECT 'Active Opportunities', COUNT(*) FROM crm_lead WHERE type = 'opportunity' AND active = true
UNION ALL
SELECT 'Won Opportunities', COUNT(*) FROM crm_lead WHERE type = 'opportunity' AND probability = 100
UNION ALL
SELECT 'Lost Opportunities', COUNT(*) FROM crm_lead WHERE type = 'opportunity' AND probability = 0 AND active = false
UNION ALL
SELECT 'Expected Revenue (Open)', COALESCE(SUM(expected_revenue), 0) FROM crm_lead WHERE type = 'opportunity' AND active = true AND probability NOT IN (0, 100)
UNION ALL
SELECT 'Won Revenue', COALESCE(SUM(expected_revenue), 0) FROM crm_lead WHERE type = 'opportunity' AND probability = 100
UNION ALL
SELECT 'Opportunities with Deadlines', COUNT(*) FROM crm_lead WHERE type = 'opportunity' AND date_deadline IS NOT NULL
UNION ALL
SELECT 'Users with Sales Targets', COUNT(*) FROM res_users WHERE sales IS NOT NULL;

COMMIT;
