# Quick Fix Deployment: Booking Percentage UI
# Fixes: 1000% display issue and read-only field

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Booking Percentage UI Fix Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SSH_KEY = "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt"
$SERVER = "root@139.84.163.11"
$REMOTE_PATH = "/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/views"

# Upload view file
Write-Host "[1/3] Uploading property_details_view.xml..." -ForegroundColor Yellow
scp -i $SSH_KEY `
    "rental_management\views\property_details_view.xml" `
    "${SERVER}:${REMOTE_PATH}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ File uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Upload failed!" -ForegroundColor Red
    exit 1
}

# Restart Odoo
Write-Host ""
Write-Host "[2/3] Restarting Odoo service..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "sudo systemctl restart odoo"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Odoo restarted successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Restart failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Verifying service status..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
ssh -i $SSH_KEY $SERVER "sudo systemctl status odoo --no-pager | head -n 10"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Changes applied:" -ForegroundColor Cyan
Write-Host "  • Removed percentage widget (fixes display issue)" -ForegroundColor White
Write-Host "  • Added percent symbol manually after field" -ForegroundColor White
Write-Host "  • Made custom_booking_percentage editable" -ForegroundColor White
Write-Host "  • Improved labels and help text" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Refresh your browser (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "  2. Open any property -> Pricing Details tab" -ForegroundColor White
Write-Host "  3. Check Booking Configuration section" -ForegroundColor White
Write-Host "  4. Should now show correct percentage display" -ForegroundColor White
Write-Host ""
