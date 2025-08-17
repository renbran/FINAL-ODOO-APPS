-- Sales Order Status SQL Migration
-- Run this SQL script directly on the database if needed

-- 1. Update confirmed/done orders to have 'post' order status
UPDATE sale_order 
SET order_status = 'post',
    write_date = NOW()
WHERE state IN ('sale', 'done') 
  AND order_status NOT IN ('post', 'approved');

-- 2. Update draft orders to have 'draft' order status
UPDATE sale_order 
SET order_status = 'draft',
    write_date = NOW()
WHERE state = 'draft' 
  AND order_status NOT IN ('draft', 'document_review');

-- 3. Set documentation_user_id where missing (use create_uid)
UPDATE sale_order 
SET documentation_user_id = create_uid
WHERE order_status IN ('post', 'approved', 'final_review')
  AND documentation_user_id IS NULL
  AND create_uid IS NOT NULL;

-- 4. Set commission_user_id where missing (use write_uid or create_uid)
UPDATE sale_order 
SET commission_user_id = COALESCE(write_uid, create_uid)
WHERE order_status IN ('post', 'approved', 'final_review')
  AND commission_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 5. Set allocation_user_id where missing
UPDATE sale_order 
SET allocation_user_id = COALESCE(write_uid, create_uid)
WHERE order_status IN ('post', 'approved', 'final_review')
  AND allocation_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 6. Set final_review_user_id where missing
UPDATE sale_order 
SET final_review_user_id = COALESCE(write_uid, create_uid)
WHERE order_status IN ('post', 'approved', 'final_review')
  AND final_review_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 7. Set approval_user_id where missing for posted orders
UPDATE sale_order 
SET approval_user_id = COALESCE(write_uid, create_uid)
WHERE order_status = 'post'
  AND approval_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 8. Set posting_user_id where missing for posted orders
UPDATE sale_order 
SET posting_user_id = COALESCE(write_uid, create_uid)
WHERE order_status = 'post'
  AND posting_user_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- Query to check results
SELECT 
    state,
    order_status,
    COUNT(*) as count
FROM sale_order 
GROUP BY state, order_status
ORDER BY state, order_status;
