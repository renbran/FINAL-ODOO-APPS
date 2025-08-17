
-- Payment Approval State Validation Query
-- Run this query to see which payments need migration

SELECT 
    'NEEDS_MIGRATION' as category,
    state as payment_state,
    approval_state,
    COUNT(*) as count,
    STRING_AGG(name, ', ') as examples
FROM account_payment 
WHERE (
    (state = 'posted' AND approval_state != 'posted') OR
    (state = 'cancel' AND approval_state != 'cancelled') OR
    (state = 'draft' AND approval_state NOT IN ('draft', 'under_review'))
)
GROUP BY state, approval_state

UNION ALL

SELECT 
    'ALREADY_SYNCED' as category,
    state as payment_state,
    approval_state,
    COUNT(*) as count,
    '' as examples
FROM account_payment 
WHERE (
    (state = 'posted' AND approval_state = 'posted') OR
    (state = 'cancel' AND approval_state = 'cancelled') OR
    (state = 'draft' AND approval_state IN ('draft', 'under_review'))
)
GROUP BY state, approval_state

ORDER BY category, payment_state, approval_state;

-- Summary query
SELECT 
    CASE 
        WHEN (state = 'posted' AND approval_state = 'posted') OR
             (state = 'cancel' AND approval_state = 'cancelled') OR
             (state = 'draft' AND approval_state IN ('draft', 'under_review'))
        THEN 'SYNCED'
        ELSE 'NEEDS_MIGRATION'
    END as sync_status,
    COUNT(*) as count
FROM account_payment
GROUP BY sync_status;
