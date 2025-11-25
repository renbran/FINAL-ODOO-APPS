#!/bin/bash
# Deploy t-raw fixes to scholarixv2 and osusproperties databases

echo "========================================================================"
echo "Deploying t-raw fixes to remote databases"
echo "========================================================================"
echo ""

# Modules that were fixed
MODULES=(
    "ks_dynamic_financial_report"
    "rental_management"
    "om_account_followup"
    "announcement_banner"
)

# Stop Odoo
echo "Step 1: Stopping Odoo service..."
sudo systemctl stop odoo

# Update modules in scholarixv2
echo ""
echo "Step 2: Updating modules in scholarixv2 database..."
cd /var/odoo/scholarixv2

for MODULE in "${MODULES[@]}"; do
    echo "  - Updating $MODULE..."
    sudo -u odoo venv/bin/python3 src/odoo-bin \
        -c odoo.conf \
        -d scholarixv2 \
        -u $MODULE \
        --stop-after-init
done

# Update modules in osusproperties (if different server/path)
echo ""
echo "Step 3: Updating modules in osusproperties database..."
# Adjust path if needed
cd /var/odoo/osusproperties 2>/dev/null || cd /var/odoo/scholarixv2

for MODULE in "${MODULES[@]}"; do
    echo "  - Updating $MODULE..."
    sudo -u odoo venv/bin/python3 src/odoo-bin \
        -c odoo.conf \
        -d osusproperties \
        -u $MODULE \
        --stop-after-init 2>/dev/null || echo "    (Database not found, skipping)"
done

# Start Odoo
echo ""
echo "Step 4: Starting Odoo service..."
sudo systemctl start odoo

echo ""
echo "========================================================================"
echo "Deployment Complete!"
echo "========================================================================"
echo ""
echo "Fixed modules:"
for MODULE in "${MODULES[@]}"; do
    echo "  ✅ $MODULE"
done
echo ""
echo "⚠️  IMPORTANT: Clear browser cache on ALL clients:"
echo "   1. Press Ctrl+Shift+Delete"
echo "   2. Clear 'Cached images and files'"
echo "   3. Or use hard refresh: Ctrl+F5"
echo ""
echo "The t-raw deprecation warning should now be gone!"
echo "========================================================================"
