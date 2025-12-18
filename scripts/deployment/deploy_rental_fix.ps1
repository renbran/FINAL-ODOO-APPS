#############################################################################
# Deploy Rental Management Fix to Production Server
# Usage: .\deploy_rental_fix.ps1
#############################################################################

$ErrorActionPreference = "Stop"

# Configuration
$SERVER = "root@139.84.163.11"
$SSH_KEY = "$env:USERPROFILE\.ssh\scholarix_vultr"
$LOCAL_SCRIPT = ".\fix_rental_management_deployment.sh"
$REMOTE_SCRIPT = "/tmp/fix_rental_management.sh"

Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     DEPLOYING RENTAL MANAGEMENT FIX TO PRODUCTION            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload script to server
Write-Host "📤 Step 1: Uploading fix script to server..." -ForegroundColor Yellow

if (Test-Path $SSH_KEY) {
    scp -i $SSH_KEY $LOCAL_SCRIPT "${SERVER}:${REMOTE_SCRIPT}"
    Write-Host "✓ Script uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ SSH key not found. Using password authentication..." -ForegroundColor Yellow
    scp $LOCAL_SCRIPT "${SERVER}:${REMOTE_SCRIPT}"
}

Write-Host ""

# Step 2: Make script executable
Write-Host "🔧 Step 2: Making script executable..." -ForegroundColor Yellow

if (Test-Path $SSH_KEY) {
    ssh -i $SSH_KEY $SERVER "chmod +x $REMOTE_SCRIPT"
} else {
    ssh $SERVER "chmod +x $REMOTE_SCRIPT"
}
Write-Host "✓ Script is executable" -ForegroundColor Green

Write-Host ""

# Step 3: Execute the fix script
Write-Host "🚀 Step 3: Executing fix script on server..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path $SSH_KEY) {
    ssh -i $SSH_KEY $SERVER "sudo bash $REMOTE_SCRIPT"
} else {
    Write-Host "⚠ Using password authentication..." -ForegroundColor Yellow
    ssh $SERVER "sudo bash $REMOTE_SCRIPT"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

# Step 4: Cleanup
Write-Host "🧹 Step 4: Cleaning up temporary files..." -ForegroundColor Yellow

if (Test-Path $SSH_KEY) {
    ssh -i $SSH_KEY $SERVER "rm $REMOTE_SCRIPT"
} else {
    ssh $SERVER "rm $REMOTE_SCRIPT"
}
Write-Host "✓ Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    DEPLOYMENT COMPLETE                       ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Verification Steps:" -ForegroundColor Cyan
Write-Host "   1. Check Odoo logs:" -ForegroundColor White
Write-Host "      ssh $SERVER 'sudo tail -f /var/log/odoo/odoo.log'" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   2. Test Property Dashboard:" -ForegroundColor White
Write-Host "      https://scholarixglobal.com" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   3. Monitor service status:" -ForegroundColor White
Write-Host "      ssh $SERVER 'sudo systemctl status odoo'" -ForegroundColor DarkGray
Write-Host ""
