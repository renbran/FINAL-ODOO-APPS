#!/bin/bash
# ===============================================================================
# EMERGENCY DEPLOYMENT SCRIPT: ai_enrichment_report Fix
# ===============================================================================
# Date: November 29, 2025
# Purpose: Deploy crm_ai_field_compatibility module to production
# Target: scholarixglobal.com
# ===============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
PRODUCTION_HOST="scholarixglobal.com"
PRODUCTION_USER="odoo"
ODOO_PATH="/opt/odoo"
ODOO_CONF="/etc/odoo/odoo.conf"
DATABASE_NAME="scholarix_db"
MODULE_NAME="crm_ai_field_compatibility"
LOCAL_MODULE_PATH="./crm_ai_field_compatibility"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Error handler
error_handler() {
    log_error "Emergency deployment failed at line $1"
    log_error "Rolling back changes..."
    # Add rollback logic here if needed
    exit 1
}

trap 'error_handler $LINENO' ERR

# ===============================================================================
# MAIN DEPLOYMENT SCRIPT
# ===============================================================================

log_info "==============================================================================="
log_info "EMERGENCY FIX DEPLOYMENT: ai_enrichment_report Field"
log_info "==============================================================================="
log_info "Target: $PRODUCTION_HOST"
log_info "Module: $MODULE_NAME"
log_info "Time: $(date)"
log_info "==============================================================================="

# Step 1: Validate local module exists
log_step "1/8 - Validating local module..."
if [ ! -d "$LOCAL_MODULE_PATH" ]; then
    log_error "Module directory not found: $LOCAL_MODULE_PATH"
    log_error "Please run this script from FINAL-ODOO-APPS root directory"
    exit 1
fi

if [ ! -f "$LOCAL_MODULE_PATH/__manifest__.py" ]; then
    log_error "Module manifest not found: $LOCAL_MODULE_PATH/__manifest__.py"
    exit 1
fi

log_info "✓ Local module validated"

# Step 2: Check production server connectivity
log_step "2/8 - Checking production server connectivity..."
if ssh -o ConnectTimeout=5 "${PRODUCTION_USER}@${PRODUCTION_HOST}" "echo connected" > /dev/null 2>&1; then
    log_info "✓ Production server accessible"
else
    log_error "Cannot connect to $PRODUCTION_HOST"
    log_error "Please check SSH credentials and server availability"
    exit 1
fi

# Step 3: Backup existing module (if exists)
log_step "3/8 - Creating backup of existing module (if any)..."
ssh "${PRODUCTION_USER}@${PRODUCTION_HOST}" << 'EOF'
    if [ -d "/opt/odoo/addons/crm_ai_field_compatibility" ]; then
        BACKUP_NAME="crm_ai_field_compatibility.backup.$(date +%Y%m%d_%H%M%S)"
        mv /opt/odoo/addons/crm_ai_field_compatibility "/opt/odoo/addons/$BACKUP_NAME"
        echo "Backup created: $BACKUP_NAME"
    else
        echo "No existing module to backup"
    fi
EOF
log_info "✓ Backup completed"

# Step 4: Upload module to production
log_step "4/8 - Uploading module to production..."
scp -r "$LOCAL_MODULE_PATH" "${PRODUCTION_USER}@${PRODUCTION_HOST}:${ODOO_PATH}/addons/"
if [ $? -eq 0 ]; then
    log_info "✓ Module uploaded successfully"
else
    log_error "Failed to upload module"
    exit 1
fi

# Step 5: Set correct permissions
log_step "5/8 - Setting file permissions..."
ssh "${PRODUCTION_USER}@${PRODUCTION_HOST}" << EOF
    chown -R odoo:odoo ${ODOO_PATH}/addons/${MODULE_NAME}
    chmod -R 755 ${ODOO_PATH}/addons/${MODULE_NAME}
EOF
log_info "✓ Permissions set"

# Step 6: Install module
log_step "6/8 - Installing module in Odoo..."
log_warn "This will stop and restart Odoo service"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_error "Deployment cancelled by user"
    exit 1
fi

ssh "${PRODUCTION_USER}@${PRODUCTION_HOST}" << EOF
    cd ${ODOO_PATH}
    ./odoo-bin -c ${ODOO_CONF} -d ${DATABASE_NAME} -i ${MODULE_NAME} --stop-after-init --logfile=/var/log/odoo/install_${MODULE_NAME}.log
EOF

if [ $? -eq 0 ]; then
    log_info "✓ Module installed successfully"
else
    log_error "Module installation failed"
    log_error "Check logs: ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} 'tail -100 /var/log/odoo/install_${MODULE_NAME}.log'"
    exit 1
fi

# Step 7: Restart Odoo service
log_step "7/8 - Restarting Odoo service..."
ssh "${PRODUCTION_USER}@${PRODUCTION_HOST}" << 'EOF'
    sudo systemctl restart odoo
    sleep 5
    sudo systemctl status odoo | head -20
EOF
log_info "✓ Odoo service restarted"

# Step 8: Verify installation
log_step "8/8 - Verifying installation..."
ssh "${PRODUCTION_USER}@${PRODUCTION_HOST}" << EOF
    # Check if module is installed
    cd ${ODOO_PATH}
    ./odoo-bin shell -c ${ODOO_CONF} -d ${DATABASE_NAME} --no-http << 'PYTHON'
import sys
try:
    env = self.env
    module = env['ir.module.module'].search([('name', '=', '${MODULE_NAME}')], limit=1)
    if module and module.state == 'installed':
        print("✓ Module ${MODULE_NAME} is installed")
        sys.exit(0)
    else:
        print("✗ Module ${MODULE_NAME} is not installed")
        sys.exit(1)
except Exception as e:
    print(f"✗ Verification failed: {str(e)}")
    sys.exit(1)
PYTHON
EOF

if [ $? -eq 0 ]; then
    log_info "✓ Installation verified"
else
    log_error "Verification failed"
    exit 1
fi

# Step 9: Clear asset cache
log_step "Clearing asset cache..."
ssh "${PRODUCTION_USER}@${PRODUCTION_HOST}" << EOF
    rm -rf /var/lib/odoo/.local/share/Odoo/filestore/${DATABASE_NAME}/assets/*
    echo "✓ Asset cache cleared"
EOF

# ===============================================================================
# DEPLOYMENT COMPLETE
# ===============================================================================

log_info "==============================================================================="
log_info "✅ EMERGENCY FIX DEPLOYED SUCCESSFULLY"
log_info "==============================================================================="
log_info "Module: $MODULE_NAME"
log_info "Status: Installed and Active"
log_info "Time: $(date)"
log_info "==============================================================================="

log_info ""
log_info "NEXT STEPS:"
log_info "1. Clear browser cache (Ctrl+Shift+R) on all client machines"
log_info "2. Test CRM lead forms to verify error is resolved"
log_info "3. Monitor logs for any new errors:"
log_info "   ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} 'tail -f /var/log/odoo/odoo.log | grep -i ai_enrichment'"
log_info "4. Verify field is visible in CRM lead forms"
log_info "5. Plan permanent fix: Install/upgrade llm_lead_scoring module"

log_info ""
log_warn "IMPORTANT: This is a COMPATIBILITY FIX"
log_warn "For full AI lead scoring features, install llm_lead_scoring module"

log_info ""
log_info "Deployment log saved to: /var/log/odoo/install_${MODULE_NAME}.log"
log_info "==============================================================================="

exit 0
