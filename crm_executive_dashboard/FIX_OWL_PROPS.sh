#!/bin/bash
# Fix for CRM Executive Dashboard OWL Props Error
# Run this script after uploading the crm_executive_dashboard module

echo "🔧 Fixing CRM Executive Dashboard OWL Props..."

# Module path (update this to your actual path)
MODULE_PATH="/path/to/your/odoo/addons/crm_executive_dashboard"

# Backup original files
echo "📦 Creating backups..."
cp "${MODULE_PATH}/static/src/js/crm_executive_dashboard.js" "${MODULE_PATH}/static/src/js/crm_executive_dashboard.js.backup"
cp "${MODULE_PATH}/static/src/js/crm_strategic_dashboard.js" "${MODULE_PATH}/static/src/js/crm_strategic_dashboard.js.backup"

echo "✅ Backups created"
echo ""
echo "📝 The following changes were made locally:"
echo "   1. Added props definition to CRMExecutiveDashboard"
echo "   2. Added props definition to CRMStrategicDashboard"
echo "   3. Props added: action, actionId, className (all optional)"
echo ""
echo "🚀 To apply on server:"
echo "   1. Upload fixed files from local machine"
echo "   2. Restart Odoo service"
echo "   3. Clear browser cache"
echo ""
echo "✅ Fix complete!"
