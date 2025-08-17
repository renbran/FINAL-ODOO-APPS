#!/bin/bash

# =============================================================================
# ODOO MANAGEMENT SCRIPT - OLDOSUS INSTANCE
# =============================================================================

# Configuration Variables
ODOO_BASE="/var/odoo/oldosus"
ODOO_SRC="$ODOO_BASE/src"
ODOO_LOGS="$ODOO_BASE/logs"
ODOO_CONFIG="$ODOO_BASE/odoo.conf"
PYTHON_INTERPRETER="$ODOO_BASE/venv/bin/python3"
ODOO_USER="odoo"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}================================${NC}"
}

# Function to check if user has proper permissions
check_permissions() {
    if [[ $EUID -ne 0 ]] && ! groups | grep -q sudo; then
        print_error "This script requires sudo privileges"
        exit 1
    fi
}

# Function to check if Odoo paths exist
check_odoo_paths() {
    local paths_ok=true
    
    if [[ ! -d "$ODOO_BASE" ]]; then
        print_error "Odoo base directory not found: $ODOO_BASE"
        paths_ok=false
    fi
    
    if [[ ! -d "$ODOO_SRC" ]]; then
        print_error "Odoo source directory not found: $ODOO_SRC"
        paths_ok=false
    fi
    
    if [[ ! -d "$ODOO_LOGS" ]]; then
        print_warning "Logs directory not found: $ODOO_LOGS"
        read -p "Create logs directory? (y/n): " create_logs
        if [[ $create_logs == "y" || $create_logs == "Y" ]]; then
            sudo mkdir -p "$ODOO_LOGS"
            sudo chown "$ODOO_USER:$ODOO_USER" "$ODOO_LOGS"
            print_status "Created logs directory: $ODOO_LOGS"
        fi
    fi
    
    if [[ ! -f "$ODOO_CONFIG" ]]; then
        print_error "Odoo config file not found: $ODOO_CONFIG"
        paths_ok=false
    fi
    
    if [[ ! -f "$PYTHON_INTERPRETER" ]]; then
        print_error "Python interpreter not found: $PYTHON_INTERPRETER"
        paths_ok=false
    fi
    
    if [[ $paths_ok == false ]]; then
        print_error "Please check your Odoo installation paths"
        exit 1
    fi
    
    print_status "All Odoo paths verified successfully"
}

# Function 1: Update payment status in Odoo
update_payment_status() {
    print_header "UPDATING PAYMENT STATUS"
    
    local default_status="${1:-draft}"
    local new_status="${2:-posted}"
    
    print_status "Updating payment entries from '$default_status' to '$new_status'"
    
    # Create Python script for Odoo shell
    cat > /tmp/update_payments.py << EOF
# Update payment status script
import logging

_logger = logging.getLogger(__name__)

try:
    # Search for payment entries with default status
    payments = env['account.payment'].search([('state', '=', '$default_status')])
    
    if not payments:
        print("No payments found with status '$default_status'")
    else:
        updated_count = 0
        for payment in payments:
            try:
                if payment.state == '$default_status':
                    payment.write({'state': '$new_status'})
                    updated_count += 1
            except Exception as e:
                print(f"Error updating payment {payment.id}: {e}")
        
        print(f"Successfully updated {updated_count} payment entries")
        env.cr.commit()
        
except Exception as e:
    print(f"Error in payment update: {e}")
    env.cr.rollback()
EOF
    
    # Execute via Odoo shell
    cd "$ODOO_BASE" && sudo -u "$ODOO_USER" "$PYTHON_INTERPRETER" src/odoo-bin shell -c odoo.conf --shell-interface ipython < /tmp/update_payments.py
    
    # Clean up
    rm -f /tmp/update_payments.py
    print_status "Payment status update completed"
}

