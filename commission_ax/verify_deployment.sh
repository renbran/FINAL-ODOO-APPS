#!/bin/bash
# Commission AX Deployment Verification Script
# Run this on CloudPepper server to verify successful deployment

echo "=================================="
echo "Commission AX Deployment Verification"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
    fi
}

echo "1. Checking Module State on osusproperties database..."
MODULE_STATE=$(sudo -u postgres psql -d osusproperties -t -c "SELECT state FROM ir_module_module WHERE name='commission_ax';")
if [[ "$MODULE_STATE" == *"installed"* ]]; then
    print_status 0 "Module installed on osusproperties"
else
    print_status 1 "Module NOT installed on osusproperties (State: $MODULE_STATE)"
fi

echo ""
echo "2. Checking Module State on erposus database..."
MODULE_STATE_ERPOSUS=$(sudo -u postgres psql -d erposus -t -c "SELECT state FROM ir_module_module WHERE name='commission_ax';")
if [[ "$MODULE_STATE_ERPOSUS" == *"installed"* ]]; then
    print_status 0 "Module installed on erposus"
else
    print_status 1 "Module NOT installed on erposus (State: $MODULE_STATE_ERPOSUS)"
fi

echo ""
echo "3. Checking commission_id column in account_move..."
COLUMN_EXISTS=$(sudo -u postgres psql -d osusproperties -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='account_move' AND column_name='commission_id';")
if [[ "$COLUMN_EXISTS" == *"commission_id"* ]]; then
    print_status 0 "commission_id column exists in account_move"
else
    print_status 1 "commission_id column NOT found in account_move"
fi

echo ""
echo "4. Checking commission_lines_count in sale_order..."
COMMISSION_COUNT=$(sudo -u postgres psql -d osusproperties -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='sale_order' AND column_name LIKE '%commission%';")
if [ "$COMMISSION_COUNT" -gt 5 ]; then
    print_status 0 "Commission fields exist in sale_order (Found: $COMMISSION_COUNT fields)"
else
    print_status 1 "Commission fields missing in sale_order (Found only: $COMMISSION_COUNT fields)"
fi

echo ""
echo "5. Checking Odoo Service Status..."
SERVICE_STATUS=$(systemctl is-active odona-osusproperties.service)
if [ "$SERVICE_STATUS" == "active" ]; then
    print_status 0 "Odoo service is running"
else
    print_status 1 "Odoo service is NOT running (Status: $SERVICE_STATUS)"
fi

echo ""
echo "6. Checking Recent Errors in Logs..."
ERROR_COUNT=$(tail -100 /var/odoo/osusproperties/logs/odoo-server.log | grep -c "ERROR.*commission_ax")
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_status 0 "No commission_ax errors in recent logs"
else
    print_status 1 "Found $ERROR_COUNT commission_ax errors in recent logs"
    echo -e "${YELLOW}Recent Errors:${NC}"
    tail -100 /var/odoo/osusproperties/logs/odoo-server.log | grep "ERROR.*commission_ax" | tail -5
fi

echo ""
echo "7. Checking Database Index..."
INDEX_EXISTS=$(sudo -u postgres psql -d osusproperties -t -c "SELECT indexname FROM pg_indexes WHERE tablename='account_move' AND indexname='account_move_commission_id_index';")
if [[ "$INDEX_EXISTS" == *"account_move_commission_id_index"* ]]; then
    print_status 0 "commission_id index exists"
else
    print_status 1 "commission_id index NOT found"
fi

echo ""
echo "=================================="
echo "Verification Complete"
echo "=================================="
echo ""
echo "Module Version Information:"
sudo -u postgres psql -d osusproperties -c "SELECT name, state, latest_version, published_version FROM ir_module_module WHERE name='commission_ax';"

echo ""
echo "Service Status:"
systemctl status odona-osusproperties.service --no-pager | head -10

echo ""
echo "Recent Log Entries:"
tail -20 /var/odoo/osusproperties/logs/odoo-server.log | grep -E "INFO|WARNING|ERROR" | tail -10

echo ""
echo "=================================="
echo "Next Steps:"
echo "1. Test frontend: https://erposus.com"
echo "2. Navigate to Sales → Orders"
echo "3. Open sale order with commissions"
echo "4. Verify commission_lines_count field displays"
echo "5. Check browser console for RPC errors"
echo "=================================="
