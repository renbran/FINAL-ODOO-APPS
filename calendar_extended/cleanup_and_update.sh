#!/bin/bash
# Calendar Extended Module Cleanup and Database Update Script
# This script will clean up the module and fix XML validation errors

set -e  # Exit on any error

# Configuration - Updated paths for your server
ODOO_USER="odoo"
ODOO_PATH="/var/odoo/osuspro"
ODOO_CONFIG="$ODOO_PATH/odoo.conf"
PYTHON_BIN="$ODOO_PATH/venv/bin/python3"
ODOO_BIN="$ODOO_PATH/src/odoo-bin"
LOG_DIR="$ODOO_PATH/logs"
MODULE_NAME="calendar_extended"
MODULE_PATH="$ODOO_PATH/src/addons/$MODULE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to stop Odoo service
stop_odoo() {
    print_status "Stopping Odoo service..."
    systemctl stop odoo || print_warning "Odoo service was not running"
    sleep 3
}

# Function to start Odoo service
start_odoo() {
    print_status "Starting Odoo service..."
    systemctl start odoo
    sleep 5
}

# Function to clean old problematic files
clean_old_files() {
    print_status "Cleaning old problematic files..."
    
    if [ -d "$MODULE_PATH" ]; then
        # Remove old static template files that might cause XML issues
        find "$MODULE_PATH" -name "*.xml" -path "*/static/*" -delete 2>/dev/null || true
        
        # Remove old view files that are not in our manifest
        rm -f "$MODULE_PATH/views/calendar_department_group_views.xml" 2>/dev/null || true
        rm -f "$MODULE_PATH/views/calendar_event_type_views.xml" 2>/dev/null || true
        rm -f "$MODULE_PATH/views/calendar_resource_views.xml" 2>/dev/null || true
        rm -f "$MODULE_PATH/views/calendar_template_views.xml" 2>/dev/null || true
        rm -f "$MODULE_PATH/views/calendar_meeting_wizard_views.xml" 2>/dev/null || true
        rm -f "$MODULE_PATH/views/calendar_internal_meeting_views.xml" 2>/dev/null || true
        
        # Remove old wizard files
        rm -rf "$MODULE_PATH/wizards" 2>/dev/null || true
        
        # Remove old data files not in our manifest
        rm -f "$MODULE_PATH/data/calendar_data.xml" 2>/dev/null || true
        rm -f "$MODULE_PATH/data/email_templates.xml" 2>/dev/null || true
        
        # Remove old security files
        rm -f "$MODULE_PATH/security/calendar_extended_security.xml" 2>/dev/null || true
        
        # Remove old model files that might have conflicts
        rm -f "$MODULE_PATH/models/calendar_event.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/calendar_event_type.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/calendar_resource.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/calendar_template.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/calendar_reminder.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/res_partner.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/calendar_internal_meeting.py" 2>/dev/null || true
        rm -f "$MODULE_PATH/models/calendar_meeting_attendee.py" 2>/dev/null || true
        
        print_success "Old problematic files removed"
    else
        print_warning "Module path not found: $MODULE_PATH"
    fi
}

# Function to clean Python cache
clean_python_cache() {
    print_status "Cleaning Python cache files..."
    
    # Remove __pycache__ directories
    find "$ODOO_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove .pyc files
    find "$ODOO_PATH" -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove .pyo files
    find "$ODOO_PATH" -name "*.pyo" -delete 2>/dev/null || true
    
    print_success "Python cache cleaned"
}

# Function to validate XML files
validate_xml_files() {
    print_status "Validating XML files..."
    
    if [ -d "$MODULE_PATH" ]; then
        # Check all XML files for syntax errors
        local xml_errors=0
        
        while IFS= read -r -d '' xml_file; do
            if ! xmllint --noout "$xml_file" 2>/dev/null; then
                print_error "XML syntax error in: $xml_file"
                xml_errors=$((xml_errors + 1))
            fi
        done < <(find "$MODULE_PATH" -name "*.xml" -print0)
        
        if [ $xml_errors -eq 0 ]; then
            print_success "All XML files are valid"
        else
            print_error "Found $xml_errors XML files with errors"
            return 1
        fi
    fi
}