# Function 2: Apply decimal precision to monetary fields
apply_decimal_precision() {
    print_header "APPLYING DECIMAL PRECISION"
    
    local precision="${1:-2}"
    
    print_status "Applying $precision decimal precision to monetary fields"
    
    # Create Python script for decimal precision
    cat > /tmp/decimal_precision.py << EOF
# Decimal precision enforcement script
import logging

_logger = logging.getLogger(__name__)

try:
    # Update account move lines
    move_lines = env['account.move.line'].search([])
    updated_count = 0
    
    for line in move_lines:
        updates = {}
        
        # Round debit and credit to specified precision
        if line.debit:
            new_debit = round(line.debit, $precision)
            if new_debit != line.debit:
                updates['debit'] = new_debit
        
        if line.credit:
            new_credit = round(line.credit, $precision)
            if new_credit != line.credit:
                updates['credit'] = new_credit
        
        if line.amount_currency:
            new_amount = round(line.amount_currency, $precision)
            if new_amount != line.amount_currency:
                updates['amount_currency'] = new_amount
        
        if updates:
            line.write(updates)
            updated_count += 1
    
    print(f"Updated {updated_count} account move lines with proper decimal precision")
    
    # Update invoice lines
    invoice_lines = env['account.move.line'].search([('move_id.move_type', 'in', ['out_invoice', 'in_invoice'])])
    invoice_updated = 0
    
    for line in invoice_lines:
        if line.price_unit:
            new_price = round(line.price_unit, $precision)
            if new_price != line.price_unit:
                line.write({'price_unit': new_price})
                invoice_updated += 1
    
    print(f"Updated {invoice_updated} invoice lines with proper decimal precision")
    env.cr.commit()
    
except Exception as e:
    print(f"Error applying decimal precision: {e}")
    env.cr.rollback()
EOF
    
    # Execute via Odoo shell
    cd "$ODOO_BASE" && sudo -u "$ODOO_USER" "$PYTHON_INTERPRETER" src/odoo-bin shell -c odoo.conf --shell-interface ipython < /tmp/decimal_precision.py
    
    # Clean up
    rm -f /tmp/decimal_precision.py
    print_status "Decimal precision applied successfully"
}

# Function 3: Find and merge duplicate contacts
find_duplicate_contacts() {
    print_header "FINDING DUPLICATE CONTACTS"
    
    local threshold="${1:-80}"
    
    print_status "Searching for duplicate contacts with $threshold% similarity threshold"
    
    # Create Python script for finding duplicates
    cat > /tmp/find_duplicates.py << EOF
# Find duplicate contacts script
import logging
from difflib import SequenceMatcher

_logger = logging.getLogger(__name__)

def similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

try:
    partners = env['res.partner'].search([('is_company', '=', False)])
    duplicates = []
    
    print(f"Analyzing {len(partners)} contacts for duplicates...")
    
    for i, partner1 in enumerate(partners):
        for partner2 in partners[i+1:]:
            name_sim = similarity(partner1.name or '', partner2.name or '')
            email_sim = similarity(partner1.email or '', partner2.email or '')
            phone_sim = similarity(partner1.phone or '', partner2.phone or '')
            
            # Consider duplicate if name similarity is high OR email/phone match
            if (name_sim >= $threshold or 
                (email_sim >= 90 and partner1.email and partner2.email) or
                (phone_sim >= 90 and partner1.phone and partner2.phone)):
                
                duplicates.append({
                    'partner1': partner1,
                    'partner2': partner2,
                    'name_similarity': round(name_sim, 2),
                    'email_similarity': round(email_sim, 2),
                    'phone_similarity': round(phone_sim, 2)
                })
    
    if duplicates:
        print(f"\\nFound {len(duplicates)} potential duplicate pairs:")
        print("-" * 80)
        
        for i, dup in enumerate(duplicates):
            print(f"\\nDuplicate Pair {i+1}:")
            print(f"Contact 1 (ID: {dup['partner1'].id}): {dup['partner1'].name}")
            print(f"  Email: {dup['partner1'].email or 'N/A'}")
            print(f"  Phone: {dup['partner1'].phone or 'N/A'}")
            print(f"Contact 2 (ID: {dup['partner2'].id}): {dup['partner2'].name}")
            print(f"  Email: {dup['partner2'].email or 'N/A'}")
            print(f"  Phone: {dup['partner2'].phone or 'N/A'}")
            print(f"Similarities - Name: {dup['name_similarity']}% | Email: {dup['email_similarity']}% | Phone: {dup['phone_similarity']}%")
            print("-" * 40)
            
            # Save duplicate info to a CSV file for review
            with open('/tmp/odoo_duplicates.csv', 'a') as f:
                if i == 0:  # Write header only once
                    f.write("ID1,Name1,Email1,Phone1,ID2,Name2,Email2,Phone2,NameSim,EmailSim,PhoneSim\\n")
                f.write(f"{dup['partner1'].id},\"{dup['partner1'].name or ''}\",\"{dup['partner1'].email or ''}\",\"{dup['partner1'].phone or ''}\",")
                f.write(f"{dup['partner2'].id},\"{dup['partner2'].name or ''}\",\"{dup['partner2'].email or ''}\",\"{dup['partner2'].phone or ''}\",")
                f.write(f"{dup['name_similarity']},{dup['email_similarity']},{dup['phone_similarity']}\\n")
        
        print(f"\\nDuplicate report saved to: /tmp/odoo_duplicates.csv")
    else:
        print("No duplicate contacts found!")
        
except Exception as e:
    print(f"Error finding duplicates: {e}")
EOF
    
    # Remove existing duplicate report
    rm -f /tmp/odoo_duplicates.csv
    
    # Execute via Odoo shell
    cd "$ODOO_BASE" && sudo -u "$ODOO_USER" "$PYTHON_INTERPRETER" src/odoo-bin shell -c odoo.conf --shell-interface ipython < /tmp/find_duplicates.py
    
    # Clean up
    rm -f /tmp/find_duplicates.py
    
    if [[ -f /tmp/odoo_duplicates.csv ]]; then
        print_status "Duplicate contacts report generated: /tmp/odoo_duplicates.csv"
        echo "You can review the duplicates and manually merge them through Odoo interface"
    fi
}

