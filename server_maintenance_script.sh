#!/bin/bash
# ============================================================================
# ODOO 17 SERVER MAINTENANCE SCRIPT
# CloudPepper/Vultr Server: 139.84.163.11
# Database: scholarixv2
# ============================================================================
# This script performs comprehensive cleanup and maintenance tasks:
# 1. Removes unused module folders with deprecated JavaScript
# 2. Clears stale session files
# 3. Regenerates asset bundles
# 4. Cleans up database entries for uninstalled modules
# ============================================================================

set -e  # Exit on any error

# Configuration
DB_NAME="scholarixv2"
DB_USER="odoo"
ODOO_USER="odoo"
ADDONS_PATH="/var/odoo/scholarixv2/extra-addons"
FILESTORE_PATH="/var/odoo/.local/share/Odoo/filestore/scholarixv2"
ODOO_SERVICE="odoo"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "============================================================================"
echo "           ODOO 17 SERVER MAINTENANCE SCRIPT"
echo "           Database: $DB_NAME"
echo "           Date: $(date)"
echo "============================================================================"
echo ""

# ============================================================================
# STEP 1: BACKUP (Safety First!)
# ============================================================================
log_info "Step 1: Creating safety backup..."

BACKUP_DIR="/var/odoo/backups/maintenance_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
log_info "Backing up database..."
pg_dump -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/${DB_NAME}_backup.sql.gz"
log_success "Database backup: $BACKUP_DIR/${DB_NAME}_backup.sql.gz"

# ============================================================================
# STEP 2: LIST MODULES TO REMOVE (UNINSTALLED WITH DEPRECATED JS)
# ============================================================================
log_info "Step 2: Identifying unused modules with deprecated JavaScript..."

# These modules have deprecated require() syntax and are NOT installed
DEPRECATED_MODULES=(
    "property_sale_management"
    "responsive_web"
    "vehicle_subscription"
    "vista_backend_theme"
    "theme_fasion"
    "theme_archit"
    "backend_theme_infinito"
    "backend_theme_odoo12"
    "barcode_capturing_sale_purchase"
    "base_accounting_kit"
    "cts_theme_rozz"
    "dodger_blue"
    "ecommerce_barcode_search"
    "face_recognized_attendance_login"
    "machine_repair_barcode_scanner"
    "multicolor_backend_theme"
    "pos_add_product_webcam_barcode"
    "pos_face_recognition"
)

echo ""
log_info "Modules marked for folder removal (all are UNINSTALLED):"
for module in "${DEPRECATED_MODULES[@]}"; do
    echo "  - $module"
done
echo ""

# ============================================================================
# STEP 3: STOP ODOO SERVICE
# ============================================================================
log_info "Step 3: Stopping Odoo service..."
systemctl stop $ODOO_SERVICE
sleep 3
log_success "Odoo service stopped"

# ============================================================================
# STEP 4: CLEAR STALE SESSIONS
# ============================================================================
log_info "Step 4: Clearing stale session files..."

SESSION_PATH="$FILESTORE_PATH/sessions"
if [ -d "$SESSION_PATH" ]; then
    # Count sessions before cleanup
    SESSION_COUNT_BEFORE=$(find "$SESSION_PATH" -type f | wc -l)
    
    # Remove session files older than 7 days
    find "$SESSION_PATH" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Also remove empty directories
    find "$SESSION_PATH" -type d -empty -delete 2>/dev/null || true
    
    SESSION_COUNT_AFTER=$(find "$SESSION_PATH" -type f 2>/dev/null | wc -l)
    log_success "Sessions cleaned: $((SESSION_COUNT_BEFORE - SESSION_COUNT_AFTER)) removed, $SESSION_COUNT_AFTER remaining"
else
    log_warning "Session directory not found: $SESSION_PATH"
fi

# ============================================================================
# STEP 5: CLEAR ASSET CACHE
# ============================================================================
log_info "Step 5: Clearing asset cache from database..."

psql -U $DB_USER -d $DB_NAME << 'CLEANSQL'
-- Remove old asset bundles
DELETE FROM ir_attachment 
WHERE name LIKE 'web.assets%' 
AND create_date < NOW() - INTERVAL '1 day';

