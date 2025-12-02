-- ================================================================
-- UPDATE EXISTING SALE CONTRACTS WITH PAYMENT SCHEDULES
-- ================================================================
-- This script updates existing property.vendor (sale contract) records
-- to inherit payment schedules from their associated properties
-- 
-- Run this on production database ONCE to fix existing bookings
-- created before the payment schedule inheritance fix was deployed
-- ================================================================

BEGIN;

-- Update existing sale contracts to inherit payment schedules from properties
UPDATE property_vendor pv
SET 
    payment_schedule_id = pd.payment_schedule_id,
    use_schedule = TRUE,
    schedule_from_property = TRUE
FROM property_details pd
WHERE pv.property_id = pd.id
  AND pd.is_payment_plan = TRUE
  AND pd.payment_schedule_id IS NOT NULL
  AND pv.payment_schedule_id IS NULL  -- Only update contracts without schedules
  AND pv.stage IN ('draft', 'booked', 'on_progress');  -- Only active/draft contracts

-- Display updated records
SELECT 
    pv.id,
    pv.sold_seq as "Contract Ref",
    pd.name as "Property",
    ps.name as "Payment Schedule",
    pv.use_schedule as "Using Schedule",
    pv.schedule_from_property as "Inherited"
FROM property_vendor pv
JOIN property_details pd ON pv.property_id = pd.id
LEFT JOIN payment_schedule ps ON pv.payment_schedule_id = ps.id
WHERE pv.use_schedule = TRUE
  AND pv.schedule_from_property = TRUE
ORDER BY pv.id DESC
LIMIT 20;

-- Commit the transaction
COMMIT;

-- ================================================================
-- VERIFICATION QUERY (Run separately to check results)
-- ================================================================
-- SELECT 
--     COUNT(*) FILTER (WHERE payment_schedule_id IS NOT NULL) as "With Schedule",
--     COUNT(*) FILTER (WHERE payment_schedule_id IS NULL) as "Without Schedule",
--     COUNT(*) as "Total Active Contracts"
-- FROM property_vendor
-- WHERE stage IN ('draft', 'booked', 'on_progress');