# Function to uninstall module completely
uninstall_module() {
    print_status "Uninstalling calendar_extended module completely..."
    
    # First try to uninstall via Odoo
    sudo -u "$ODOO_USER" "$PYTHON_BIN" "$ODOO_BIN" \
        -c "$ODOO_CONFIG" \
        --no-http \
        --stop-after-init \
        --uninstall "$MODULE_NAME" 2>/dev/null || {
        print_warning "Module uninstall failed or module was not installed"
    }
    
    # Clean database entries manually if needed
    DB_NAME=$(grep -E "^db_name\s*=" "$ODOO_CONFIG" | cut -d'=' -f2 | tr -d ' ' | head -1)
    
    if [ -n "$DB_NAME" ]; then
        print_status "Cleaning database entries for calendar_extended..."
        
        sudo -u postgres psql "$DB_NAME" <<EOF 2>/dev/null || true
-- Remove module records
DELETE FROM ir_module_module WHERE name = 'calendar_extended';
DELETE FROM ir_model_data WHERE module = 'calendar_extended';
DELETE FROM ir_attachment WHERE res_model LIKE '%calendar_extended%';

-- Remove any orphaned records
DELETE FROM ir_ui_view WHERE arch_db LIKE '%calendar_extended%';
DELETE FROM ir_ui_menu WHERE action LIKE '%calendar_extended%';
DELETE FROM ir_actions_act_window WHERE res_model LIKE '%calendar_extended%';

-- Clean up any custom model tables if they exist
DROP TABLE IF EXISTS calendar_announcement CASCADE;
DROP TABLE IF EXISTS calendar_department_select_wizard CASCADE;
DROP TABLE IF EXISTS calendar_send_invitation_wizard CASCADE;
DROP TABLE IF EXISTS calendar_reminder CASCADE;
DROP TABLE IF EXISTS calendar_reminder_template CASCADE;

COMMIT;
EOF
        
        print_success "Database cleaned"
    fi
}

# Function to reinstall module
install_module() {
    print_status "Installing calendar_extended module..."
    
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
        --install "$MODULE_NAME"
    
    print_success "Module installation completed"
}

# Function to check service status
check_service_status() {
    print_status "Checking Odoo service status..."
    
    if systemctl is-active --quiet odoo; then
        print_success "Odoo service is running"
        
        # Wait a bit and check if it's responding
        sleep 10
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069 | grep -q "200\|302\|301"; then
            print_success "Odoo is responding to HTTP requests"
        else
            print_warning "Odoo service is running but not responding to HTTP requests yet"
        fi
    else
        print_error "Odoo service is not running"
        systemctl status odoo --no-pager -l
        return 1
    fi
}

# Main execution function
main() {
    echo "================================================"
    echo "Calendar Extended Module Cleanup & Update Script"
    echo "================================================"
    
    check_permissions
    
    print_status "Starting cleanup and reinstallation process..."
    
    # Step 1: Stop Odoo
    stop_odoo
    
    # Step 2: Clean old problematic files
    clean_old_files
    
    # Step 3: Clean Python cache
    clean_python_cache
    
    # Step 4: Validate XML files
    validate_xml_files || {
        print_error "XML validation failed. Please fix XML errors first."
        exit 1
    }
    
    # Step 5: Uninstall module completely
    uninstall_module
    
    # Step 6: Start Odoo (needed for module operations)
    start_odoo
    
    # Step 7: Reinstall module
    install_module
    
    # Step 8: Check service status
    check_service_status
    
    print_success "Cleanup and reinstallation completed successfully!"
    print_status "The Calendar Extended module should now be working without XML errors."
    print_status "Check the Calendar menu for 'Meeting Announcements'"
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --clean-only        Only clean files and cache"
    echo "  --validate-only     Only validate XML files"
    echo ""
    echo "This script will:"
    echo "  1. Stop Odoo service"
    echo "  2. Remove old problematic XML and Python files"
    echo "  3. Clean Python cache"
    echo "  4. Validate XML syntax"
    echo "  5. Completely uninstall the module"
    echo "  6. Reinstall the module cleanly"
    echo "  7. Verify service is running"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --clean-only)
        print_status "Running cleanup only..."
        stop_odoo
        clean_old_files
        clean_python_cache
        start_odoo
        print_success "Cleanup completed!"
        exit 0
        ;;
    --validate-only)
        print_status "Validating XML files only..."
        validate_xml_files
        print_success "Validation completed!"
        exit 0
        ;;
    *)
        main
        ;;
esac
