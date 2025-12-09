#!/bin/bash
# ============================================================================
# QUICK FIX: Clear Asset Cache & Sessions
# Run this to fix browser console errors (138 errors issue)
# ============================================================================

echo "=== ODOO 17 QUICK FIX: Asset Cache Cleanup ==="
echo ""

# Stop Odoo
echo "[1/5] Stopping Odoo service..."
systemctl stop odoo
sleep 2

# Clear old sessions
echo "[2/5] Clearing stale sessions..."
find /var/odoo/.local/share/Odoo/filestore/scholarixv2/sessions -type f -mtime +1 -delete 2>/dev/null
find /var/odoo/.local/share/Odoo/filestore/scholarixv2/sessions -type d -empty -delete 2>/dev/null

# Clear asset cache from database
echo "[3/5] Clearing asset cache from database..."
psql -U odoo -d scholarixv2 -c "DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';"

# Clear filestore assets
echo "[4/5] Clearing filestore assets..."
rm -rf /var/odoo/.local/share/Odoo/filestore/scholarixv2/assets/* 2>/dev/null

# Restart Odoo
echo "[5/5] Starting Odoo service..."
systemctl start odoo
sleep 3

# Verify
if systemctl is-active --quiet odoo; then
    echo ""
    echo "✅ SUCCESS! Odoo is running."
    echo ""
    echo "IMPORTANT: Tell users to:"
    echo "  1. Press Ctrl+Shift+Delete to clear browser cache"
    echo "  2. Press Ctrl+Shift+R to hard refresh"
    echo ""
else
    echo ""
    echo "❌ ERROR: Odoo failed to start!"
    echo "Check logs: journalctl -u odoo -f"
fi
