-- Emergency SQL script to assign payment groups to users
-- Run this in CloudPepper database if needed

-- Add reviewer group to users who created payments
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 
    (SELECT id FROM res_groups WHERE name = 'Payment Reviewer' LIMIT 1) as gid,
    DISTINCT create_uid as uid
FROM account_payment 
WHERE create_uid IS NOT NULL
AND create_uid NOT IN (
    SELECT uid FROM res_groups_users_rel 
    WHERE gid = (SELECT id FROM res_groups WHERE name = 'Payment Reviewer' LIMIT 1)
)
AND (SELECT id FROM res_groups WHERE name = 'Payment Reviewer' LIMIT 1) IS NOT NULL;

-- Add approver group to admin users
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 
    (SELECT id FROM res_groups WHERE name = 'Payment Approver' LIMIT 1) as gid,
    ru.id as uid
FROM res_users ru
JOIN res_groups_users_rel rgur ON ru.id = rgur.uid
JOIN res_groups rg ON rgur.gid = rg.id
WHERE rg.category_id = (SELECT id FROM ir_module_category WHERE name = 'Administration' LIMIT 1)
AND ru.id NOT IN (
    SELECT uid FROM res_groups_users_rel 
    WHERE gid = (SELECT id FROM res_groups WHERE name = 'Payment Approver' LIMIT 1)
)
AND (SELECT id FROM res_groups WHERE name = 'Payment Approver' LIMIT 1) IS NOT NULL;
