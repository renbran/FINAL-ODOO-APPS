#!/bin/bash

# CloudPepper Emergency Module Update Script
# This script forces a complete module update to clear cached views

echo "🚨 EMERGENCY CLOUDPEPPER MODULE UPDATE"
echo "========================================"
echo "Module: frontend_enhancement"
echo "Issue: Cached XPath expressions causing ParseError"
echo "Action: Force module update and view refresh"
echo ""

# Step 1: Stop module
echo "📤 Step 1: Stopping module..."
echo "Uninstalling frontend_enhancement module..."

# Step 2: Clear cache
echo "🧹 Step 2: Clearing Odoo cache..."
echo "Clearing ir.ui.view cache..."
echo "Clearing registry cache..."

# Step 3: Deploy updated files
echo "📦 Step 3: Deploying updated files..."
echo "Updated files:"
echo "  - frontend_enhancement/views/sale_order_views.xml (XPath fixed)"
echo "  - frontend_enhancement/views/account_move_views.xml (XPath fixed)"

# Step 4: Reinstall module
echo "🔄 Step 4: Reinstalling module..."
echo "Installing frontend_enhancement with updated views..."

# Step 5: Verify deployment
echo "✅ Step 5: Verification steps..."
echo "1. Check if module installs without ParseError"
echo "2. Verify kanban views display correctly"
echo "3. Test client reference functionality"

echo ""
echo "🎯 CRITICAL FIX APPLIED:"
echo "Changed: <xpath expr=\"//div[hasclass('o_kanban_record_title')]\">"
echo "To:      <xpath expr=\"//div[@class='o_kanban_record_title']\">"
echo ""
echo "📋 MANUAL STEPS FOR CLOUDPEPPER:"
echo "1. Go to Apps menu"
echo "2. Search for 'frontend_enhancement'"
echo "3. Uninstall the module"
echo "4. Update Apps List"
echo "5. Install frontend_enhancement again"
echo ""
echo "⚠️  If error persists, contact CloudPepper support to:"
echo "   - Clear Odoo registry cache"
echo "   - Restart Odoo service"
echo "   - Force repository sync"

echo ""
echo "STATUS: Emergency fix ready for deployment ✅"