# Odoo Management Functions
odoo_shell() {
    print_header "ODOO SHELL ACCESS"
    print_status "Opening Odoo shell..."
    cd "$ODOO_BASE" && sudo -u "$ODOO_USER" "$PYTHON_INTERPRETER" src/odoo-bin shell -c odoo.conf
}

update_all_modules() {
    print_header "UPDATING ALL MODULES"
    print_warning "This operation may take several minutes..."
    read -p "Are you sure you want to update all modules? (y/n): " confirm
    
    if [[ $confirm == "y" || $confirm == "Y" ]]; then
        print_status "Updating all Odoo modules..."
        cd "$ODOO_BASE" && sudo -u "$ODOO_USER" "$PYTHON_INTERPRETER" src/odoo-bin -c odoo.conf --no-http --stop-after-init --update all
        print_status "Module update completed"
    else
        print_status "Module update cancelled"
    fi
}

install_python_package() {
    local package_name="$1"
    
    if [[ -z "$package_name" ]]; then
        read -p "Enter package name to install: " package_name
    fi
    
    if [[ -n "$package_name" ]]; then
        print_header "INSTALLING PYTHON PACKAGE"
        print_status "Installing package: $package_name"
        sudo -u "$ODOO_USER" "$PYTHON_INTERPRETER" -m pip install "$package_name"
        print_status "Package installation completed"
    else
        print_error "No package name provided"
    fi
}

