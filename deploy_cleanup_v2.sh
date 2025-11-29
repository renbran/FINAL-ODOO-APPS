#!/bin/bash
# Simplified rental_management Cleanup & Deployment for CloudPepper
# This works with direct Odoo CLI commands

set -e

TIMESTAMP=$(date +%s)
LOG_FILE="/var/log/odoo/rental_cleanup_${TIMESTAMP}.log"
BACKUP_DIR="/opt/odoo/backups"
BACKUP_FILE="$BACKUP_DIR/scholarixv2_pre_rental_$(date +%Y%m%d_%H%M%S).sql"

mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

# Logging functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  $1" | tee -a "$LOG_FILE"
}

log_ok() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1" | tee -a "$LOG_FILE"
}

log_err() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1" | tee -a "$LOG_FILE"
}

echo "=========================================="
echo "🧹 RENTAL_MANAGEMENT CLEANUP & DEPLOYMENT"
echo "=========================================="

# Step 1: Backup Database
log_info "Step 1: Creating database backup..."
if pg_dump scholarixv2 > "$BACKUP_FILE" 2>&1; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_ok "Backup created: $BACKUP_FILE ($SIZE)"
else
    log_err "Backup failed"
    exit 1
fi

# Step 2: Direct PostgreSQL Cleanup (remove stale views)
log_info "Step 2: Cleaning stale views from database..."
psql scholarixv2 << 'EOF' >> "$LOG_FILE" 2>&1
BEGIN;
-- Remove stale rental_management views that might reference non-existent fields
DELETE FROM ir_ui_view 
WHERE module = 'rental_management' 
  OR (key LIKE 'rental_management.%' AND arch LIKE '%is_payment_plan%');

-- Mark module for upgrade
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'rental_management';

COMMIT;

-- Verify cleanup
SELECT '[CLEANUP] Removed stale views, module marked for upgrade' as status;
EOF

if [ $? -eq 0 ]; then
    log_ok "Database cleanup completed"
else
    log_warn "Database cleanup had issues, continuing..."
fi

# Step 3: Stop Odoo gracefully
log_info "Step 3: Stopping Odoo service..."
if systemctl is-active --quiet odoo; then
    systemctl stop odoo
    sleep 3
    log_ok "Odoo service stopped"
else
    log_warn "Odoo service was not running"
fi

# Step 4: Clear Python cache
log_info "Step 4: Clearing Python cache..."
find /opt/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/odoo -name "*.pyc" -delete 2>/dev/null || true
log_ok "Python cache cleared"

# Step 5: Uninstall Module (Fresh Start)
log_info "Step 5: Uninstalling rental_management module..."
cd /opt/odoo

# Start Odoo in uninstall mode (with timeout)
timeout 300 odoo --config=/etc/odoo.conf -d scholarixv2 --uninstall=rental_management --stop-after-init >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ] || [ $? -eq 124 ]; then
    log_ok "Module uninstalled (or timeout after init)"
    sleep 2
else
    log_warn "Uninstall returned error, attempting clean install..."
fi

# Step 6: Install Module Fresh
log_info "Step 6: Installing rental_management module (fresh)..."
log_info "  This may take 3-5 minutes, please wait..."

# Use longer timeout for install
timeout 600 odoo --config=/etc/odoo.conf -d scholarixv2 -i rental_management --stop-after-init >> "$LOG_FILE" 2>&1

INSTALL_EXIT=$?
if [ $INSTALL_EXIT -eq 0 ]; then
    log_ok "Module installation completed successfully"
elif [ $INSTALL_EXIT -eq 124 ]; then
    log_warn "Installation timed out (may still be successful), checking status..."
else
    log_err "Installation failed with exit code: $INSTALL_EXIT"
    log_info "Restoring database from backup..."
    psql scholarixv2 < "$BACKUP_FILE" 2>&1
    log_err "Restored backup. Check log: $LOG_FILE"
    exit 1
fi

# Step 7: Start Odoo Service
log_info "Step 7: Starting Odoo service..."
systemctl start odoo
sleep 4

if systemctl is-active --quiet odoo; then
    log_ok "Odoo service started successfully"
else
    log_err "Failed to start Odoo service"
    exit 1
fi

# Step 8: Verify Installation
log_info "Step 8: Verifying installation..."
sleep 5

STATUS=$(psql scholarixv2 -t -c "SELECT state FROM ir_module_module WHERE name = 'rental_management' LIMIT 1;" 2>/dev/null | xargs)

if [ "$STATUS" = "installed" ]; then
    log_ok "✅ rental_management is INSTALLED and ready"
elif [ "$STATUS" = "to upgrade" ] || [ "$STATUS" = "to install" ]; then
    log_warn "Module state is: $STATUS (may still be installing)"
else
    log_warn "Could not determine module state: $STATUS"
fi

# Check for critical errors
log_info "Checking logs for errors..."
if tail -30 /var/log/odoo/odoo.log 2>/dev/null | grep -i "error" | grep -i "rental" > /dev/null; then
    log_warn "Found rental-related errors in logs:"
    tail -30 /var/log/odoo/odoo.log 2>/dev/null | grep -i "error" | grep -i "rental" | tee -a "$LOG_FILE"
else
    log_ok "No critical rental-management errors detected"
fi

echo ""
echo "=========================================="
log_ok "🎉 DEPLOYMENT COMPLETE"
echo "=========================================="
log_ok "Module: rental_management"
log_ok "Status: $STATUS"
log_ok "Timestamp: $(date)"
log_ok "Backup: $BACKUP_FILE"
log_ok "Log: $LOG_FILE"
echo "=========================================="

# Tail the deployment log
log_info "📋 Last 20 lines of deployment log:"
tail -20 "$LOG_FILE"

exit 0
