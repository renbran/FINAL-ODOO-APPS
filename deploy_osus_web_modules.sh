#!/bin/bash
# OSUS Properties Web Modules Deployment Script
# Version: 1.0
# Date: November 25, 2025

echo "=================================================="
echo "OSUS Properties Web Modules Deployment"
echo "=================================================="
echo ""

# Configuration
SSH_KEY="$HOME/.ssh/odoo17_cloudpepper_new"
SSH_HOST="root@139.84.163.11"
SSH_PORT="22"
ODOO_PATH="/var/odoo/scholarixv2"
DATABASE="scholarixv2"
MODULES="muk_web_colors,muk_web_theme,muk_web_chatter,muk_web_dialog"

echo "Target: https://stagingtry.cloudpepper.site/"
echo "Modules: $MODULES"
echo ""

# Confirm deployment
read -p "Are you sure you want to deploy? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "Step 1/5: Stopping Odoo service..."
ssh -i "$SSH_KEY" "$SSH_HOST" -p "$SSH_PORT" "sudo systemctl stop odoo"
if [ $? -eq 0 ]; then
    echo "✅ Odoo stopped successfully"
else
    echo "❌ Failed to stop Odoo"
    exit 1
fi

echo ""
echo "Step 2/5: Creating backup..."
ssh -i "$SSH_KEY" "$SSH_HOST" -p "$SSH_PORT" "cd $ODOO_PATH && sudo -u odoo tar -czf backups/modules_backup_$(date +%Y%m%d_%H%M%S).tar.gz addons/muk_web_*"
if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully"
else
    echo "⚠️ Backup creation failed (continuing anyway)"
fi

echo ""
echo "Step 3/5: Updating modules..."
ssh -i "$SSH_KEY" "$SSH_HOST" -p "$SSH_PORT" "cd $ODOO_PATH && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d $DATABASE -u $MODULES --stop-after-init"
if [ $? -eq 0 ]; then
    echo "✅ Modules updated successfully"
else
    echo "❌ Module update failed"
    echo "Rolling back..."
    ssh -i "$SSH_KEY" "$SSH_HOST" -p "$SSH_PORT" "sudo systemctl start odoo"
    exit 1
fi

echo ""
echo "Step 4/5: Starting Odoo service..."
ssh -i "$SSH_KEY" "$SSH_HOST" -p "$SSH_PORT" "sudo systemctl start odoo"
if [ $? -eq 0 ]; then
    echo "✅ Odoo started successfully"
else
    echo "❌ Failed to start Odoo"
    exit 1
fi

echo ""
echo "Step 5/5: Verifying deployment..."
sleep 5
ssh -i "$SSH_KEY" "$SSH_HOST" -p "$SSH_PORT" "sudo systemctl status odoo --no-pager | head -n 10"

echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "Please verify:"
echo "1. Access: https://stagingtry.cloudpepper.site/"
echo "2. Clear browser cache (Ctrl+F5)"
echo "3. Check navbar is maroon with gold border"
echo "4. Verify apps menu shows OSUS colors"
echo "5. Test chatter and dialog functionality"
echo ""
echo "If any issues, check logs:"
echo "  ssh -i $SSH_KEY $SSH_HOST -p $SSH_PORT 'tail -f /var/log/odoo/odoo-server.log'"
echo ""
