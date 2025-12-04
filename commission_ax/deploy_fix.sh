#!/bin/bash
# Deploy commission_ax bugfix to CloudPepper
# Fixes: Missing field commission_lines_count

set -e  # Exit on error

echo "========================================"
echo "Commission AX Module Deployment"
echo "========================================"
echo ""

# Configuration
SERVER="root@139.84.163.11"
PORT="22"
REMOTE_PATH="/var/odoo/osusproperties/extra-addons/commission_ax"
LOCAL_PATH="."

echo "Target Server: $SERVER"
echo "Module Path: $REMOTE_PATH"
echo ""

# Step 1: Backup current module on server
echo "Step 1: Creating backup on server..."
ssh -p $PORT $SERVER "cd $REMOTE_PATH/.. && cp -r commission_ax commission_ax.backup_$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup created"
echo ""

# Step 2: Upload modified files
echo "Step 2: Uploading modified files..."
scp -P $PORT models/sale_order.py $SERVER:$REMOTE_PATH/models/
echo "✅ Files uploaded"
echo ""

# Step 3: Restart Odoo service
echo "Step 3: Updating module in Odoo..."
ssh -p $PORT $SERVER "sudo systemctl stop odoo && sleep 2"
echo "  - Odoo stopped"

ssh -p $PORT $SERVER "cd /var/odoo/osusproperties && ./odoo-bin -u commission_ax --stop-after-init -d odoo 2>&1 | tail -n 20"
echo "  - Module upgraded"

ssh -p $PORT $SERVER "sudo systemctl start odoo && sleep 3"
echo "  - Odoo started"
echo ""

# Step 4: Verify deployment
echo "Step 4: Verifying deployment..."
ssh -p $PORT $SERVER "sudo systemctl status odoo | head -n 10"
echo ""

echo "========================================"
echo "✅ Deployment Complete"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Check logs: ssh -p $PORT $SERVER 'tail -f /var/log/odoo/odoo.log'"
echo "2. Test in browser: Navigate to Sales → Orders"
echo "3. Verify no RPC errors when viewing sale orders"
echo ""
