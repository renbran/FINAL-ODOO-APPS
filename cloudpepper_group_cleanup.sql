-- CloudPepper Emergency Group Cleanup Script
-- This script removes duplicate security groups that conflict with our module installation

-- First, remove any existing Payment Voucher User groups that conflict
DELETE FROM res_groups_users_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE name LIKE '%Payment Voucher%'
);

-- Remove the conflicting groups
DELETE FROM res_groups WHERE name IN (
    'Payment Voucher User',
    'Payment Voucher Reviewer', 
    'Payment Voucher Approver',
    'Payment Voucher Authorizer',
    'Payment Voucher Poster',
    'Payment Voucher Manager'
);

-- Remove any menu items that might reference these groups
DELETE FROM ir_ui_menu WHERE name LIKE '%Payment Voucher%';

-- Remove any access rules that reference the old groups
DELETE FROM ir_model_access WHERE name LIKE '%payment_voucher%';

-- Remove any record rules that reference the old groups
DELETE FROM ir_rule WHERE name LIKE '%Payment Voucher%';

-- Clear any cached data
UPDATE ir_model_data SET module = 'to_remove' WHERE module = 'account_payment_approval';
DELETE FROM ir_model_data WHERE module = 'to_remove';

-- Commit the changes
COMMIT;
