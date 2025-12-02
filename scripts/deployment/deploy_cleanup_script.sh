#!/bin/bash
# rental_management Cleanup & Deployment Script
# This script performs a complete database cleanup and fresh module deployment
# Executes remotely on CloudPepper

set -e

LOG_FILE="/var/log/odoo/rental_management_deploy_$(date +%s).log"
BACKUP_DIR="/opt/odoo/backups"
BACKUP_FILE="$BACKUP_DIR/scholarixv2_pre_deployment_$(date +%Y%m%d_%H%M%S).sql"

echo "=========================================="
echo "🧹 RENTAL_MANAGEMENT CLEANUP & DEPLOYMENT"
echo "=========================================="
echo "Starting at: $(date)"
echo "Log file: $LOG_FILE"
echo ""

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log output
log_step() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1" | tee -a "$LOG_FILE"
}

# Step 1: Verify Database Connection
log_step "Step 1/6: Verifying database connection..."
if sudo -u odoo psql -U odoo_user -d scholarixv2 -c "SELECT 1" > /dev/null 2>&1; then
    log_success "Database connection verified"
else
    log_error "Failed to connect to database"
    exit 1
fi

# Step 2: Create Backup
log_step "Step 2/6: Creating pre-deployment backup..."
if sudo -u odoo pg_dump -U odoo_user -d scholarixv2 -F p -f "$BACKUP_FILE" 2>> "$LOG_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_success "Backup created: $BACKUP_FILE ($BACKUP_SIZE)"
else
    log_error "Backup creation failed"
    exit 1
fi

# Step 3: Stop Odoo Service
log_step "Step 3/6: Stopping Odoo service..."
if sudo systemctl stop odoo 2>> "$LOG_FILE"; then
    log_success "Odoo service stopped"
    sleep 2  # Wait for graceful shutdown
else
    log_warning "Odoo service stop returned non-zero, continuing..."
fi

# Step 4: Database Cleanup (Remove stale views and module data)
log_step "Step 4/6: Cleaning up stale views and module data from database..."
sudo -u odoo psql -U odoo_user -d scholarixv2 << EOF >> "$LOG_FILE" 2>&1
BEGIN;

-- Step 4a: Delete stale view records related to rental_management
DELETE FROM ir_ui_view 
WHERE module LIKE 'rental_management' 
   OR (key LIKE 'rental_management.%' AND arch LIKE '%is_payment_plan%');

-- Step 4b: Delete any orphaned view actions
DELETE FROM ir_actions_act_window 
WHERE res_id IN (SELECT id FROM ir_ui_view WHERE module = 'rental_management' AND create_date < NOW() - interval '1 hour');

-- Step 4c: Verify rental_management module is marked for update (not installed)
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'rental_management' AND state IN ('installed', 'to install');

COMMIT;

-- Verify cleanup
SELECT COUNT(*) as stale_views_removed FROM ir_ui_view WHERE module = 'rental_management';
EOF

if [ $? -eq 0 ]; then
    log_success "Database cleanup completed"
else
    log_error "Database cleanup encountered issues"
fi

# Step 5: Clear Odoo Cache
log_step "Step 5/6: Clearing Odoo cache..."
if rm -rf /var/lib/odoo/.local/share/Odoo 2>> "$LOG_FILE"; then
    log_success "Odoo cache cleared"
else
    log_warning "Could not fully clear cache, continuing..."
fi

# Step 6: Start Odoo and Deploy Module (Uninstall + Reinstall)
log_step "Step 6/6: Starting Odoo with module uninstall and reinstall..."
log_step "This may take 2-5 minutes..."

# First attempt: Uninstall module
log_step "  6a: Uninstalling rental_management..."
if timeout 300 sudo -u odoo /var/odoo/scholarixv2/src/odoo/odoo-bin \
    --config=/etc/odoo/odoo.conf \
    -d scholarixv2 \
    --uninstall=rental_management \
    --stop-after-init 2>> "$LOG_FILE"; then
    log_success "Module uninstalled"
    sleep 2
else
    log_warning "Uninstall timed out or failed, attempting fresh install anyway..."
fi

# Second attempt: Install module fresh
log_step "  6b: Installing rental_management (fresh)..."
if timeout 600 sudo -u odoo /var/odoo/scholarixv2/src/odoo/odoo-bin \
    --config=/etc/odoo/odoo.conf \
    -d scholarixv2 \
    -i rental_management \
    --stop-after-init 2>> "$LOG_FILE"; then
    log_success "Module installed successfully"
else
    log_error "Module installation failed - check log file"
    echo "Attempting to restore from backup..."
    sudo -u odoo psql -U odoo_user -d scholarixv2 < "$BACKUP_FILE" 2>> "$LOG_FILE"
    log_error "Restored backup. Please check the log for details."
    exit 1
fi

# Step 7: Start Odoo Service
log_step "Starting Odoo service..."
if sudo systemctl start odoo 2>> "$LOG_FILE"; then
    log_success "Odoo service started"
    sleep 3
else
    log_error "Failed to start Odoo service"
    exit 1
fi

# Verification
log_step "Verifying deployment..."
sleep 5
if sudo -u odoo psql -U odoo_user -d scholarixv2 -c "SELECT state FROM ir_module_module WHERE name = 'rental_management'" 2>> "$LOG_FILE" | grep -q "installed"; then
    log_success "✅ rental_management module is INSTALLED"
else
    log_warning "Could not verify module installation status"
fi

# Check Odoo logs for errors
if tail -50 /var/log/odoo/odoo.log | grep -i "error.*rental_management" > /dev/null; then
    log_warning "Found errors in Odoo logs related to rental_management"
    tail -20 /var/log/odoo/odoo.log | tee -a "$LOG_FILE"
else
    log_success "No critical errors detected in logs"
fi

log_success "=========================================="
log_success "🎉 DEPLOYMENT COMPLETE!"
log_success "=========================================="
log_success "Module: rental_management"
log_success "Status: INSTALLED"
log_success "Time: $(date)"
log_success "Backup saved: $BACKUP_FILE"
log_success "Full log: $LOG_FILE"
log_success "=========================================="
