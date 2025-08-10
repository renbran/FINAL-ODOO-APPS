-- Remote Database Cleanup Script for account_payment_final module
-- Execute this in your PostgreSQL database BEFORE installing the module

-- Step 1: Clean up invalid data in account_payment table (if it exists)
UPDATE account_payment SET 
    submitted_by = NULL,
    reviewed_by = NULL, 
    approved_by = NULL,
    authorized_by = NULL,
    posted_by = NULL 
WHERE 
    (submitted_by IS NOT NULL AND CAST(submitted_by AS TEXT) = 'ADMINISTRATOR')
    OR (reviewed_by IS NOT NULL AND CAST(reviewed_by AS TEXT) = 'ADMINISTRATOR')
    OR (approved_by IS NOT NULL AND CAST(approved_by AS TEXT) = 'ADMINISTRATOR')
    OR (authorized_by IS NOT NULL AND CAST(authorized_by AS TEXT) = 'ADMINISTRATOR')
    OR (posted_by IS NOT NULL AND CAST(posted_by AS TEXT) = 'ADMINISTRATOR');

-- Step 2: Clean up any other non-numeric values in user ID fields
UPDATE account_payment SET 
    create_uid = NULL 
WHERE create_uid IS NOT NULL AND CAST(create_uid AS TEXT) NOT LIKE '[0-9]%';

UPDATE account_payment SET 
    write_uid = NULL 
WHERE write_uid IS NOT NULL AND CAST(write_uid AS TEXT) NOT LIKE '[0-9]%';

-- Step 3: Clean up payment signatory fields if they exist
UPDATE payment_signatory SET 
    user_id = NULL,
    create_uid = NULL,
    write_uid = NULL
WHERE 
    (user_id IS NOT NULL AND CAST(user_id AS TEXT) = 'ADMINISTRATOR')
    OR (create_uid IS NOT NULL AND CAST(create_uid AS TEXT) NOT LIKE '[0-9]%')
    OR (write_uid IS NOT NULL AND CAST(write_uid AS TEXT) NOT LIKE '[0-9]%');

-- Step 4: Verification - Check if cleanup was successful
-- Run this query to verify no 'ADMINISTRATOR' strings remain in ID fields