view_logs() {
    print_header "ODOO LOGS"
    echo "Available log files in $ODOO_LOGS:"
    ls -la "$ODOO_LOGS"
    echo ""
    read -p "Enter log file name to view (or press Enter to view latest): " log_file
    
    if [[ -z "$log_file" ]]; then
        log_file=$(ls -t "$ODOO_LOGS"/*.log 2>/dev/null | head -1)
    else
        log_file="$ODOO_LOGS/$log_file"
    fi
    
    if [[ -f "$log_file" ]]; then
        print_status "Viewing log file: $log_file"
        echo "Press 'q' to quit, Space for next page"
        less "$log_file"
    else
        print_error "Log file not found: $log_file"
    fi
}

backup_database() {
    print_header "DATABASE BACKUP"
    read -p "Enter database name: " db_name
    
    if [[ -n "$db_name" ]]; then
        backup_file="/tmp/odoo_backup_${db_name}_$(date +%Y%m%d_%H%M%S).sql"
        print_status "Creating backup: $backup_file"
        
        sudo -u postgres pg_dump "$db_name" > "$backup_file"
        
        if [[ $? -eq 0 ]]; then
            print_status "Backup created successfully: $backup_file"
        else
            print_error "Backup failed"
        fi
    else
        print_error "No database name provided"
    fi
}

# Show system status
show_status() {
    print_header "ODOO SYSTEM STATUS"
    
    echo -e "${BLUE}Paths:${NC}"
    echo "  Base Directory: $ODOO_BASE"
    echo "  Source: $ODOO_SRC"
    echo "  Logs: $ODOO_LOGS"
    echo "  Config: $ODOO_CONFIG"
    echo "  Python: $PYTHON_INTERPRETER"
    echo ""
    
    echo -e "${BLUE}Disk Usage:${NC}"
    df -h "$ODOO_BASE" 2>/dev/null || echo "  Cannot access $ODOO_BASE"
    echo ""
    
    echo -e "${BLUE}Recent Log Activity:${NC}"
    if [[ -d "$ODOO_LOGS" ]]; then
        find "$ODOO_LOGS" -name "*.log" -type f -mtime -1 2>/dev/null | head -5 | while read log; do
            echo "  $(basename "$log") - $(stat -c %y "$log" 2>/dev/null | cut -d' ' -f1,2)"
        done
    else
        echo "  No log directory found"
    fi
    echo ""
    
    echo -e "${BLUE}Odoo Process:${NC}"
    ps aux | grep -v grep | grep odoo | head -3 || echo "  No Odoo processes running"
}

# Interactive menu
show_menu() {
    echo ""
    echo -e "${PURPLE}=== ODOO MANAGEMENT TOOLS - OLDOSUS ===${NC}"
    echo "1.  Update payment status (draft to posted)"
    echo "2.  Apply 2 decimal precision to monetary fields"
    echo "3.  Find duplicate contacts with fuzzy matching"
    echo "4.  Open Odoo shell"
    echo "5.  Update all modules"
    echo "6.  Install Python package"
    echo "7.  View logs"
    echo "8.  Backup database"
    echo "9.  Show system status"
    echo "10. Exit"
    echo ""
}

# Main execution
main() {
    print_header "ODOO MANAGEMENT SCRIPT INITIALIZATION"
    
    # Check prerequisites
    check_permissions
    check_odoo_paths
    
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Choose an option (1-10): " choice
            
            case $choice in
                1)
                    read -p "Enter default status to change [draft]: " default_status
                    default_status=${default_status:-draft}
                    read -p "Enter new status [posted]: " new_status
                    new_status=${new_status:-posted}
                    update_payment_status "$default_status" "$new_status"
                    ;;
                2)
                    read -p "Enter decimal precision [2]: " precision
                    precision=${precision:-2}
                    apply_decimal_precision "$precision"
                    ;;
                3)
                    read -p "Enter similarity threshold % [80]: " threshold
                    threshold=${threshold:-80}
                    find_duplicate_contacts "$threshold"
                    ;;
                4)
                    odoo_shell
                    ;;
                5)
                    update_all_modules
                    ;;
                6)
                    install_python_package
                    ;;
                7)
                    view_logs
                    ;;
                8)
                    backup_database
                    ;;
                9)
                    show_status
                    ;;
                10)
                    print_status "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please try again."
                    ;;
            esac
        done
    else
        # Command line mode
        case "$1" in
            "update-payments")
                update_payment_status "$2" "$3"
                ;;
            "apply-precision")
                apply_decimal_precision "$2"
                ;;
            "find-duplicates")
                find_duplicate_contacts "$2"
                ;;
            "shell")
                odoo_shell
                ;;
            "update-modules")
                update_all_modules
                ;;
            "install-package")
                install_python_package "$2"
                ;;
            "backup")
                backup_database
                ;;
            "status")
                show_status
                ;;
            *)
                echo "Usage: $0 [command] [args...]"
                echo ""
                echo "Commands:"
                echo "  update-payments [default_status] [new_status]"
                echo "  apply-precision [decimal_places]"
                echo "  find-duplicates [threshold]"
                echo "  shell"
                echo "  update-modules"
                echo "  install-package [package_name]"
                echo "  backup"
                echo "  status"
                echo ""
                echo "Run without arguments for interactive mode"
                ;;
        esac
    fi
}

# Run main function with all arguments
main "$@"
