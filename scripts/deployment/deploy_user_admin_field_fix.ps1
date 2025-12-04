# Quick Fix: Add is_admin field to res.users
# Fixes: "res.users"."is_admin" field is undefined error

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "User Admin Field Compatibility Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SSH_KEY = "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt"
$SERVER = "root@139.84.163.11"
$REMOTE_BASE = "/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a"

# Create module directory on server
Write-Host "[1/5] Creating module directory on server..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "mkdir -p ${REMOTE_BASE}/user_admin_field_compatibility/models"

# Upload manifest
Write-Host "[2/5] Uploading module files..." -ForegroundColor Yellow
scp -i $SSH_KEY `
    "user_admin_field_compatibility\__manifest__.py" `
    "${SERVER}:${REMOTE_BASE}/user_admin_field_compatibility/"

scp -i $SSH_KEY `
    "user_admin_field_compatibility\__init__.py" `
    "${SERVER}:${REMOTE_BASE}/user_admin_field_compatibility/"

scp -i $SSH_KEY `
    "user_admin_field_compatibility\models\__init__.py" `
    "${SERVER}:${REMOTE_BASE}/user_admin_field_compatibility/models/"

scp -i $SSH_KEY `
    "user_admin_field_compatibility\models\res_users.py" `
    "${SERVER}:${REMOTE_BASE}/user_admin_field_compatibility/models/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Files uploaded successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Upload failed!" -ForegroundColor Red
    exit 1
}

# Restart Odoo
Write-Host ""
Write-Host "[3/5] Restarting Odoo service..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "sudo systemctl restart odoo"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Odoo restarted successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Restart failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/5] Waiting for Odoo to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "[5/5] Verifying service status..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "sudo systemctl status odoo --no-pager | head -n 10"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ MODULE DEPLOYED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Login to Odoo UI" -ForegroundColor White
Write-Host "  2. Go to Apps -> Update Apps List" -ForegroundColor White
Write-Host "  3. Search for 'User Admin Field Compatibility'" -ForegroundColor White
Write-Host "  4. Install the module" -ForegroundColor White
Write-Host "  5. Refresh your browser" -ForegroundColor White
Write-Host "  6. The is_admin field error should be resolved" -ForegroundColor White
Write-Host ""
Write-Host "Module Location:" -ForegroundColor Cyan
Write-Host "  Server: user_admin_field_compatibility module" -ForegroundColor White
Write-Host ""