-- Clear asset version cache
DELETE FROM ir_attachment 
WHERE res_model = 'ir.ui.view' 
AND res_field = 'arch_fs';

-- Update module states for deprecated modules (mark as uninstallable if problematic)
UPDATE ir_module_module 
SET state = 'uninstallable' 
WHERE name IN (
    'property_sale_management',
    'responsive_web',
    'vehicle_subscription',
    'vista_backend_theme',
    'theme_fasion',
    'theme_archit',
    'backend_theme_infinito',
    'backend_theme_odoo12',
    'barcode_capturing_sale_purchase',
    'base_accounting_kit',
    'cts_theme_rozz',
    'dodger_blue',
    'ecommerce_barcode_search',
    'face_recognized_attendance_login',
    'machine_repair_barcode_scanner',
    'multicolor_backend_theme',
    'pos_add_product_webcam_barcode',
    'pos_face_recognition'
) AND state = 'uninstalled';
CLEANSQL

log_success "Asset cache cleared from database"

# ============================================================================
# STEP 6: CLEAR FILESTORE ASSET CACHE
# ============================================================================
log_info "Step 6: Clearing filestore asset cache..."

ASSETS_PATH="$FILESTORE_PATH/assets"
if [ -d "$ASSETS_PATH" ]; then
    rm -rf "$ASSETS_PATH"/*
    log_success "Filestore assets cleared"
else
    log_warning "Assets directory not found: $ASSETS_PATH"
fi

# ============================================================================
# STEP 7: REMOVE DEPRECATED MODULE FOLDERS (OPTIONAL - COMMENTED OUT)
# ============================================================================
log_info "Step 7: Module folder cleanup..."

# SAFETY: This section is commented out by default
# Uncomment to actually remove the folders after verifying the list

# ODOOAPPS_PATH="$ADDONS_PATH/odooapps.git-68ee71eda34bc"
# CYBRO_PATH="$ADDONS_PATH/cybroaddons.git-68f85fe88986a"

# for module in "${DEPRECATED_MODULES[@]}"; do
#     # Check odooapps
#     if [ -d "$ODOOAPPS_PATH/$module" ]; then
#         log_info "Moving $module to backup..."
#         mv "$ODOOAPPS_PATH/$module" "$BACKUP_DIR/"
#         log_success "Moved: $ODOOAPPS_PATH/$module"
#     fi
#     
#     # Check cybroaddons
#     if [ -d "$CYBRO_PATH/$module" ]; then
#         log_info "Moving $module to backup..."
#         mv "$CYBRO_PATH/$module" "$BACKUP_DIR/"
#         log_success "Moved: $CYBRO_PATH/$module"
#     fi
# done

log_warning "Module folder removal is DISABLED by default"
log_warning "Edit this script and uncomment Step 7 to enable folder removal"

# ============================================================================
# STEP 8: FIX PERMISSIONS
# ============================================================================
log_info "Step 8: Fixing file permissions..."

chown -R $ODOO_USER:$ODOO_USER "$FILESTORE_PATH" 2>/dev/null || true
chown -R $ODOO_USER:$ODOO_USER "$ADDONS_PATH" 2>/dev/null || true

log_success "Permissions fixed"

# ============================================================================
# STEP 9: START ODOO SERVICE
# ============================================================================
log_info "Step 9: Starting Odoo service..."

systemctl start $ODOO_SERVICE
sleep 5

# Check if service started successfully
if systemctl is-active --quiet $ODOO_SERVICE; then
    log_success "Odoo service started successfully"
else
    log_error "Odoo service failed to start! Check logs with: journalctl -u odoo -f"
    exit 1
fi

# ============================================================================
# STEP 10: VERIFY SERVICE
# ============================================================================
log_info "Step 10: Verifying service status..."

systemctl status $ODOO_SERVICE --no-pager | head -15

echo ""
echo "============================================================================"
echo "                    MAINTENANCE COMPLETE"
echo "============================================================================"
echo ""
log_success "Backup location: $BACKUP_DIR"
log_info "Next steps for users:"
echo "  1. Clear browser cache (Ctrl+Shift+Delete)"
echo "  2. Hard refresh the page (Ctrl+Shift+R)"
echo "  3. If errors persist, check: journalctl -u odoo -f"
echo ""
echo "============================================================================"
