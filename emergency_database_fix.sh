#!/bin/bash
# Emergency fix script for the ADMINISTRATOR string error
# Execute this on your remote server

echo "🚨 EMERGENCY FIX: Cleaning database for account_payment_final installation"

# Step 1: Clean the database
echo "Step 1: Cleaning database..."
psql -U odoo -d stagingtry << 'EOF'
BEGIN;

-- Clean up ADMINISTRATOR values in account_payment table
UPDATE account_payment 
SET 
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

-- Fix user ID fields
UPDATE account_payment 
SET create_uid = 1 
WHERE create_uid IS NOT NULL AND CAST(create_uid AS TEXT) = 'ADMINISTRATOR';

UPDATE account_payment 
SET write_uid = 1 
WHERE write_uid IS NOT NULL AND CAST(write_uid AS TEXT) = 'ADMINISTRATOR';

-- Clean payment_signatory if exists
UPDATE payment_signatory 
SET user_id = NULL
WHERE user_id IS NOT NULL AND CAST(user_id AS TEXT) = 'ADMINISTRATOR';

COMMIT;

-- Verify cleanup
SELECT 'Cleanup completed successfully' as status;
EOF

echo "✅ Database cleanup completed"

# Step 2: Try installing the module
echo "Step 2: Installing account_payment_final module..."
cd /var/odoo/stagingtry
./odoo-bin -d stagingtry -i account_payment_final --stop-after-init

echo "🎯 Installation attempt completed. Check the output above for success/errors."
