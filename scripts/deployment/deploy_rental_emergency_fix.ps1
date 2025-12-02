# EMERGENCY FIX: rental_management dependency issue
# Deploy crm_ai_field_compatibility FIRST, then upgrade rental_management

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EMERGENCY FIX DEPLOYMENT" -ForegroundColor Yellow
Write-Host "Issue: rental_management missing ai_enrichment_report field" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SSH_HOST = "scholarixglobal.com"
$SSH_USER = "your_ssh_user"  # REPLACE WITH YOUR USERNAME
$ODOO_PATH = "/var/odoo/scholarixv2"
$DB_NAME = "scholarixv2"

Write-Host "Step 1: Verify SSH connection..." -ForegroundColor Green
Write-Host "Testing connection to $SSH_HOST..." -ForegroundColor Gray

# Test SSH connection
$sshTest = ssh -o ConnectTimeout=5 -o BatchMode=yes "${SSH_USER}@${SSH_HOST}" "echo 2>&1" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ SSH connection failed!" -ForegroundColor Red
    Write-Host "Please update SSH_USER variable and ensure SSH keys are configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual deployment steps:" -ForegroundColor Cyan
    Write-Host "1. SSH to CloudPepper: ssh ${SSH_USER}@${SSH_HOST}" -ForegroundColor White
    Write-Host "2. Install compatibility module: odoo -d $DB_NAME -i crm_ai_field_compatibility --stop-after-init" -ForegroundColor White
    Write-Host "3. Restart Odoo: sudo systemctl restart odoo" -ForegroundColor White
    Write-Host "4. Upgrade rental_management: odoo -d $DB_NAME -u rental_management --stop-after-init" -ForegroundColor White
    Write-Host "5. Restart Odoo again: sudo systemctl restart odoo" -ForegroundColor White
    exit 1
}

Write-Host "✅ SSH connection successful!" -ForegroundColor Green
Write-Host ""

# Step 2: Check if compatibility module exists
Write-Host "Step 2: Checking if crm_ai_field_compatibility module exists..." -ForegroundColor Green
$compatModuleCheck = ssh "${SSH_USER}@${SSH_HOST}" "ls -d ${ODOO_PATH}/extra-addons/*/crm_ai_field_compatibility 2>/dev/null | head -1"
if ([string]::IsNullOrEmpty($compatModuleCheck)) {
    Write-Host "❌ Compatibility module not found on server!" -ForegroundColor Red
    Write-Host "Uploading module to server..." -ForegroundColor Yellow
    
    # Upload module
    $localModulePath = "d:\RUNNING APPS\FINAL-ODOO-APPS\crm_ai_field_compatibility"
    if (Test-Path $localModulePath) {
        scp -r "$localModulePath" "${SSH_USER}@${SSH_HOST}:${ODOO_PATH}/extra-addons/"
        Write-Host "✅ Module uploaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Local module not found at: $localModulePath" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Compatibility module found: $compatModuleCheck" -ForegroundColor Green
}
Write-Host ""

# Step 3: Install compatibility module
Write-Host "Step 3: Installing crm_ai_field_compatibility module..." -ForegroundColor Green
Write-Host "Running: odoo -d $DB_NAME -i crm_ai_field_compatibility --stop-after-init" -ForegroundColor Gray

$installOutput = ssh "${SSH_USER}@${SSH_HOST}" "cd ${ODOO_PATH} && odoo -d $DB_NAME -i crm_ai_field_compatibility --stop-after-init 2>&1"
Write-Host $installOutput

if ($installOutput -match "error|traceback|failed" -and $installOutput -notmatch "ModuleNotFoundError.*already installed") {
    Write-Host "⚠️ Warning: Installation may have failed. Check output above." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
} else {
    Write-Host "✅ Compatibility module installed!" -ForegroundColor Green
}
Write-Host ""

# Step 4: Restart Odoo
Write-Host "Step 4: Restarting Odoo service..." -ForegroundColor Green
ssh "${SSH_USER}@${SSH_HOST}" "sudo systemctl restart odoo"
Start-Sleep -Seconds 5
Write-Host "✅ Odoo restarted!" -ForegroundColor Green
Write-Host ""

# Step 5: Upload updated rental_management manifest
Write-Host "Step 5: Uploading updated rental_management module..." -ForegroundColor Green
$localRentalPath = "d:\RUNNING APPS\FINAL-ODOO-APPS\rental_management"
$remoteRentalPath = ssh "${SSH_USER}@${SSH_HOST}" "ls -d ${ODOO_PATH}/extra-addons/*/rental_management 2>/dev/null | head -1"

if ([string]::IsNullOrEmpty($remoteRentalPath)) {
    Write-Host "❌ rental_management module not found on server!" -ForegroundColor Red
    exit 1
}

Write-Host "Found rental_management at: $remoteRentalPath" -ForegroundColor Gray
scp "${localRentalPath}/__manifest__.py" "${SSH_USER}@${SSH_HOST}:${remoteRentalPath}/__manifest__.py"
Write-Host "✅ Manifest file uploaded!" -ForegroundColor Green
Write-Host ""

# Step 6: Upgrade rental_management
Write-Host "Step 6: Upgrading rental_management module..." -ForegroundColor Green
Write-Host "Running: odoo -d $DB_NAME -u rental_management --stop-after-init" -ForegroundColor Gray

$upgradeOutput = ssh "${SSH_USER}@${SSH_HOST}" "cd ${ODOO_PATH} && odoo -d $DB_NAME -u rental_management --stop-after-init 2>&1"
Write-Host $upgradeOutput

if ($upgradeOutput -match "error|traceback|ParseError") {
    Write-Host "❌ Upgrade failed! Check output above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Rollback steps:" -ForegroundColor Yellow
    Write-Host "1. Restore from backup" -ForegroundColor White
    Write-Host "2. Check Odoo logs: tail -f /var/log/odoo/odoo.log" -ForegroundColor White
    exit 1
} else {
    Write-Host "✅ rental_management upgraded successfully!" -ForegroundColor Green
}
Write-Host ""

# Step 7: Final restart
Write-Host "Step 7: Final Odoo restart..." -ForegroundColor Green
ssh "${SSH_USER}@${SSH_HOST}" "sudo systemctl restart odoo"
Start-Sleep -Seconds 5
Write-Host "✅ Odoo restarted!" -ForegroundColor Green
Write-Host ""

# Step 8: Verify
Write-Host "Step 8: Verifying deployment..." -ForegroundColor Green
$verifyOutput = ssh "${SSH_USER}@${SSH_HOST}" "tail -n 50 /var/log/odoo/odoo.log | grep -i 'rental_management\|error'"
Write-Host $verifyOutput

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test CRM lead form: Open any lead and check 'Property Details' tab" -ForegroundColor White
Write-Host "2. Test property sales: Create contract, generate payment schedule" -ForegroundColor White
Write-Host "3. Test SPA report: Print from property sale contract" -ForegroundColor White
Write-Host "4. Monitor logs: tail -f /var/log/odoo/odoo.log" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: See EMERGENCY_FIX_rental_management_dependency.md" -ForegroundColor Cyan
