-- Payment Approval State SQL Migration
-- Run this SQL script directly on the database if needed

-- 1. Update posted payments to have posted approval state
UPDATE account_payment 
SET approval_state = 'posted',
    write_date = NOW()
WHERE state = 'posted' 
  AND approval_state != 'posted';

-- 2. Update cancelled payments to have cancelled approval state  
UPDATE account_payment 
SET approval_state = 'cancelled',
    write_date = NOW()
WHERE state = 'cancel' 
  AND approval_state != 'cancelled';

-- 3. Update draft payments to have draft approval state
UPDATE account_payment 
SET approval_state = 'draft',
    write_date = NOW()
WHERE state = 'draft' 
  AND approval_state NOT IN ('draft', 'under_review');

-- 4. Set reviewer_id where missing (use create_uid)
UPDATE account_payment 
SET reviewer_id = create_uid,
    reviewer_date = create_date
WHERE approval_state IN ('posted', 'approved', 'for_authorization')
  AND reviewer_id IS NULL
  AND create_uid IS NOT NULL;

-- 5. Set approver_id where missing (use write_uid or create_uid)
UPDATE account_payment 
SET approver_id = COALESCE(write_uid, create_uid),
    approver_date = COALESCE(write_date, create_date)
WHERE approval_state IN ('posted', 'approved', 'for_authorization')
  AND approver_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- 6. Set authorizer_id where missing for posted payments
UPDATE account_payment 
SET authorizer_id = COALESCE(write_uid, create_uid),
    authorizer_date = COALESCE(write_date, create_date)
WHERE approval_state = 'posted'
  AND authorizer_id IS NULL
  AND COALESCE(write_uid, create_uid) IS NOT NULL;

-- Query to check results
SELECT 
    state,
    approval_state,
    COUNT(*) as count
FROM account_payment 
GROUP BY state, approval_state
ORDER BY state, approval_state;
