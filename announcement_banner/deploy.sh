#!/bin/bash
# Deployment script for scholarixv2 - announcement_banner module fix

echo "======================================================================"
echo "🚀 Deploying announcement_banner fix to scholarixv2"
echo "======================================================================"
echo ""

# Configuration
REMOTE_HOST="root@139.84.163.11"
REMOTE_PORT="22"
SSH_KEY="$HOME/.ssh/odoo17_cloudpepper_new"
ODOO_PATH="/var/odoo/scholarixv2"
MODULE_NAME="announcement_banner"
DB_NAME="scholarixv2"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📝 Step 1: Backing up current module on remote server..."
ssh -i "$SSH_KEY" -p $REMOTE_PORT $REMOTE_HOST << 'ENDSSH'
cd /var/odoo/scholarixv2
if [ -d "addons/announcement_banner" ]; then
    BACKUP_NAME="announcement_banner.backup.$(date +%Y%m%d_%H%M%S)"
    sudo -u odoo cp -r addons/announcement_banner "addons/$BACKUP_NAME"
    echo "✅ Backup created: addons/$BACKUP_NAME"
else
    echo "⚠️  Module directory not found, skipping backup"
fi
ENDSSH

echo ""
echo "📤 Step 2: Uploading module to remote server..."
scp -i "$SSH_KEY" -P $REMOTE_PORT -r "../announcement_banner" "${REMOTE_HOST}:/tmp/"

echo ""
echo "📦 Step 3: Installing module on remote server..."
ssh -i "$SSH_KEY" -p $REMOTE_PORT $REMOTE_HOST << 'ENDSSH'
cd /var/odoo/scholarixv2

# Move module to addons directory
sudo rm -rf addons/announcement_banner
sudo mv /tmp/announcement_banner addons/
sudo chown -R odoo:odoo addons/announcement_banner

echo "✅ Module files updated"
ENDSSH

echo ""
echo "🔄 Step 4: Updating module in database..."
ssh -i "$SSH_KEY" -p $REMOTE_PORT $REMOTE_HOST << 'ENDSSH'
cd /var/odoo/scholarixv2

# Update module
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u announcement_banner --stop-after-init

if [ $? -eq 0 ]; then
    echo "✅ Module updated successfully"
else
    echo "❌ Module update failed"
    exit 1
fi
ENDSSH

echo ""
echo "🔁 Step 5: Restarting Odoo service..."
ssh -i "$SSH_KEY" -p $REMOTE_PORT $REMOTE_HOST << 'ENDSSH'
# Check if systemctl is available
if command -v systemctl &> /dev/null; then
    sudo systemctl restart odoo
    echo "✅ Odoo service restarted via systemctl"
else
    # Try alternative restart methods
    if [ -f "/etc/init.d/odoo" ]; then
        sudo /etc/init.d/odoo restart
        echo "✅ Odoo service restarted via init.d"
    else
        echo "⚠️  Please restart Odoo manually"
    fi
fi
ENDSSH

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "======================================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Clear browser cache (Ctrl+Shift+Delete)"
echo "2. Login to scholarixv2 database"
echo "3. Open browser console (F12)"
echo "4. Check for any console errors"
echo "5. Test announcement banner functionality"
echo ""
echo "======================================================================"
