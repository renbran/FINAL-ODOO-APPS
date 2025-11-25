# OSUS Properties Web Modules Deployment Script (PowerShell)
# Version: 1.0
# Date: November 25, 2025

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "OSUS Properties Web Modules Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SSH_KEY = "$HOME\.ssh\odoo17_cloudpepper_new"
$SSH_HOST = "root@139.84.163.11"
$SSH_PORT = "22"
$ODOO_PATH = "/var/odoo/scholarixv2"
$DATABASE = "scholarixv2"
$MODULES = "muk_web_colors,muk_web_theme,muk_web_chatter,muk_web_dialog"

Write-Host "Target: https://stagingtry.cloudpepper.site/" -ForegroundColor Yellow
Write-Host "Modules: $MODULES" -ForegroundColor Yellow
Write-Host ""

# Confirm deployment
$confirm = Read-Host "Are you sure you want to deploy? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Deployment cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Step 1/5: Stopping Odoo service..." -ForegroundColor Green
ssh -i $SSH_KEY "$SSH_HOST" -p $SSH_PORT "sudo systemctl stop odoo"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Odoo stopped successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to stop Odoo" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2/5: Creating backup..." -ForegroundColor Green
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ssh -i $SSH_KEY "$SSH_HOST" -p $SSH_PORT "cd $ODOO_PATH && sudo -u odoo tar -czf backups/modules_backup_$timestamp.tar.gz addons/muk_web_*"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup created successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ Backup creation failed (continuing anyway)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3/5: Updating modules..." -ForegroundColor Green
ssh -i $SSH_KEY "$SSH_HOST" -p $SSH_PORT "cd $ODOO_PATH && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d $DATABASE -u $MODULES --stop-after-init"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Modules updated successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Module update failed" -ForegroundColor Red
    Write-Host "Rolling back..." -ForegroundColor Yellow
    ssh -i $SSH_KEY "$SSH_HOST" -p $SSH_PORT "sudo systemctl start odoo"
    exit 1
}

Write-Host ""
Write-Host "Step 4/5: Starting Odoo service..." -ForegroundColor Green
ssh -i $SSH_KEY "$SSH_HOST" -p $SSH_PORT "sudo systemctl start odoo"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Odoo started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start Odoo" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 5/5: Verifying deployment..." -ForegroundColor Green
Start-Sleep -Seconds 5
ssh -i $SSH_KEY "$SSH_HOST" -p $SSH_PORT "sudo systemctl status odoo --no-pager | head -n 10"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please verify:" -ForegroundColor Yellow
Write-Host "1. Access: https://stagingtry.cloudpepper.site/"
Write-Host "2. Clear browser cache (Ctrl+F5)"
Write-Host "3. Check navbar is maroon with gold border"
Write-Host "4. Verify apps menu shows OSUS colors"
Write-Host "5. Test chatter and dialog functionality"
Write-Host ""
Write-Host "If any issues, check logs:" -ForegroundColor Yellow
Write-Host "  ssh -i $SSH_KEY $SSH_HOST -p $SSH_PORT 'tail -f /var/log/odoo/odoo-server.log'"
Write-Host ""
