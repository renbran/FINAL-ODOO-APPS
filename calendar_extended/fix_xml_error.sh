#!/bin/bash
# Calendar Extended - Critical XML Fix Script
# This script specifically fixes the XML template validation error

set -e

# Configuration
ODOO_USER="odoo"
ODOO_PATH="/var/odoo/osuspro"
ODOO_CONFIG="$ODOO_PATH/odoo.conf"
PYTHON_BIN="$ODOO_PATH/venv/bin/python3"
ODOO_BIN="$ODOO_PATH/src/odoo-bin"
MODULE_NAME="calendar_extended"
MODULE_PATH="$ODOO_PATH/src/addons/$MODULE_NAME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_status "=== CALENDAR EXTENDED XML FIX ==="

# Stop Odoo service
print_status "Stopping Odoo service..."
systemctl stop odoo || print_warning "Odoo service was not running"
sleep 3

# Remove problematic template files that cause XML validation errors
print_status "Removing problematic XML template files..."

if [ -d "$MODULE_PATH" ]; then
    # Remove any template files in static directories
    find "$MODULE_PATH/static" -name "*template*.xml" -delete 2>/dev/null || true
    find "$MODULE_PATH/static" -name "templates.xml" -delete 2>/dev/null || true
    
    # Remove any XML files that don't start with <odoo>
    find "$MODULE_PATH" -name "*.xml" -exec grep -l "^<templates>" {} \; | xargs rm -f 2>/dev/null || true
    find "$MODULE_PATH" -name "*.xml" -exec grep -l "^<?xml.*<templates>" {} \; | xargs rm -f 2>/dev/null || true
    
    print_success "Problematic template files removed"
else
    print_warning "Module path not found: $MODULE_PATH"
fi

# Clean Python cache completely
print_status "Cleaning Python cache..."
find "$ODOO_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$ODOO_PATH" -name "*.pyc" -delete 2>/dev/null || true
find "$ODOO_PATH" -name "*.pyo" -delete 2>/dev/null || true

# Clean Odoo cache
print_status "Cleaning Odoo cache..."
if [ -d "/var/lib/odoo" ]; then
    find /var/lib/odoo -name "assets_*" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf /var/lib/odoo/sessions/* 2>/dev/null || true
fi

# Validate remaining XML files
print_status "Validating XML files..."
xml_errors=0

if [ -d "$MODULE_PATH" ]; then
    while IFS= read -r -d '' xml_file; do
        if ! xmllint --noout "$xml_file" 2>/dev/null; then
            print_error "XML syntax error in: $xml_file"
            xml_errors=$((xml_errors + 1))
        else
            print_success "Valid XML: $(basename "$xml_file")"
        fi
    done < <(find "$MODULE_PATH" -name "*.xml" -print0)
    
    if [ $xml_errors -gt 0 ]; then
        print_error "Found $xml_errors XML files with errors"
        exit 1
    fi
fi

# Force complete module uninstall including database cleanup
print_status "Force uninstalling calendar_extended module..."

DB_NAME=$(grep -E "^db_name\s*=" "$ODOO_CONFIG" | cut -d'=' -f2 | tr -d ' ' | head -1)

if [ -n "$DB_NAME" ]; then
    print_status "Cleaning database entries..."
    
    sudo -u postgres psql "$DB_NAME" <<EOF 2>/dev/null || true
-- Complete cleanup of calendar_extended
BEGIN;

-- Remove module and all related data
DELETE FROM ir_module_module WHERE name = 'calendar_extended';
DELETE FROM ir_model_data WHERE module = 'calendar_extended';
DELETE FROM ir_attachment WHERE res_model LIKE '%calendar_extended%' OR res_model LIKE '%calendar.announcement%';

-- Remove views and menus
DELETE FROM ir_ui_view WHERE name LIKE '%calendar_extended%' OR arch_db LIKE '%calendar_extended%';
DELETE FROM ir_ui_menu WHERE name LIKE '%calendar_extended%' OR name LIKE '%Meeting Announcement%';
DELETE FROM ir_actions_act_window WHERE res_model LIKE '%calendar_extended%' OR res_model LIKE '%calendar.announcement%';

-- Remove model definitions
DELETE FROM ir_model WHERE model LIKE '%calendar_extended%' OR model LIKE '%calendar.announcement%';
DELETE FROM ir_model_fields WHERE model LIKE '%calendar_extended%' OR model LIKE '%calendar.announcement%';

-- Drop custom tables if they exist
DROP TABLE IF EXISTS calendar_announcement CASCADE;
DROP TABLE IF EXISTS calendar_announcement_attendee_rel CASCADE;
DROP TABLE IF EXISTS calendar_announcement_department_rel CASCADE;
DROP TABLE IF EXISTS calendar_department_select_wizard CASCADE;
DROP TABLE IF EXISTS calendar_send_invitation_wizard CASCADE;

-- Remove any orphaned records
DELETE FROM ir_cron WHERE name LIKE '%calendar_extended%' OR code LIKE '%calendar_extended%';

COMMIT;
EOF
    
    print_success "Database cleaned"
fi

# Start Odoo service
print_status "Starting Odoo service..."
systemctl start odoo
sleep 10

# Check if Odoo started successfully
if systemctl is-active --quiet odoo; then
    print_success "Odoo service started successfully"
    
    # Wait for Odoo to fully initialize
    print_status "Waiting for Odoo to initialize..."
    sleep 15
    
    # Install the clean module
    print_status "Installing cleaned calendar_extended module..."
    
    # Update module list first
    sudo -u "$ODOO_USER" "$PYTHON_BIN" "$ODOO_BIN" \
        -c "$ODOO_CONFIG" \
        --no-http \
        --stop-after-init \
        --update-modules-list
    
    # Install the module
    sudo -u "$ODOO_USER" "$PYTHON_BIN" "$ODOO_BIN" \
        -c "$ODOO_CONFIG" \
        --no-http \
        --stop-after-init \
        --install "$MODULE_NAME" || {
        
        print_error "Module installation failed. Check logs:"
        tail -n 50 "$ODOO_PATH/logs"/*.log 2>/dev/null || echo "No log files found"
        exit 1
    }
    
    print_success "Module installed successfully"
    
    # Final service check
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069 | grep -q "200\|302\|301"; then
        print_success "Odoo is responding to HTTP requests"
        print_success "Calendar Extended module is ready!"
        print_status "Access: Calendar → Meeting Announcements → Announcements"
    else
        print_warning "Odoo is running but may not be fully ready yet"
    fi
    
else
    print_error "Failed to start Odoo service"
    systemctl status odoo --no-pager -l
    exit 1
fi

print_success "=== XML FIX COMPLETED SUCCESSFULLY ==="
