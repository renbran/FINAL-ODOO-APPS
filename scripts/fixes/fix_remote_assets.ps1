# Remote Asset Fix Script for CloudPepper
# Fixes missing rental.js and announcement_banner assets

param(
    [Parameter(Mandatory=$false)]
    [string]$SSHUser = "root",
    
    [Parameter(Mandatory=$false)]
    [string]$SSHHost = "scholarixglobal.com"
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REMOTE ASSET FIX" -ForegroundColor Yellow
Write-Host "rental_management + announcement_banner" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test SSH connection
Write-Host "Testing SSH connection to ${SSHUser}@${SSHHost}..." -ForegroundColor Green
$sshTest = ssh -o ConnectTimeout=5 "${SSHUser}@${SSHHost}" "echo 'Connection OK'" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ SSH connection failed!" -ForegroundColor Red
    Write-Host "Error: $sshTest" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Cyan
    Write-Host "1. SSH keys are configured" -ForegroundColor White
    Write-Host "2. Host is reachable: $SSHHost" -ForegroundColor White
    Write-Host "3. Username is correct: $SSHUser" -ForegroundColor White
    exit 1
}

Write-Host "✅ SSH connection successful!" -ForegroundColor Green
Write-Host ""

# Upload fix script to server
Write-Host "Step 1: Uploading fix script to server..." -ForegroundColor Green
$localScript = "fix_missing_assets.sh"

if (!(Test-Path $localScript)) {
    Write-Host "❌ Local script not found: $localScript" -ForegroundColor Red
    Write-Host "Please ensure you're running this from the repository root" -ForegroundColor Yellow
    exit 1
}

scp "$localScript" "${SSHUser}@${SSHHost}:/tmp/fix_missing_assets.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Script uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to upload script" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Make script executable and run it
Write-Host "Step 2: Executing fix script on server..." -ForegroundColor Green
Write-Host "This may take 2-3 minutes..." -ForegroundColor Gray
Write-Host ""

$remoteCommand = @"
chmod +x /tmp/fix_missing_assets.sh
cd /var/odoo/scholarixv2
bash /tmp/fix_missing_assets.sh
"@

ssh "${SSHUser}@${SSHHost}" $remoteCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Fix script executed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ Script execution completed with warnings (check output above)" -ForegroundColor Yellow
}

Write-Host ""

# Verify fix
Write-Host "Step 3: Verifying fix..." -ForegroundColor Green

$verifyCommand = @"
cd /var/odoo/scholarixv2
echo "Checking rental.js..."
find extra-addons -path '*/rental_management/static/src/js/rental.js' 2>/dev/null | head -1

echo ""
echo "Checking Odoo service..."
systemctl is-active odoo && echo "Odoo: RUNNING" || echo "Odoo: STOPPED"

echo ""
echo "Recent logs (last 10 lines):"
tail -10 /var/odoo/scholarixv2/logs/odoo.log | grep -v "INFO" | tail -5
"@

Write-Host ""
ssh "${SSHUser}@${SSHHost}" $verifyCommand

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ REMOTE FIX COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open Odoo in browser: https://scholarixglobal.com" -ForegroundColor White
Write-Host "2. Hard refresh: Ctrl+Shift+R" -ForegroundColor White
Write-Host "3. Open DevTools Console (F12)" -ForegroundColor White
Write-Host "4. Verify no errors for:" -ForegroundColor White
Write-Host "   - rental_management/static/src/js/rental.js" -ForegroundColor Gray
Write-Host "   - announcement_banner assets" -ForegroundColor Gray
Write-Host ""

Write-Host "Monitor logs remotely:" -ForegroundColor Cyan
Write-Host "ssh ${SSHUser}@${SSHHost} 'tail -f /var/odoo/scholarixv2/logs/odoo.log | grep -i error'" -ForegroundColor Gray
Write-Host ""

# Optional: Clean up uploaded script
$cleanup = Read-Host "Remove uploaded script from server? (y/n)"
if ($cleanup -eq "y") {
    ssh "${SSHUser}@${SSHHost}" "rm -f /tmp/fix_missing_assets.sh"
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}

Write-Host ""
Write-Host "Fix completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
