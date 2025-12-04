# Phase 1 Critical Fixes Deployment Script
# Deploys: payment_status field, migration script, version update

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  PHASE 1 DEPLOYMENT - Critical Fixes" -ForegroundColor Cyan
Write-Host "  rental_management v3.4.0 to v3.4.1" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SSH_KEY = "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt"
$REMOTE_HOST = "root@139.84.163.11"
$REMOTE_PATH = "/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management"
$LOCAL_MODULE = "rental_management"

Write-Host "Phase 1 Fixes Included:" -ForegroundColor Yellow
Write-Host "  [OK] BLOCKER #1: Added payment_status field to SaleInvoice model" -ForegroundColor Green
Write-Host "  [OK] BLOCKER #2: Created migration script for backward compatibility" -ForegroundColor Green
Write-Host "  [OK] Updated module version to 3.4.1" -ForegroundColor Green
Write-Host ""

# Step 1: Backup
Write-Host "Step 1: Creating backup..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "   Backing up database..." -ForegroundColor Gray
ssh -i $SSH_KEY $REMOTE_HOST "sudo -u postgres pg_dump scholarixv2 > /tmp/scholarixv2_backup_$timestamp.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Database backup failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Database backed up: /tmp/scholarixv2_backup_$timestamp.sql" -ForegroundColor Green

Write-Host "   Backing up module files..." -ForegroundColor Gray
ssh -i $SSH_KEY $REMOTE_HOST "cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a && tar -czf /tmp/rental_management_backup_$timestamp.tar.gz rental_management/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Module backup failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Module backed up: /tmp/rental_management_backup_$timestamp.tar.gz" -ForegroundColor Green
Write-Host ""

# Step 2: Upload modified files
Write-Host "Step 2: Uploading modified files..." -ForegroundColor Yellow

Write-Host "   Uploading sale_contract.py..." -ForegroundColor Gray
scp -i $SSH_KEY "$LOCAL_MODULE\models\sale_contract.py" "${REMOTE_HOST}:${REMOTE_PATH}/models/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Upload failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] sale_contract.py uploaded" -ForegroundColor Green

Write-Host "   Uploading __manifest__.py..." -ForegroundColor Gray
scp -i $SSH_KEY "$LOCAL_MODULE\__manifest__.py" "${REMOTE_HOST}:${REMOTE_PATH}/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Upload failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] __manifest__.py uploaded" -ForegroundColor Green

Write-Host "   Creating migration directory..." -ForegroundColor Gray
ssh -i $SSH_KEY $REMOTE_HOST "mkdir -p ${REMOTE_PATH}/migrations/3.4.1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Directory creation failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   Uploading migration script..." -ForegroundColor Gray
scp -i $SSH_KEY "$LOCAL_MODULE\migrations\__init__.py" "${REMOTE_HOST}:${REMOTE_PATH}/migrations/"
scp -i $SSH_KEY "$LOCAL_MODULE\migrations\3.4.1\__init__.py" "${REMOTE_HOST}:${REMOTE_PATH}/migrations/3.4.1/"
scp -i $SSH_KEY "$LOCAL_MODULE\migrations\3.4.1\post-migrate.py" "${REMOTE_HOST}:${REMOTE_PATH}/migrations/3.4.1/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Upload failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Migration scripts uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Stop Odoo
Write-Host "Step 3: Stopping Odoo service..." -ForegroundColor Yellow
ssh -i $SSH_KEY $REMOTE_HOST "sudo systemctl stop odoo"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Failed to stop Odoo!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Odoo service stopped" -ForegroundColor Green
Write-Host ""

# Step 4: Run upgrade
Write-Host "Step 4: Running module upgrade (this will run migration)..." -ForegroundColor Yellow
Write-Host "   This may take 2-3 minutes..." -ForegroundColor Gray
Write-Host ""

ssh -i $SSH_KEY $REMOTE_HOST "/opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d scholarixv2 -u rental_management --stop-after-init 2>&1 | tee /tmp/upgrade_$timestamp.log"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "   [WARN] Upgrade command exited with non-zero code" -ForegroundColor Yellow
    Write-Host "   Checking logs for errors..." -ForegroundColor Gray
    Write-Host ""
}

# Step 5: Check migration logs
Write-Host ""
Write-Host "Step 5: Checking migration logs..." -ForegroundColor Yellow
Write-Host "   Searching for migration output..." -ForegroundColor Gray
Write-Host ""
Write-Host "==================== MIGRATION LOG ====================" -ForegroundColor Cyan
ssh -i $SSH_KEY $REMOTE_HOST "tail -n 500 /var/log/odoo/odoo.log | grep -A 30 'MIGRATION'; exit 0"
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Step 6: Start Odoo
Write-Host "Step 6: Starting Odoo service..." -ForegroundColor Yellow
ssh -i $SSH_KEY $REMOTE_HOST "sudo systemctl start odoo"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   [FAIL] Failed to start Odoo!" -ForegroundColor Red
    exit 1
}
Write-Host "   [OK] Odoo service started" -ForegroundColor Green
Write-Host ""

# Step 7: Wait and check status
Write-Host "Step 7: Waiting for Odoo to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "   Checking service status..." -ForegroundColor Gray
ssh -i $SSH_KEY $REMOTE_HOST "sudo systemctl status odoo --no-pager | head -n 10"
Write-Host ""

# Step 8: Check for errors
Write-Host "Step 8: Checking for errors..." -ForegroundColor Yellow
Write-Host "   Checking recent log entries..." -ForegroundColor Gray
Write-Host ""
Write-Host "==================== RECENT ERRORS ====================" -ForegroundColor Cyan
ssh -i $SSH_KEY $REMOTE_HOST "tail -n 100 /var/log/odoo/odoo.log | grep -i 'error'; exit 0"
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] Files Deployed:" -ForegroundColor Green
Write-Host "   - models/sale_contract.py (payment_status field added)" -ForegroundColor White
Write-Host "   - __manifest__.py (version 3.4.1)" -ForegroundColor White
Write-Host "   - migrations/3.4.1/post-migrate.py (backward compatibility)" -ForegroundColor White
Write-Host ""
Write-Host "Backups Created:" -ForegroundColor Yellow
Write-Host "   - Database: /tmp/scholarixv2_backup_$timestamp.sql" -ForegroundColor White
Write-Host "   - Module: /tmp/rental_management_backup_$timestamp.tar.gz" -ForegroundColor White
Write-Host ""
Write-Host "Module Upgraded: rental_management to v3.4.1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test new contract creation (should be in 'draft' stage)" -ForegroundColor White
Write-Host "   2. Test existing contracts (should work normally)" -ForegroundColor White
Write-Host "   3. Test booking invoice generation" -ForegroundColor White
Write-Host "   4. Test installment creation validation" -ForegroundColor White
Write-Host "   5. Monitor logs for any issues" -ForegroundColor White
Write-Host ""
Write-Host "[IMPORTANT]" -ForegroundColor Red
Write-Host "   - Clear browser cache (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "   - Test thoroughly before using in production" -ForegroundColor White
Write-Host "   - Keep backups until stability confirmed" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[OK] Phase 1 deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To monitor logs in real-time:" -ForegroundColor Gray
Write-Host "   ssh -i $SSH_KEY $REMOTE_HOST 'tail -f /var/log/odoo/odoo.log'" -ForegroundColor Cyan
Write-Host ""
