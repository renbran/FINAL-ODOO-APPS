#!/bin/bash
# CloudPepper Emergency Group Cleanup and Module Fix Script
# This script resolves the duplicate security group constraint violation

echo "=== CloudPepper Emergency Group Cleanup Started ==="
echo "Timestamp: $(date)"

# Step 1: First clean up the conflicting groups in the database
echo "Step 1: Cleaning up conflicting security groups..."

# Connect to CloudPepper database and run cleanup
# Note: This would typically be run through CloudPepper's database interface
cat << 'EOF' > /tmp/cleanup_groups.sql
-- Remove user-group relationships for conflicting groups
DELETE FROM res_groups_users_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE name LIKE '%Payment Voucher%'
);

-- Remove implied group relationships
DELETE FROM res_groups_implied_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE name LIKE '%Payment Voucher%'
) OR hid IN (
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

-- Clean up model data references
DELETE FROM ir_model_data WHERE model = 'res.groups' AND name LIKE '%payment_voucher%';
DELETE FROM ir_model_data WHERE model = 'ir.model.access' AND name LIKE '%payment_voucher%';
DELETE FROM ir_model_data WHERE model = 'ir.rule' AND name LIKE '%payment_voucher%';

-- Clean up any module data for account_payment_approval
UPDATE ir_model_data SET module = 'to_remove' WHERE module = 'account_payment_approval';
DELETE FROM ir_model_data WHERE module = 'to_remove';
EOF

echo "Database cleanup script created at /tmp/cleanup_groups.sql"

# Step 2: Show the manual steps needed
echo ""
echo "=== MANUAL STEPS REQUIRED ON CLOUDPEPPER ==="
echo ""
echo "1. Execute the database cleanup script:"
echo "   - Log into CloudPepper database admin"
echo "   - Run the SQL script: /tmp/cleanup_groups.sql"
echo "   - OR copy and paste the SQL commands from cloudpepper_group_cleanup.sql"
echo ""
echo "2. Clear CloudPepper cache:"
echo "   - Restart the Odoo instance"
echo "   - OR clear all caches through CloudPepper admin"
echo ""
echo "3. Reinstall the module:"
echo "   - Go to Apps menu"
echo "   - Search for 'Enhanced Payment Voucher System - OSUS'"
echo "   - Click Install (it should work now with unique group names)"
echo ""

# Step 3: Verify our module files are correct
echo "Step 3: Verifying module files..."

# Check that our security file has unique names
if grep -q "OSUS Payment Voucher" account_payment_approval/security/payment_voucher_security.xml; then
    echo "✓ Security groups have unique OSUS prefixes"
else
    echo "✗ ERROR: Security groups still have generic names"
    exit 1
fi

# Check manifest file
if [ -f "account_payment_approval/__manifest__.py" ]; then
    echo "✓ Manifest file exists"
else
    echo "✗ ERROR: Manifest file missing"
    exit 1
fi

echo ""
echo "=== SOLUTION SUMMARY ==="
echo "✓ Fixed duplicate group names by adding 'OSUS' prefix"
echo "✓ Created database cleanup script"
echo "✓ Module files are ready for installation"
echo ""
echo "The error 'duplicate key value violates unique constraint res_groups_name_uniq'"
echo "was caused by generic group names like 'Payment Voucher User' conflicting"
echo "with existing groups in the CloudPepper database."
echo ""
echo "NEXT STEPS:"
echo "1. Run the database cleanup SQL script on CloudPepper"
echo "2. Restart CloudPepper Odoo instance"
echo "3. Install the module - it should work now!"
echo ""
echo "=== CloudPepper Emergency Fix Completed ==="
