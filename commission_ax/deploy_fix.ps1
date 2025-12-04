# Deploy commission_ax bugfix to CloudPepper
# Fixes: Missing field commission_lines_count

$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host "Commission AX Module Deployment"
Write-Host "========================================"
Write-Host ""

# Configuration
$SERVER = "root@139.84.163.11"
$PORT = "22"
$REMOTE_PATH = "/var/odoo/osusproperties/extra-addons/commission_ax"
$LOCAL_PATH = "."

Write-Host "Target Server: $SERVER"
Write-Host "Module Path: $REMOTE_PATH"
Write-Host ""

# Step 1: Backup current module on server
Write-Host "Step 1: Creating backup on server..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ssh -p $PORT $SERVER "cd $REMOTE_PATH/.. && cp -r commission_ax commission_ax.backup_$timestamp"
Write-Host "✅ Backup created" -ForegroundColor Green
Write-Host ""

# Step 2: Upload modified files
Write-Host "Step 2: Uploading modified files..." -ForegroundColor Yellow
scp -P $PORT models/sale_order.py "$SERVER`:$REMOTE_PATH/models/"
Write-Host "✅ Files uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Update module in Odoo
Write-Host "Step 3: Updating module in Odoo..." -ForegroundColor Yellow
ssh -p $PORT $SERVER "sudo systemctl stop odoo && sleep 2"
Write-Host "  - Odoo stopped"

ssh -p $PORT $SERVER "cd /var/odoo/osusproperties && ./odoo-bin -u commission_ax --stop-after-init -d odoo 2>&1 | tail -n 20"
Write-Host "  - Module upgraded"

ssh -p $PORT $SERVER "sudo systemctl start odoo && sleep 3"
Write-Host "  - Odoo started"
Write-Host ""

# Step 4: Verify deployment
Write-Host "Step 4: Verifying deployment..." -ForegroundColor Yellow
ssh -p $PORT $SERVER "sudo systemctl status odoo | head -n 10"
Write-Host ""

Write-Host "========================================"
Write-Host "✅ Deployment Complete" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Check logs: ssh -p $PORT $SERVER 'tail -f /var/log/odoo/odoo.log'"
Write-Host "2. Test in browser: Navigate to Sales → Orders"
Write-Host "3. Verify no RPC errors when viewing sale orders"
Write-Host ""
