#!/bin/bash
# ============================================
# SIMPLE MODULE APPLICATION SCRIPT
# ============================================

echo "🚀 Applying Custom Modules to Database"
echo "======================================"

DATABASE_NAME=${1:-propertyosus}
MODULES=${2:-"report_xlsx,osus_dashboard,hrms_dashboard"}

echo "📋 Database: $DATABASE_NAME"
echo "📦 Modules: $MODULES"
echo ""

echo "🔄 Step 1: Restarting Odoo stack..."
docker-compose restart

echo "⏳ Step 2: Waiting for services to be ready..."
sleep 20

echo "💾 Step 3: Registering modules in database..."
# Register modules in the database so they appear in Apps
IFS=',' read -ra MODULE_ARRAY <<< "$MODULES"
for module in "${MODULE_ARRAY[@]}"; do
    module=$(echo "$module" | xargs)  # trim whitespace
    echo "  🔸 Registering: $module"
    
    # Insert/Update module record
    docker exec odoo17_final-db-1 psql -U odoo -d $DATABASE_NAME -c \
        "INSERT INTO ir_module_module (name, state, author, website, summary, description, category_id, auto_install, application) 
         VALUES ('$module', 'uninstalled', 'Custom', '', 'Custom Module: $module', 'Custom Module: $module', 1, false, true) 
         ON CONFLICT (name) DO UPDATE SET 
         state = 'uninstalled', 
         author = 'Custom',
         summary = 'Custom Module: $module',
         description = 'Custom Module: $module',
         application = true;"
done

echo "📱 Step 4: Scanning for module files..."
# Update module path scan
docker exec odoo17_final-odoo-1 ls -la /mnt/extra-addons/ | head -20

echo "✅ MODULE APPLICATION COMPLETE!"
echo "==============================="
echo "🌐 Access: http://localhost:8069/web?db=$DATABASE_NAME"
echo ""
echo "💡 Next steps:"
echo "   1. Go to Apps menu"
echo "   2. Click 'Update Apps List' button"
echo "   3. Search for your modules:"
for module in "${MODULE_ARRAY[@]}"; do
    module=$(echo "$module" | xargs)
    echo "      - $module"
done
echo "   4. Click 'Install' on each module"
echo ""
echo "🔧 If modules don't appear, they may need dependencies installed first:"
echo "   - report_xlsx requires: base"
echo "   - osus_dashboard requires: report_xlsx, report_pdf_options"
echo "   - hrms_dashboard requires: hr, report_xlsx"
