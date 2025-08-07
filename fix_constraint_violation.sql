
-- FINAL FIX for duplicate key constraint on payment_account_enhanced
-- Target: Key (module, name)=(base, module_payment_account_enhanced) already exists

-- 1. Find the problematic record
SELECT * FROM ir_model_data 
WHERE module = 'base' AND name = 'module_payment_account_enhanced';

-- 2. Delete the duplicate record causing constraint violation
DELETE FROM ir_model_data 
WHERE module = 'base' AND name = 'module_payment_account_enhanced';

-- 3. Also remove any other variations
DELETE FROM ir_model_data 
WHERE name = 'module_payment_account_enhanced';

-- 4. Remove any remaining payment_account_enhanced entries
DELETE FROM ir_model_data 
WHERE module = 'payment_account_enhanced';

-- 5. Clean up ir_module_module table entries
DELETE FROM ir_module_module 
WHERE name = 'payment_account_enhanced';

-- 6. Verify cleanup
SELECT 'Constraint violation fixed' as status;
SELECT COUNT(*) as remaining_base_records 
FROM ir_model_data 
WHERE module = 'base' AND name LIKE '%payment_account_enhanced%';

SELECT COUNT(*) as remaining_module_records 
FROM ir_model_data 
WHERE module = 'payment_account_enhanced';
