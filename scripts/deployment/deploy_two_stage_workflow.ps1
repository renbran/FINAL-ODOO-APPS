# ================================================================
# TWO-STAGE PAYMENT WORKFLOW - Deployment Script
# ================================================================
# This script deploys the two-stage payment workflow implementation
# to CloudPepper production server
# ================================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TWO-STAGE PAYMENT WORKFLOW DEPLOYMENT" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$SERVER = "root@139.84.163.11"
$SSH_KEY = "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt"
$LOCAL_PATH = "d:\RUNNING APPS\FINAL-ODOO-APPS\rental_management"
$REMOTE_PATH = "/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management"

Write-Host "📋 Deployment Plan:" -ForegroundColor Yellow
Write-Host "   - Upload: models/sale_contract.py" -ForegroundColor Gray
Write-Host "   - Upload: wizard/booking_wizard.py" -ForegroundColor Gray
Write-Host "   - Upload: wizard/property_vendor_wizard.py" -ForegroundColor Gray
Write-Host "   - Restart: Odoo service`n" -ForegroundColor Gray

$response = Read-Host "Proceed with deployment? (y/N)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "`n❌ Deployment cancelled by user" -ForegroundColor Red
    exit 0
}

Write-Host "`n🚀 Starting deployment...`n" -ForegroundColor Green

# Step 1: Upload sale_contract.py
Write-Host "[1/3] Uploading sale_contract.py..." -ForegroundColor Cyan
scp -i $SSH_KEY "$LOCAL_PATH\models\sale_contract.py" "$($SERVER):$REMOTE_PATH/models/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upload sale_contract.py" -ForegroundColor Red
    exit 1
}
Write-Host "✅ sale_contract.py uploaded successfully`n" -ForegroundColor Green

# Step 2: Upload booking_wizard.py
Write-Host "[2/3] Uploading booking_wizard.py..." -ForegroundColor Cyan
scp -i $SSH_KEY "$LOCAL_PATH\wizard\booking_wizard.py" "$($SERVER):$REMOTE_PATH/wizard/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upload booking_wizard.py" -ForegroundColor Red
    exit 1
}
Write-Host "✅ booking_wizard.py uploaded successfully`n" -ForegroundColor Green

# Step 3: Upload property_vendor_wizard.py
Write-Host "[3/3] Uploading property_vendor_wizard.py..." -ForegroundColor Cyan
scp -i $SSH_KEY "$LOCAL_PATH\wizard\property_vendor_wizard.py" "$($SERVER):$REMOTE_PATH/wizard/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upload property_vendor_wizard.py" -ForegroundColor Red
    exit 1
}
Write-Host "✅ property_vendor_wizard.py uploaded successfully`n" -ForegroundColor Green

# Step 4: Restart Odoo service
Write-Host "[4/4] Restarting Odoo service..." -ForegroundColor Cyan
ssh -i $SSH_KEY $SERVER 'systemctl restart odoo && sleep 8 && systemctl status odoo | head -15'
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to restart Odoo service" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Odoo service restarted successfully`n" -ForegroundColor Green

# Step 5: Check logs for errors
Write-Host "[5/5] Checking logs for errors..." -ForegroundColor Cyan
ssh -i $SSH_KEY $SERVER 'tail -50 /var/odoo/scholarixv2/logs/odoo-server.log | grep -i "error\|traceback" | tail -10'

Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Green

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test new booking creation" -ForegroundColor Gray
Write-Host "   2. Verify 3 invoices generated (booking + DLD + admin)" -ForegroundColor Gray
Write-Host "   3. Test payment marking and confirmation" -ForegroundColor Gray
Write-Host "   4. Test installment generation after booking paid" -ForegroundColor Gray
Write-Host "   5. Verify validation errors work correctly`n" -ForegroundColor Gray

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - TWO_STAGE_PAYMENT_WORKFLOW_COMPLETE.md (Full guide)" -ForegroundColor Gray
Write-Host "   - See file for testing checklist and troubleshooting`n" -ForegroundColor Gray
