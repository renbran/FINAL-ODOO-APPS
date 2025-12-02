#!/bin/bash
#############################################################################
# Fix Rental Management Module Deployment Script
# Resolves field validation errors on scholarixv2
#############################################################################

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     RENTAL MANAGEMENT MODULE FIX - scholarixv2               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
ODOO_USER="odoo"
ODOO_DB="scholarixv2"
ODOO_PATH="/opt/odoo/odoo-bin"
ADDONS_PATH="/var/odoo/scholarixv2"
MODULE_NAME="rental_management"

echo "📋 Step 1: Stopping Odoo service..."
sudo systemctl stop odoo || true

echo ""
echo "📋 Step 2: Backing up database..."
sudo -u postgres pg_dump "$ODOO_DB" > "/tmp/${ODOO_DB}_backup_$(date +%Y%m%d_%H%M%S).sql"
echo "✓ Backup created in /tmp/"

echo ""
echo "📋 Step 3: Clearing invalid views from database..."
sudo -u postgres psql -d "$ODOO_DB" <<EOF
-- Delete invalid custom views that reference non-existent fields
DELETE FROM ir_ui_view 
WHERE id IN (
    SELECT v.id 
    FROM ir_ui_view v 
    WHERE v.arch_db LIKE '%is_payment_plan%' 
    AND v.model = 'property.details'
    AND NOT EXISTS (
        SELECT 1 FROM ir_model_fields 
        WHERE model = 'property.details' 
        AND name = 'is_payment_plan'
    )
);

DELETE FROM ir_ui_view 
WHERE id IN (
    SELECT v.id 
    FROM ir_ui_view v 
    WHERE v.arch_db LIKE '%<field name="name"%' 
    AND v.model = 'property.tag'
    AND v.arch_db NOT LIKE '%compute=%'
);

-- Clear view cache
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view';

-- Vacuum the database
VACUUM ANALYZE;
EOF

echo "✓ Invalid views cleared"

echo ""
echo "📋 Step 4: Updating rental_management module..."
sudo -u "$ODOO_USER" "$ODOO_PATH" \
    -d "$ODOO_DB" \
    --addons-path="$ADDONS_PATH" \
    -u "$MODULE_NAME" \
    --stop-after-init \
    --log-level=warn

echo "✓ Module updated"

echo ""
echo "📋 Step 5: Starting Odoo service..."
sudo systemctl start odoo

echo ""
echo "📋 Step 6: Waiting for service to be ready..."
sleep 5

# Check service status
if sudo systemctl is-active --quiet odoo; then
    echo "✓ Odoo service is running"
else
    echo "⚠ Warning: Odoo service may not have started properly"
    echo "Check logs: sudo journalctl -u odoo -n 50"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    FIX COMPLETED                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Next Steps:"
echo "   1. Check Odoo logs: sudo tail -f /var/log/odoo/odoo.log"
echo "   2. Test the Property Dashboard: https://scholarixglobal.com"
echo "   3. Clear browser cache if needed"
echo ""
echo "🔄 If errors persist, run:"
echo "   sudo -u odoo $ODOO_PATH -d $ODOO_DB -u $MODULE_NAME --stop-after-init"
echo ""
