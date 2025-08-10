#!/bin/bash
# CloudPepper Nuclear Module Reset Script
# Use this when all else fails

echo "🚨 CLOUDPEPPER NUCLEAR MODULE RESET"
echo "=================================="

# Step 1: SSH into CloudPepper server
echo "1. SSH into CloudPepper server:"
echo "   ssh root@your-cloudpepper-server"

# Step 2: Stop Odoo service
echo ""
echo "2. Stop Odoo service:"
echo "   systemctl stop odoo"

# Step 3: Clear module cache
echo ""
echo "3. Clear module cache:"
echo "   rm -rf /var/odoo/stagingtry/src/odoo/addons/account_payment_approval"
echo "   rm -rf /var/odoo/stagingtry/extra-addons/odoo17_final.git-*/account_payment_approval"

# Step 4: Database cleanup
echo ""
echo "4. Run database cleanup:"
echo "   sudo -u postgres psql stagingtry"
echo "   DELETE FROM ir_model_data WHERE module = 'account_payment_approval';"
echo "   DELETE FROM ir_module_module WHERE name = 'account_payment_approval';"
echo "   \\q"

# Step 5: Upload clean module
echo ""
echo "5. Upload the FIXED module (with commented out button):"
echo "   Upload the account_payment_approval folder to extra-addons"

# Step 6: Restart Odoo
echo ""
echo "6. Start Odoo service:"
echo "   systemctl start odoo"

# Step 7: Install module
echo ""
echo "7. Install module via web interface:"
echo "   Apps > Update Apps List > Install account_payment_approval"

echo ""
echo "🎯 This will completely reset the module and install the fixed version."
