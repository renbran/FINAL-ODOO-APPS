# ===============================================================================
# EMERGENCY DEPLOYMENT SCRIPT: ai_enrichment_report Fix (PowerShell)
# ===============================================================================
# Date: November 29, 2025
# Purpose: Deploy crm_ai_field_compatibility module to production
# Target: scholarixglobal.com
# ===============================================================================

param(
    [string]$ProductionHost = "scholarixglobal.com",
    [string]$ProductionUser = "odoo",
    [string]$OdooPath = "/opt/odoo",
    [string]$OdooConf = "/etc/odoo/odoo.conf",
    [string]$DatabaseName = "scholarix_db",
    [string]$ModuleName = "crm_ai_field_compatibility",
    [switch]$SkipConfirmation
)

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Log-Info { param([string]$Message) Write-ColorOutput "[INFO] $Message" -Color Green }
function Log-Warn { param([string]$Message) Write-ColorOutput "[WARN] $Message" -Color Yellow }
function Log-Error { param([string]$Message) Write-ColorOutput "[ERROR] $Message" -Color Red }
function Log-Step { param([string]$Message) Write-ColorOutput "[STEP] $Message" -Color Cyan }

# ===============================================================================
# MAIN DEPLOYMENT SCRIPT
# ===============================================================================

try {
    Log-Info "==============================================================================="
    Log-Info "EMERGENCY FIX DEPLOYMENT: ai_enrichment_report Field"
    Log-Info "==============================================================================="
    Log-Info "Target: $ProductionHost"
    Log-Info "Module: $ModuleName"
    Log-Info "Time: $(Get-Date)"
    Log-Info "==============================================================================="

    # Step 1: Validate local module exists
    Log-Step "1/9 - Validating local module..."
    $LocalModulePath = ".\crm_ai_field_compatibility"
    
    if (-not (Test-Path $LocalModulePath)) {
        Log-Error "Module directory not found: $LocalModulePath"
        Log-Error "Please run this script from FINAL-ODOO-APPS root directory"
        exit 1
    }

    if (-not (Test-Path "$LocalModulePath\__manifest__.py")) {
        Log-Error "Module manifest not found: $LocalModulePath\__manifest__.py"
        exit 1
    }

    Log-Info "✓ Local module validated"

    # Step 2: Check SSH connectivity (using plink or ssh command)
    Log-Step "2/9 - Checking production server connectivity..."
    $sshTest = & ssh -o ConnectTimeout=5 "${ProductionUser}@${ProductionHost}" "echo connected" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Log-Error "Cannot connect to $ProductionHost"
        Log-Error "Please check SSH credentials and server availability"
        Log-Error "Error: $sshTest"
        exit 1
    }
    
    Log-Info "✓ Production server accessible"

    # Step 3: Confirm deployment
    if (-not $SkipConfirmation) {
        Log-Step "3/9 - Confirming deployment..."
        Log-Warn "This will deploy emergency fix to PRODUCTION server"
        Log-Warn "The Odoo service will be stopped and restarted"
        $confirmation = Read-Host "Continue? (Y/N)"
        
        if ($confirmation -ne "Y" -and $confirmation -ne "y") {
            Log-Error "Deployment cancelled by user"
            exit 0
        }
    }

    # Step 4: Backup existing module (if exists)
    Log-Step "4/9 - Creating backup of existing module (if any)..."
    $backupScript = @"
if [ -d "${OdooPath}/addons/${ModuleName}" ]; then
    BACKUP_NAME="${ModuleName}.backup.\$(date +%Y%m%d_%H%M%S)"
    mv ${OdooPath}/addons/${ModuleName} ${OdooPath}/addons/\$BACKUP_NAME
    echo "Backup created: \$BACKUP_NAME"
else
    echo "No existing module to backup"
