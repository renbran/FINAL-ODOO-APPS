#!/bin/bash
# Quick fix deployment for OSUS Premium settings page issue
# Run this on CloudPepper server to apply the fixes

echo "🔧 OSUS Premium Settings Page Fix Deployment"
echo "============================================="
echo ""

# Set variables
MODULE_NAME="osus_premium"
ODOO_PATH="/opt/odoo17/odoo17_final"
MODULE_PATH="$ODOO_PATH/$MODULE_NAME"

# Check if running as odoo user
if [ "$USER" != "odoo" ]; then
    echo "⚠️  Please run as odoo user: sudo -u odoo bash $0"
    exit 1
fi

# Navigate to Odoo directory
cd "$ODOO_PATH" || exit 1

echo "📦 Pulling latest changes from git..."
git pull origin main

echo ""
echo "🔄 Upgrading module: $MODULE_NAME"
/opt/odoo17/venv/bin/python3 /opt/odoo17/odoo/odoo-bin \
    -c /etc/odoo17.conf \
    -d odoo \
    -u "$MODULE_NAME" \
    --stop-after-init

echo ""
echo "🧹 Clearing browser cache instructions:"
echo "1. In browser, press Ctrl+Shift+R (hard refresh)"
echo "2. Or clear browser cache completely"
echo "3. Go to Settings page: https://erposus.com/web#action=84&model=res.config.settings&view_type=form"
echo ""
echo "✅ Deployment complete! The 'Toggle Dropdown' button should now be hidden."
echo ""
echo "🔍 What was fixed:"
echo "   - Added osus_settings.scss for proper settings page styling"
echo "   - Added settings_fixes.js to remove rogue toggle buttons"
echo "   - Improved settings page layout with OSUS branding"
echo ""
