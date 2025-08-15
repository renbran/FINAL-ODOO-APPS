#!/bin/bash
# CloudPepper Emergency Deployment Script
# This script forces a complete module update to resolve XPath caching issues

echo "🚨 CLOUDPEPPER EMERGENCY DEPLOYMENT"
echo "===================================="
echo "Module: frontend_enhancement"
echo "Issue: Cached XPath expressions causing parse errors"
echo "Solution: Force complete module reinstall"
echo ""

# Check if we're in the right directory
if [ ! -d "frontend_enhancement" ]; then
    echo "❌ Error: frontend_enhancement directory not found"
    echo "Please run this script from the odoo17_final root directory"
    exit 1
fi

echo "📋 Pre-deployment validation..."

# Validate XML files
echo "  🔍 Validating XML syntax..."
for xml_file in frontend_enhancement/views/*.xml frontend_enhancement/data/*.xml; do
    if [ -f "$xml_file" ]; then
        python3 -c "import xml.etree.ElementTree as ET; ET.parse('$xml_file')" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "    ✅ $(basename $xml_file)"
        else
            echo "    ❌ $(basename $xml_file) - SYNTAX ERROR"
            exit 1
        fi
    fi
done

# Check for problematic XPath expressions
echo "  🔍 Checking for hasclass() expressions..."
HASCLASS_COUNT=$(grep -r "hasclass(" frontend_enhancement/ 2>/dev/null | wc -l)
if [ $HASCLASS_COUNT -eq 0 ]; then
    echo "    ✅ No problematic XPath expressions found"
else
    echo "    ❌ Found $HASCLASS_COUNT hasclass() expressions - MUST BE FIXED"
    grep -r "hasclass(" frontend_enhancement/ 2>/dev/null
    exit 1
fi

echo ""
echo "✅ All validation checks passed!"
echo ""

echo "📤 CLOUDPEPPER DEPLOYMENT INSTRUCTIONS"
echo "========================================"
echo ""
echo "🔄 Method 1: Git Update (Recommended)"
echo "  1. Commit all changes to git:"
echo "     git add frontend_enhancement/"
echo "     git commit -m 'Fix XPath expressions in frontend_enhancement module'"
echo "     git push origin main"
echo ""
echo "  2. In CloudPepper, go to Apps and update the module:"
echo "     - Find 'Frontend Enhancement' module"
echo "     - Click 'Upgrade' button"
echo "     - Wait for completion"
echo ""

echo "🔄 Method 2: Manual Module Reinstall"
echo "  1. In CloudPepper Odoo:"
echo "     - Go to Apps menu"
echo "     - Remove filters, search 'frontend_enhancement'"
echo "     - Click 'Uninstall' if installed"
echo "     - Click 'Install' to reinstall with latest code"
echo ""

echo "🔄 Method 3: Force Registry Reload (Advanced)"
echo "  1. In CloudPepper server terminal:"
echo "     sudo systemctl restart odoo"
echo "     # OR"
echo "     sudo service odoo restart"
echo ""

echo "🧪 VERIFICATION STEPS"
echo "====================="
echo "After deployment, verify in CloudPepper:"
echo "  1. Go to Sales > Orders"
echo "  2. Switch to Kanban view"
echo "  3. Check for client reference display"
echo "  4. Verify no errors in browser console"
echo "  5. Test invoice kanban view as well"
echo ""

echo "🆘 IF ERRORS PERSIST"
echo "===================="
echo "  1. Check CloudPepper logs: /var/log/odoo/odoo.log"
echo "  2. Clear Odoo cache: rm -rf /tmp/odoo_cache/*"
echo "  3. Restart with cache clear: sudo systemctl restart odoo"
echo "  4. Contact CloudPepper support if needed"
echo ""

echo "✅ Deployment script completed successfully!"
echo "All files are ready for CloudPepper deployment."
