#!/bin/bash
# Payment Account Enhanced - Database Fix Deployment Script
# Server Environment: /var/odoo/osush/

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server paths
ODOO_BASE="/var/odoo/osush"
ODOO_SRC="$ODOO_BASE/src"
ODOO_CONFIG="$ODOO_BASE/odoo.conf"
ODOO_LOGS="$ODOO_BASE/logs"
EXTRA_ADDONS="$ODOO_BASE/extra-addons"
MODULE_PATH="$EXTRA_ADDONS/payment_account_enhanced"

echo -e "${BLUE}=== Payment Account Enhanced Database Fix ===${NC}"
echo -e "${BLUE}Server Environment: $ODOO_BASE${NC}"
echo ""

# Function to check if running as odoo user
check_user() {
    if [ "$USER" != "odoo" ]; then
        echo -e "${YELLOW}Warning: Not running as odoo user. Commands may need sudo.${NC}"
        SUDO_CMD="sudo -u odoo"
    else
        SUDO_CMD=""
    fi
}

# Function to backup database
backup_database() {
    echo -e "${YELLOW}Creating database backup...${NC}"
    BACKUP_FILE="$ODOO_LOGS/backup_payment_fix_$(date +%Y%m%d_%H%M%S).sql"
    sudo -u postgres pg_dump odoo > "$BACKUP_FILE"
    echo -e "${GREEN}✅ Database backup created: $BACKUP_FILE${NC}"
}

# Function to check if Odoo is running
check_odoo_status() {
    if systemctl is-active --quiet odoo 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Odoo service is running${NC}"
        return 0
    else
        echo -e "${GREEN}✅ Odoo service is stopped${NC}"
        return 1
    fi
}

# Function to stop Odoo service
stop_odoo() {
    echo -e "${YELLOW}Stopping Odoo service...${NC}"
    sudo systemctl stop odoo
    sleep 3
    echo -e "${GREEN}✅ Odoo service stopped${NC}"
}

# Function to start Odoo service
start_odoo() {
    echo -e "${YELLOW}Starting Odoo service...${NC}"
    sudo systemctl start odoo
    sleep 5
    sudo systemctl status odoo --no-pager
    echo -e "${GREEN}✅ Odoo service started${NC}"
}

# Function to fix database using Odoo shell
fix_with_odoo_shell() {
    echo -e "${YELLOW}Applying database fix using Odoo shell...${NC}"
    cd "$ODOO_BASE"
    
    # Create temporary script for Odoo shell
    cat << 'EOF' > /tmp/fix_payment_enhanced.py
# Load the fix script
exec(open('/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py').read())

# Execute the fix
try:
    fix_company_fields(env)
    print("✅ Database fix completed successfully!")
except Exception as e:
    print(f"❌ Error during fix: {e}")
    raise
EOF

    # Run the fix in Odoo shell
    $SUDO_CMD venv/bin/python3 src/odoo-bin shell -c odoo.conf < /tmp/fix_payment_enhanced.py
    
    # Clean up temporary script
    rm -f /tmp/fix_payment_enhanced.py
    
    echo -e "${GREEN}✅ Database fix applied using Odoo shell${NC}"
}

# Function to fix using module update
fix_with_module_update() {
    echo -e "${YELLOW}Applying fix using module update...${NC}"
    cd "$ODOO_BASE"
    
    $SUDO_CMD venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced
    
    echo -e "${GREEN}✅ Module update completed${NC}"
}

# Function to verify the fix
verify_fix() {
    echo -e "${YELLOW}Verifying database fix...${NC}"
    cd "$ODOO_BASE"
    
    # Create verification script
    cat << 'EOF' > /tmp/verify_payment_enhanced.py
# Check if columns exist
env.cr.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='res_company' 
    AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding')
    ORDER BY column_name
""")

columns = env.cr.fetchall()
if len(columns) == 3:
    print("✅ All required columns found:")
    for col_name, col_type in columns:
        print(f"  - {col_name}: {col_type}")
else:
    print(f"❌ Expected 3 columns, found {len(columns)}")
    for col_name, col_type in columns:
        print(f"  - {col_name}: {col_type}")
EOF

    # Run verification
    $SUDO_CMD venv/bin/python3 src/odoo-bin shell -c odoo.conf < /tmp/verify_payment_enhanced.py
    
    # Clean up
    rm -f /tmp/verify_payment_enhanced.py
    
    echo -e "${GREEN}✅ Verification completed${NC}"
}

# Function to monitor logs
monitor_logs() {
    echo -e "${YELLOW}Monitoring Odoo logs for errors...${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop monitoring${NC}"
    tail -f "$ODOO_LOGS/odoo.log" | grep -E "(ERROR|CRITICAL|payment_account_enhanced|res_company)" --color=always
}

# Main execution
main() {
    echo -e "${BLUE}Choose deployment method:${NC}"
    echo "1. Odoo Shell Fix (Recommended)"
    echo "2. Module Update"
    echo "3. Verify Fix Only"
    echo "4. Monitor Logs"
    echo "5. Full Deployment (Backup + Stop + Fix + Start + Verify)"
    
    read -p "Enter choice (1-5): " choice
    
    check_user
    
    case $choice in
        1)
            backup_database
            fix_with_odoo_shell
            verify_fix
            ;;
        2)
            backup_database
            fix_with_module_update
            verify_fix
            ;;
        3)
            verify_fix
            ;;
        4)
            monitor_logs
            ;;
        5)
            backup_database
            if check_odoo_status; then
                stop_odoo
                RESTART_NEEDED=true
            else
                RESTART_NEEDED=false
            fi
            
            fix_with_odoo_shell
            verify_fix
            
            if [ "$RESTART_NEEDED" = true ]; then
                start_odoo
                echo -e "${YELLOW}Waiting 10 seconds before monitoring logs...${NC}"
                sleep 10
                timeout 30s tail -f "$ODOO_LOGS/odoo.log" | grep -E "(ERROR|payment_account_enhanced)" || true
            fi
            
            echo -e "${GREEN}🎉 Full deployment completed successfully!${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
}

# Check prerequisites
if [ ! -d "$ODOO_BASE" ]; then
    echo -e "${RED}❌ Odoo base directory not found: $ODOO_BASE${NC}"
    exit 1
fi

if [ ! -f "$ODOO_CONFIG" ]; then
    echo -e "${RED}❌ Odoo config file not found: $ODOO_CONFIG${NC}"
    exit 1
fi

if [ ! -f "$MODULE_PATH/fix_company_fields.py" ]; then
    echo -e "${RED}❌ Fix script not found: $MODULE_PATH/fix_company_fields.py${NC}"
    exit 1
fi

# Run main function
main

echo -e "${GREEN}✅ Script execution completed${NC}"
