# PowerShell deployment script for scholarixv2 - announcement_banner module fix

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Deploying announcement_banner fix to scholarixv2" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$REMOTE_HOST = "root@139.84.163.11"
$REMOTE_PORT = "22"
$SSH_KEY = "$HOME\.ssh\odoo17_cloudpepper_new"

Write-Host "Step 1: Updating module in database..." -ForegroundColor Yellow
ssh -i $SSH_KEY -p $REMOTE_PORT $REMOTE_HOST "cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 -u announcement_banner --stop-after-init"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Step 2: Restarting Odoo service..." -ForegroundColor Yellow
    ssh -i $SSH_KEY -p $REMOTE_PORT $REMOTE_HOST "sudo systemctl restart odoo 2>/dev/null || echo 'Service restart may require manual intervention'"
    
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Clear browser cache (Ctrl+Shift+Delete)"
    Write-Host "2. Login to scholarixv2 database"
    Write-Host "3. Open browser console (F12)"
    Write-Host "4. Check for any console errors"
    Write-Host "5. Test announcement banner functionality"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "DEPLOYMENT FAILED" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Red
    Write-Host ""
}

Write-Host "======================================================================"
