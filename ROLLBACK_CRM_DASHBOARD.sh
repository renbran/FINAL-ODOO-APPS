#!/bin/bash
# CRM Dashboard Rollback Script
# Date: November 28, 2025
# Purpose: Rollback crm_dashboard module if issues occur

echo "======================================"
echo "CRM Dashboard Rollback Procedure"
echo "======================================"
echo ""

# Configuration
MODULE_PATH="/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/crm_dashboard"
BACKUP_PATH="${MODULE_PATH}.backup_$(date +%Y%m%d)"
DB_NAME="osusproperties"

# Step 1: Stop Odoo service
echo "[1/6] Stopping Odoo service..."
systemctl stop odona-osusproperties.service
sleep 3

# Step 2: Backup current module (if not already backed up)
if [ ! -d "${BACKUP_PATH}" ]; then
    echo "[2/6] Creating backup of current module..."
    cp -r "$MODULE_PATH" "$BACKUP_PATH"
    echo "Backup created at: $BACKUP_PATH"
else
    echo "[2/6] Backup already exists, skipping..."
fi

# Step 3: Restore original XML template
echo "[3/6] Restoring original XML template..."
if [ -f "${MODULE_PATH}/static/src/xml/dashboard_templates.xml.backup" ]; then
    cp "${MODULE_PATH}/static/src/xml/dashboard_templates.xml.backup" \
       "${MODULE_PATH}/static/src/xml/dashboard_templates.xml"
    echo "Original template restored"
else
    echo "WARNING: No backup template found!"
fi

# Step 4: Remove modern CSS
echo "[4/6] Removing modern CSS..."
if [ -f "${MODULE_PATH}/static/src/css/dashboard_modern.css" ]; then
    rm "${MODULE_PATH}/static/src/css/dashboard_modern.css"
    echo "Modern CSS removed"
fi

# Step 5: Restore original manifest
echo "[5/6] Checking manifest..."
# Note: Manual verification needed if manifest was modified

# Step 6: Uninstall module from database
echo "[6/6] Uninstalling module from database..."
cd /var/odoo/osusproperties
/var/odoo/osusproperties/venv/bin/python3 src/odoo-bin \
    -c odoo.conf \
    -d "$DB_NAME" \
    -u crm_dashboard \
    --stop-after-init

# Step 7: Clear assets cache
echo "[7/7] Clearing assets cache..."
sudo -u postgres psql -d "$DB_NAME" -c "DELETE FROM ir_attachment WHERE name LIKE '%assets%' OR url LIKE '%/web/assets%';"

# Step 8: Restart service
echo "Restarting Odoo service..."
systemctl start odona-osusproperties.service
sleep 5

# Check service status
echo ""
echo "======================================"
echo "Service Status:"
systemctl status odona-osusproperties.service --no-pager | head -15
echo ""
echo "======================================"
echo "Rollback Complete!"
echo ""
echo "Backup location: $BACKUP_PATH"
echo "To completely remove module:"
echo "  1. Go to Apps menu in Odoo"
echo "  2. Remove 'Installed' filter"
echo "  3. Search 'CRM Dashboard'"
echo "  4. Click Uninstall"
echo "======================================"