fi
"@
    
    $backupResult = & ssh "${ProductionUser}@${ProductionHost}" $backupScript
    Write-Host $backupResult
    Log-Info "✓ Backup completed"

    # Step 5: Upload module to production
    Log-Step "5/9 - Uploading module to production..."
    & scp -r $LocalModulePath "${ProductionUser}@${ProductionHost}:${OdooPath}/addons/"
    
    if ($LASTEXITCODE -ne 0) {
        Log-Error "Failed to upload module"
        exit 1
    }
    
    Log-Info "✓ Module uploaded successfully"

    # Step 6: Set correct permissions
    Log-Step "6/9 - Setting file permissions..."
    $permScript = @"
chown -R odoo:odoo ${OdooPath}/addons/${ModuleName}
chmod -R 755 ${OdooPath}/addons/${ModuleName}
echo "Permissions set"
"@
    
    & ssh "${ProductionUser}@${ProductionHost}" $permScript
    Log-Info "✓ Permissions set"

    # Step 7: Install module
    Log-Step "7/9 - Installing module in Odoo..."
    $installScript = @"
cd ${OdooPath}
./odoo-bin -c ${OdooConf} -d ${DatabaseName} -i ${ModuleName} --stop-after-init --logfile=/var/log/odoo/install_${ModuleName}.log
"@
    
    & ssh "${ProductionUser}@${ProductionHost}" $installScript
    
    if ($LASTEXITCODE -ne 0) {
        Log-Error "Module installation failed"
        Log-Error "Check logs: ssh ${ProductionUser}@${ProductionHost} 'tail -100 /var/log/odoo/install_${ModuleName}.log'"
        exit 1
    }
    
    Log-Info "✓ Module installed successfully"

    # Step 8: Restart Odoo service
    Log-Step "8/9 - Restarting Odoo service..."
    $restartScript = @"
sudo systemctl restart odoo
sleep 5
sudo systemctl status odoo | head -20
"@
    
    $restartResult = & ssh "${ProductionUser}@${ProductionHost}" $restartScript
    Write-Host $restartResult
    Log-Info "✓ Odoo service restarted"

    # Step 9: Clear asset cache
    Log-Step "9/9 - Clearing asset cache..."
    $cacheScript = @"
rm -rf /var/lib/odoo/.local/share/Odoo/filestore/${DatabaseName}/assets/*
echo "Asset cache cleared"
"@
    
    & ssh "${ProductionUser}@${ProductionHost}" $cacheScript
    Log-Info "✓ Asset cache cleared"

    # ===============================================================================
    # DEPLOYMENT COMPLETE
    # ===============================================================================

    Log-Info ""
    Log-Info "==============================================================================="
    Log-Info "✅ EMERGENCY FIX DEPLOYED SUCCESSFULLY"
    Log-Info "==============================================================================="
    Log-Info "Module: $ModuleName"
    Log-Info "Status: Installed and Active"
    Log-Info "Time: $(Get-Date)"
    Log-Info "==============================================================================="

    Log-Info ""
    Log-Info "NEXT STEPS:"
    Log-Info "1. Clear browser cache (Ctrl+Shift+R) on all client machines"
    Log-Info "2. Test CRM lead forms to verify error is resolved"
    Log-Info "3. Monitor logs for any new errors:"
    Log-Info "   ssh ${ProductionUser}@${ProductionHost} 'tail -f /var/log/odoo/odoo.log | grep -i ai_enrichment'"
    Log-Info "4. Verify field is visible in CRM lead forms"
    Log-Info "5. Plan permanent fix: Install/upgrade llm_lead_scoring module"

    Log-Info ""
    Log-Warn "IMPORTANT: This is a COMPATIBILITY FIX"
    Log-Warn "For full AI lead scoring features, install llm_lead_scoring module"

    Log-Info ""
    Log-Info "Deployment log saved to: /var/log/odoo/install_${ModuleName}.log"
    Log-Info "==============================================================================="

    exit 0

} catch {
    Log-Error "Emergency deployment failed: $_"
    Log-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}
