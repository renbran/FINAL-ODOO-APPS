#!/bin/bash
# Complete Commission AX Verification Script
# Checks all bugfixes: commission_lines_count, commission_id, is_fully_invoiced

echo "=========================================="
echo "Commission AX Complete Verification"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
    fi
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Database to check
DATABASES=("osusproperties" "erposus")

for DB in "${DATABASES[@]}"; do
    print_section "Database: $DB"
    
    # 1. Module Status
    echo "1. Checking module status..."
    MODULE_STATE=$(sudo -u postgres psql -d $DB -t -c "SELECT state FROM ir_module_module WHERE name='commission_ax';")
    if [[ "$MODULE_STATE" == *"installed"* ]]; then
        print_status 0 "Module is installed"
    else
        print_status 1 "Module NOT installed (State: $MODULE_STATE)"
    fi
    
    # 2. commission_lines_count field
    echo ""
    echo "2. Checking commission_lines_count field..."
    COUNT_FIELD=$(sudo -u postgres psql -d $DB -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='commission_lines_count';")
    if [[ "$COUNT_FIELD" == *"commission_lines_count"* ]]; then
        print_status 0 "commission_lines_count field exists"
    else
        print_status 1 "commission_lines_count field MISSING"
    fi
    
    # 3. commission_id column
    echo ""
    echo "3. Checking commission_id column in account_move..."
    COMM_ID=$(sudo -u postgres psql -d $DB -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='account_move' AND column_name='commission_id';")
    if [[ "$COMM_ID" == *"commission_id"* ]]; then
        print_status 0 "commission_id column exists"
        
        # Check index
        INDEX_EXISTS=$(sudo -u postgres psql -d $DB -t -c "SELECT indexname FROM pg_indexes WHERE tablename='account_move' AND indexname='account_move_commission_id_index';")
        if [[ "$INDEX_EXISTS" == *"account_move_commission_id_index"* ]]; then
            print_status 0 "commission_id index exists"
        else
            print_status 1 "commission_id index MISSING"
        fi
    else
        print_status 1 "commission_id column MISSING"
    fi
    
    # 4. is_fully_invoiced field
    echo ""
    echo "4. Checking is_fully_invoiced field..."
    INVOICE_FIELD=$(sudo -u postgres psql -d $DB -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='is_fully_invoiced';")
    if [[ "$INVOICE_FIELD" == *"is_fully_invoiced"* ]]; then
        print_status 0 "is_fully_invoiced field exists"
    else
        print_status 1 "is_fully_invoiced field MISSING"
    fi
    
    # 5. Count all commission fields
    echo ""
    echo "5. Counting all commission-related fields..."
    COMM_COUNT=$(sudo -u postgres psql -d $DB -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='sale_order' AND column_name LIKE '%commission%';")
    if [ "$COMM_COUNT" -gt 25 ]; then
        print_status 0 "Found $COMM_COUNT commission fields"
    else
        print_status 1 "Only found $COMM_COUNT commission fields (expected 30+)"
    fi
    
    echo ""
done

# Service Status
print_section "Service Status"
SERVICE_STATUS=$(systemctl is-active odona-osusproperties.service)
if [ "$SERVICE_STATUS" == "active" ]; then
    print_status 0 "Odoo service is running"
    
    # Check workers
    WORKER_COUNT=$(ps aux | grep -E 'odoo-bin.*osusproperties' | grep -v grep | wc -l)
    print_status 0 "Found $WORKER_COUNT Odoo workers"
else
    print_status 1 "Odoo service is NOT running (Status: $SERVICE_STATUS)"
fi

# Log Analysis
print_section "Log Analysis"
echo "Checking for errors in last 100 log lines..."

ERROR_COUNT=$(tail -100 /var/odoo/osusproperties/logs/odoo-server.log | grep -c "ERROR.*commission_ax")
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_status 0 "No commission_ax errors in logs"
else
    print_status 1 "Found $ERROR_COUNT commission_ax errors"
    echo -e "${YELLOW}Recent errors:${NC}"
    tail -100 /var/odoo/osusproperties/logs/odoo-server.log | grep "ERROR.*commission_ax" | tail -3
fi

UNDEFINED_FIELD_ERRORS=$(tail -100 /var/odoo/osusproperties/logs/odoo-server.log | grep -c "field is undefined")
if [ "$UNDEFINED_FIELD_ERRORS" -eq 0 ]; then
    print_status 0 "No 'field is undefined' errors"
else
    print_status 1 "Found $UNDEFINED_FIELD_ERRORS 'field is undefined' errors"
fi

# Summary
print_section "Verification Summary"

echo ""
echo "Module Version:"
sudo -u postgres psql -d osusproperties -c "SELECT name, state, latest_version FROM ir_module_module WHERE name='commission_ax';"

echo ""
echo "Critical Fields Status:"
echo "+-------------------------+---------------+---------+"
echo "| Field                   | osusproperties | erposus |"
echo "+-------------------------+---------------+---------+"

# commission_lines_count
OSUS_COUNT=$(sudo -u postgres psql -d osusproperties -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='commission_lines_count';" | wc -l)
ERP_COUNT=$(sudo -u postgres psql -d erposus -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='commission_lines_count';" | wc -l)
printf "| %-23s | %-13s | %-7s |\n" "commission_lines_count" "$([ $OSUS_COUNT -gt 0 ] && echo '✅' || echo '❌')" "$([ $ERP_COUNT -gt 0 ] && echo '✅' || echo '❌')"

# commission_id
OSUS_ID=$(sudo -u postgres psql -d osusproperties -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='account_move' AND column_name='commission_id';" | wc -l)
ERP_ID=$(sudo -u postgres psql -d erposus -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='account_move' AND column_name='commission_id';" | wc -l)
printf "| %-23s | %-13s | %-7s |\n" "commission_id" "$([ $OSUS_ID -gt 0 ] && echo '✅' || echo '❌')" "$([ $ERP_ID -gt 0 ] && echo '✅' || echo '❌')"

# is_fully_invoiced
OSUS_INV=$(sudo -u postgres psql -d osusproperties -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='is_fully_invoiced';" | wc -l)
ERP_INV=$(sudo -u postgres psql -d erposus -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name='is_fully_invoiced';" | wc -l)
printf "| %-23s | %-13s | %-7s |\n" "is_fully_invoiced" "$([ $OSUS_INV -gt 0 ] && echo '✅' || echo '❌')" "$([ $ERP_INV -gt 0 ] && echo '✅' || echo '❌')"

echo "+-------------------------+---------------+---------+"

echo ""
print_section "Testing Recommendations"
echo ""
echo "1. Frontend Testing:"
echo "   URL: https://erposus.com"
echo "   Test: Sales → Orders → Open any order"
echo "   Verify: No RPC errors in browser console (F12)"
echo ""
echo "2. Commission Calculation:"
echo "   Test: Create/edit order with commission partners"
echo "   Verify: commission_lines_count displays correct number"
echo ""
echo "3. Invoice Status:"
echo "   Test: Create and validate invoice for order"
echo "   Verify: is_fully_invoiced updates correctly"
echo ""
echo "4. Account Move Commission:"
echo "   Test: Create vendor bill with commission reference"
echo "   Verify: commission_id field is accessible"
echo ""

print_section "All Checks Complete"
echo ""
echo "Status: $(date)"
echo "=========================================="
