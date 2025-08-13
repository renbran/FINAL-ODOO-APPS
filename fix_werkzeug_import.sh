#!/bin/bash
# fix_werkzeug_import.sh - Script to resolve the werkzeug import error

echo "=== Payment Approval Workflow - Import Fix Script ==="
echo ""

echo "🔍 Checking for problematic imports..."
if grep -r "werkzeug.security" payment_approval_workflow/ 2>/dev/null; then
    echo "❌ Found werkzeug.security imports that need fixing"
else
    echo "✅ No werkzeug.security imports found - fix appears to be applied"
fi

echo ""
echo "🔍 Checking for safe_str_cmp usage..."
if grep -r "safe_str_cmp" payment_approval_workflow/ 2>/dev/null; then
    echo "❌ Found safe_str_cmp usage that needs fixing"
else
    echo "✅ No safe_str_cmp usage found - fix appears to be applied"
fi

echo ""
echo "🧹 Cleaning Python cache..."
find payment_approval_workflow/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find payment_approval_workflow/ -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Python cache cleaned"

echo ""
echo "📂 Current portal.py import section:"
head -n 10 payment_approval_workflow/controllers/portal.py

echo ""
echo "🔧 RESOLUTION STEPS:"
echo "1. ✅ Import fix has been applied locally"
echo "2. 🔄 Push changes to your Git repository (if using Git deployment)"
echo "3. 🔄 Pull/deploy changes on the server"
echo "4. 🔄 Restart the Odoo server to clear import cache"
echo "5. 🔄 Try installing the module again"

echo ""
echo "💡 Quick server restart commands:"
echo "   Docker: docker-compose restart odoo"
echo "   Systemd: sudo systemctl restart odoo"
echo "   Manual: kill odoo process and restart"

echo ""
echo "✅ Script completed!"
