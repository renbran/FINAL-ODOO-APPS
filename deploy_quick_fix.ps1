# ============================================================================
# DEPLOY & RUN: Quick Fix for 138 Browser Errors
# Run this from your local Windows machine
# ============================================================================

param(
    [switch]$Execute,
    [switch]$FullMaintenance
)

$ServerIP = "139.84.163.11"
$ServerUser = "root"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "         ODOO 17 ERROR FIX DEPLOYMENT SCRIPT" -ForegroundColor Yellow
Write-Host "         Server: $ServerIP" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Test SSH connection
Write-Host "[TEST] Checking SSH connection..." -ForegroundColor Blue
$testResult = ssh -o ConnectTimeout=5 -o BatchMode=yes "$ServerUser@$ServerIP" "echo 'connected'" 2>&1
if ($testResult -ne "connected") {
    Write-Host "[ERROR] Cannot connect to server via SSH" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] SSH connection successful" -ForegroundColor Green
Write-Host ""

if (-not $Execute) {
    Write-Host "============================================================================" -ForegroundColor Yellow
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host "============================================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "This script will:" -ForegroundColor White
    Write-Host "  1. Stop Odoo service temporarily" -ForegroundColor White
    Write-Host "  2. Clear stale session files (older than 1 day)" -ForegroundColor White
    Write-Host "  3. Clear asset cache from database" -ForegroundColor White
    Write-Host "  4. Clear filestore assets" -ForegroundColor White
    Write-Host "  5. Restart Odoo service" -ForegroundColor White
    Write-Host ""
    Write-Host "To execute, run: .\deploy_quick_fix.ps1 -Execute" -ForegroundColor Cyan
    Write-Host "For full maintenance: .\deploy_quick_fix.ps1 -Execute -FullMaintenance" -ForegroundColor Cyan
    Write-Host ""
    
    # Show current server status
    Write-Host "[INFO] Current Odoo Service Status:" -ForegroundColor Blue
    ssh "$ServerUser@$ServerIP" "systemctl status odoo --no-pager | head -5"
    exit 0
}

Write-Host "[EXECUTING] Running quick fix on server..." -ForegroundColor Yellow
Write-Host ""

# Create and run the quick fix script
$QuickFixScript = @'
#!/bin/bash
set -e

echo "=== ODOO 17 QUICK FIX: Asset Cache Cleanup ==="
echo ""

# Backup first
BACKUP_DIR="/var/odoo/backups/quickfix_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "[BACKUP] Creating database backup..."
pg_dump -U odoo scholarixv2 | gzip > "$BACKUP_DIR/scholarixv2_backup.sql.gz"
echo "[BACKUP] Saved to: $BACKUP_DIR/scholarixv2_backup.sql.gz"

# Stop Odoo
echo "[1/5] Stopping Odoo service..."
systemctl stop odoo
sleep 2

# Clear old sessions
echo "[2/5] Clearing stale sessions..."
find /var/odoo/.local/share/Odoo/filestore/scholarixv2/sessions -type f -mtime +1 -delete 2>/dev/null || true
find /var/odoo/.local/share/Odoo/filestore/scholarixv2/sessions -type d -empty -delete 2>/dev/null || true

# Clear asset cache from database
echo "[3/5] Clearing asset cache from database..."
psql -U odoo -d scholarixv2 -c "DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';" 2>/dev/null || true

# Clear filestore assets
echo "[4/5] Clearing filestore assets..."
rm -rf /var/odoo/.local/share/Odoo/filestore/scholarixv2/assets/* 2>/dev/null || true

# Restart Odoo
echo "[5/5] Starting Odoo service..."
systemctl start odoo
sleep 5

# Verify
if systemctl is-active --quiet odoo; then
    echo ""
    echo "SUCCESS! Odoo is running."
    echo ""
    echo "IMPORTANT - Users must:"
    echo "  1. Press Ctrl+Shift+Delete to clear browser cache"
    echo "  2. Press Ctrl+Shift+R to hard refresh"
else
    echo ""
    echo "ERROR: Odoo failed to start!"
    echo "Check logs: journalctl -u odoo -f"
    exit 1
fi
'@

# Upload and execute
Write-Host "[UPLOAD] Uploading script to server..." -ForegroundColor Blue
$QuickFixScript | ssh "$ServerUser@$ServerIP" "cat > /tmp/quick_fix.sh && chmod +x /tmp/quick_fix.sh"

Write-Host "[RUN] Executing fix script..." -ForegroundColor Blue
Write-Host ""
ssh "$ServerUser@$ServerIP" "/tmp/quick_fix.sh"

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "                    FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Clear your browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  2. Hard refresh the page (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "  3. If errors persist, check browser DevTools console" -ForegroundColor White
Write-Host ""

# Show final status
Write-Host "[STATUS] Final Odoo Service Status:" -ForegroundColor Blue
ssh "$ServerUser@$ServerIP" "systemctl status odoo --no-pager | head -10"
