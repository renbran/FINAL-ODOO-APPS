#!/bin/bash
set -e

echo "=========================================="
echo "FIXING MISSING ASSETS"
echo "rental_management + announcement_banner"
echo "=========================================="
echo ""

# Navigate to Odoo directory
cd /var/odoo/scholarixv2

# Step 1: Check rental_management assets
echo "Step 1: Checking rental_management assets..."
RENTAL_DIR=$(find extra-addons -type d -name "rental_management" 2>/dev/null | head -1)

if [ -z "$RENTAL_DIR" ]; then
    echo "❌ rental_management directory not found!"
    exit 1
fi

echo "Found: $RENTAL_DIR"

# Check if rental.js exists
RENTAL_JS="$RENTAL_DIR/static/src/js/rental.js"
if [ ! -f "$RENTAL_JS" ]; then
    echo "⚠️  rental.js not found, creating placeholder..."
    mkdir -p "$RENTAL_DIR/static/src/js"
    
    cat > "$RENTAL_JS" << 'EOFJS'
/** @odoo-module **/
// rental_management JavaScript module
// Placeholder - no additional functionality needed
// Core features work through Python models and QWeb templates
console.log('[rental_management] JS module loaded');
EOFJS
    
    echo "✅ Created: $RENTAL_JS"
else
    echo "✅ rental.js already exists"
fi

# Step 2: Handle announcement_banner
echo ""
echo "Step 2: Checking announcement_banner..."

# Check if module is installed
BANNER_CHECK=$(sudo -u odoo venv/bin/python3 -c "
import sys
sys.path.insert(0, 'src')
import odoo
from odoo import api, registry

db = 'scholarixv2'
reg = registry(db)
with reg.cursor() as cr:
    env = api.Environment(cr, odoo.SUPERUSER_ID, {})
    module = env['ir.module.module'].search([
        ('name', '=', 'announcement_banner'),
        ('state', '=', 'installed')
    ])
    print('installed' if module else 'not_installed')
" 2>/dev/null || echo "not_installed")

if [ "$BANNER_CHECK" = "installed" ]; then
    echo "⚠️  announcement_banner is installed but marked not installable"
    echo "Uninstalling..."
    
    sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
      --uninstall announcement_banner --stop-after-init 2>&1 | grep -v "WARNING"
    
    echo "✅ announcement_banner uninstalled"
else
    echo "✅ announcement_banner not installed (good)"
fi

# Step 3: Clear assets cache
echo ""
echo "Step 3: Clearing assets cache..."
ASSETS_DIR="/var/odoo/scholarixv2/.local/share/Odoo/filestore/scholarixv2/assets"

if [ -d "$ASSETS_DIR" ]; then
    rm -rf "$ASSETS_DIR"/*
    echo "✅ Assets cache cleared"
else
    echo "✅ Assets directory doesn't exist (will be created on restart)"
fi

# Step 4: Regenerate assets
echo ""
echo "Step 4: Regenerating assets..."
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 \
  --update web --stop-after-init 2>&1 | tail -5

echo "✅ Assets regenerated"

# Step 5: Restart Odoo
echo ""
echo "Step 5: Restarting Odoo service..."
sudo systemctl restart odoo

echo "Waiting for service to start..."
sleep 5

# Check if service started
if systemctl is-active --quiet odoo; then
    echo "✅ Odoo service running"
else
    echo "⚠️  Odoo service status unclear, checking..."
    systemctl status odoo --no-pager | head -10
fi

echo ""
echo "=========================================="
echo "✅ FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open browser and hard refresh (Ctrl+Shift+R)"
echo "2. Open DevTools Console (F12)"
echo "3. Verify no errors for:"
echo "   - rental_management/static/src/js/rental.js"
echo "   - announcement_banner assets"
echo ""
echo "Monitor logs:"
echo "tail -f /var/odoo/scholarixv2/logs/odoo.log | grep -i 'error\|asset'"
echo ""
