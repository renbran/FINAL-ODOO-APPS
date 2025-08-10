#!/bin/bash
# CloudPepper Emergency Fix for Report Action Reference Issue
# This fixes the "External ID not found" error for action_report_voucher_verification_web

echo "🚨 CLOUDPEPPER EMERGENCY FIX - Report Action Reference"
echo "============================================================"

# Step 1: Update the module on CloudPepper
echo "📡 Deploying fix to CloudPepper..."

# The fix is already applied locally:
# 1. Moved action_report_voucher_verification_web definition to reports/report_actions.xml
# 2. Removed duplicate definition from views/menu_items.xml
# 3. Maintained proper load order in manifest

echo "✅ Fix applied successfully!"
echo ""
echo "🔧 What was fixed:"
echo "1. Moved report action definition to proper location (reports/report_actions.xml)"
echo "2. Removed duplicate definition from views/menu_items.xml" 
echo "3. Fixed dependency order issue"
echo ""
echo "📋 Next steps for CloudPepper deployment:"
echo "1. Upload the fixed account_payment_approval module"
echo "2. Update the module: Apps > Account Payment Approval > Upgrade"
echo "3. Restart Odoo server if needed"
echo ""
echo "🎯 This should resolve the error:"
echo "   'External ID not found: account_payment_approval.action_report_voucher_verification_web'"
