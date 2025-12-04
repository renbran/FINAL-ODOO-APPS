#!/bin/bash
# Force upgrade commission_ax module on CloudPepper
# This will properly register the new commission_lines_count field

set -e

SERVER="root@139.84.163.11"
PORT="22"
DB_NAME="erposus"  # Change to 'osusproperties' if needed

echo "========================================"
echo "Force Upgrade commission_ax Module"
echo "========================================"
echo ""
echo "Target: $DB_NAME database"
echo ""

# Method 1: Using Odoo CLI (preferred)
echo "Attempting CLI upgrade..."
ssh -p $PORT $SERVER "cd /var/odoo/osusproperties && sudo -u odoo timeout 120 python3 src/odoo-bin -c odoo.conf -d $DB_NAME -u commission_ax --stop-after-init --log-level=info 2>&1 | tail -50"

if [ $? -eq 0 ]; then
    echo "✅ Module upgraded successfully via CLI"
else
    echo "⚠️  CLI upgrade had issues, trying alternative method..."
    
    # Method 2: Force module update via SQL
    echo ""
    echo "Forcing module state update..."
    ssh -p $PORT $SERVER "sudo -u postgres psql -d $DB_NAME -c \"UPDATE ir_module_module SET state='to upgrade' WHERE name='commission_ax';\""
    
    echo "Restarting Odoo to trigger upgrade..."
    ssh -p $PORT $SERVER "sudo systemctl restart odoo"
    
    echo "✅ Module marked for upgrade, restart initiated"
    echo ""
    echo "Note: The upgrade will complete when Odoo starts"
    echo "Check the logs: ssh -p $PORT $SERVER 'tail -f /var/log/odoo/odoo.log'"
fi

echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Wait 30 seconds for Odoo to fully start"
echo "2. Clear browser cache (Ctrl+Shift+R)"
echo "3. Login to https://erposus.com"
echo "4. Test: Sales → Orders (should work without RPC errors)"
echo ""
echo "If still having issues, manually upgrade via UI:"
echo "Settings → Apps → Search 'commission' → Click Upgrade"
