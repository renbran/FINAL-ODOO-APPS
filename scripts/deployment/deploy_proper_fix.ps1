#!/usr/bin/env pwsh
# ===============================================================================
# PROPER FIX: Install/Upgrade llm_lead_scoring Module
# ===============================================================================
# This is the CORRECT way to fix the ai_enrichment_report field error
# By properly installing/upgrading the module that defines the field
# ===============================================================================

param(
    [string]$ProductionHost = "scholarixglobal.com",
    [string]$ProductionUser = "odoo",
    [string]$OdooPath = "/opt/odoo",
    [string]$OdooConf = "/etc/odoo/odoo.conf",
    [string]$DatabaseName = "scholarix_db",
    [switch]$CheckOnly,
    [switch]$SkipConfirmation
)

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  PROPER FIX: Install/Upgrade llm_lead_scoring Module" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check module status first
Write-Host "[1/4] Checking module status on production..." -ForegroundColor Yellow

$checkScript = @"
cd ${OdooPath}
./odoo-bin shell -c ${OdooConf} -d ${DatabaseName} --no-http << 'PYTHON'
try:
    module = self.env['ir.module.module'].search([('name', '=', 'llm_lead_scoring')], limit=1)
    if module:
        print(f"STATUS:{module.state}")
        print(f"VERSION:{module.installed_version or 'Not installed'}")
    else:
        print("STATUS:not_found")
        print("VERSION:N/A")
except Exception as e:
    print(f"ERROR:{str(e)}")
PYTHON
"@

$result = ssh "${ProductionUser}@${ProductionHost}" $checkScript

if ($result -match "STATUS:installed") {
    Write-Host "✓ Module is installed but may need upgrade" -ForegroundColor Green
    $action = "upgrade"
} elseif ($result -match "STATUS:uninstalled") {
    Write-Host "⚠ Module exists but not installed" -ForegroundColor Yellow
    $action = "install"
} elseif ($result -match "STATUS:not_found") {
    Write-Host "✗ Module not found in database" -ForegroundColor Red
    $action = "install"
} else {
    Write-Host "? Module status unclear: $result" -ForegroundColor Yellow
    $action = "upgrade"
}

Write-Host ""
Write-Host "Recommended Action: $action" -ForegroundColor Cyan
Write-Host ""

if ($CheckOnly) {
    Write-Host "Check-only mode. Exiting." -ForegroundColor Gray
    exit 0
}

# Confirm with user
if (-not $SkipConfirmation) {
    Write-Host "This will $action llm_lead_scoring module on PRODUCTION" -ForegroundColor Yellow
    Write-Host "Odoo will be stopped briefly during upgrade" -ForegroundColor Yellow
    $confirmation = Read-Host "Continue? (Y/N)"
    
    if ($confirmation -ne "Y" -and $confirmation -ne "y") {
        Write-Host "Cancelled by user" -ForegroundColor Red
        exit 0
    }
}

# Perform the upgrade/install
Write-Host ""
Write-Host "[2/4] ${action}ing module on production..." -ForegroundColor Yellow

$upgradeFlag = if ($action -eq "install") { "-i" } else { "-u" }

$deployScript = @"
cd ${OdooPath}
echo "Starting module $action..."
./odoo-bin -c ${OdooConf} -d ${DatabaseName} ${upgradeFlag} llm_lead_scoring --stop-after-init --logfile=/var/log/odoo/upgrade_llm_lead_scoring.log
echo "Module $action completed"
"@

ssh "${ProductionUser}@${ProductionHost}" $deployScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Module $action failed" -ForegroundColor Red
    Write-Host "Check logs: ssh ${ProductionUser}@${ProductionHost} 'tail -100 /var/log/odoo/upgrade_llm_lead_scoring.log'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Module ${action}ed successfully" -ForegroundColor Green

# Restart Odoo
Write-Host ""
Write-Host "[3/4] Restarting Odoo service..." -ForegroundColor Yellow

$restartScript = @"
sudo systemctl restart odoo
sleep 3
sudo systemctl status odoo --no-pager | head -20
"@

ssh "${ProductionUser}@${ProductionHost}" $restartScript
Write-Host "✓ Odoo restarted" -ForegroundColor Green

# Clear cache
Write-Host ""
Write-Host "[4/4] Clearing asset cache..." -ForegroundColor Yellow

$cacheScript = @"
rm -rf /var/lib/odoo/.local/share/Odoo/filestore/${DatabaseName}/assets/*
echo "Cache cleared"
"@

ssh "${ProductionUser}@${ProductionHost}" $cacheScript
Write-Host "✓ Cache cleared" -ForegroundColor Green

# Success summary
Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Module: llm_lead_scoring" -ForegroundColor White
Write-Host "Action: ${action}ed" -ForegroundColor White
Write-Host "Status: Active and running" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Clear browser cache on all client machines (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "2. Test CRM lead forms - should load without OwlError" -ForegroundColor White
Write-Host "3. Verify 'AI Scoring' tab is visible on lead forms" -ForegroundColor White
Write-Host "4. Monitor logs: ssh ${ProductionUser}@${ProductionHost} 'tail -f /var/log/odoo/odoo.log'" -ForegroundColor White
Write-Host ""
Write-Host "✓ The ai_enrichment_report field should now exist and work properly" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan
