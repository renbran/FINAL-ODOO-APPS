#!/bin/bash
# Fix Serialization Error for ScholarixV2 Odoo Instance
# Date: December 2, 2025
# Issue: psycopg2.errors.SerializationFailure - concurrent database updates

set -e  # Exit on error

echo "=========================================="
echo "ScholarixV2 Serialization Error Fix"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check current Odoo processes
echo -e "${YELLOW}Step 1: Checking for running Odoo processes...${NC}"
ps aux | grep -i odoo | grep -v grep || echo "No Odoo processes found"
echo ""

# Step 2: Stop Odoo service (try both systemd and direct process)
echo -e "${YELLOW}Step 2: Stopping Odoo service...${NC}"
if systemctl is-active --quiet odoo 2>/dev/null; then
    echo "Stopping Odoo via systemd..."
    sudo systemctl stop odoo
    sleep 3
else
    echo "Systemd service not found, checking for direct processes..."
fi

# Kill any remaining Odoo processes
echo "Killing any remaining Odoo processes..."
sudo pkill -f odoo-bin || echo "No processes to kill"
sudo pkill -f "python.*odoo" || echo "No Python Odoo processes"
sleep 2

# Verify no processes remain
REMAINING=$(ps aux | grep -i odoo | grep -v grep | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo -e "${RED}Warning: $REMAINING Odoo processes still running!${NC}"
    ps aux | grep -i odoo | grep -v grep
    echo "Force killing..."
    sudo pkill -9 -f odoo-bin
    sleep 2
else
    echo -e "${GREEN}✓ All Odoo processes stopped${NC}"
fi
echo ""

# Step 3: Clear database connections
echo -e "${YELLOW}Step 3: Clearing database connections...${NC}"
sudo -u postgres psql -d scholarixv2 -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'scholarixv2' 
  AND pid <> pg_backend_pid()
  AND state = 'active';
" 2>/dev/null || echo "Database connections cleared (or none found)"
echo ""

# Step 4: Backup current config
echo -e "${YELLOW}Step 4: Backing up configuration...${NC}"
if [ -f /var/odoo/scholarixv2/odoo.conf ]; then
    sudo cp /var/odoo/scholarixv2/odoo.conf /var/odoo/scholarixv2/odoo.conf.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Config backed up${NC}"
else
    echo -e "${RED}Config file not found at /var/odoo/scholarixv2/odoo.conf${NC}"
fi
echo ""

# Step 5: Adjust worker settings temporarily
echo -e "${YELLOW}Step 5: Adjusting Odoo configuration for safe restart...${NC}"
if [ -f /var/odoo/scholarixv2/odoo.conf ]; then
    # Check if workers setting exists
    if grep -q "^workers" /var/odoo/scholarixv2/odoo.conf; then
        # Comment out existing workers line and add workers=0
        sudo sed -i.tmp '/^workers/s/^/; /' /var/odoo/scholarixv2/odoo.conf
        echo "workers = 0" | sudo tee -a /var/odoo/scholarixv2/odoo.conf > /dev/null
    else
        # Add workers=0 if not exists
        echo "workers = 0" | sudo tee -a /var/odoo/scholarixv2/odoo.conf > /dev/null
    fi
    
    # Set max_cron_threads to 0
    if grep -q "^max_cron_threads" /var/odoo/scholarixv2/odoo.conf; then
        sudo sed -i.tmp '/^max_cron_threads/s/^/; /' /var/odoo/scholarixv2/odoo.conf
    fi
    echo "max_cron_threads = 0" | sudo tee -a /var/odoo/scholarixv2/odoo.conf > /dev/null
    
    echo -e "${GREEN}✓ Configuration adjusted (workers=0, max_cron_threads=0)${NC}"
else
    echo -e "${RED}Cannot adjust config - file not found${NC}"
fi
echo ""

# Step 6: Start Odoo with updated config
echo -e "${YELLOW}Step 6: Starting Odoo with safe configuration...${NC}"
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --log-level=info > /var/odoo/scholarixv2/logs/startup.log 2>&1 &
ODOO_PID=$!
echo "Odoo started with PID: $ODOO_PID"
echo "Waiting for initialization (30 seconds)..."
sleep 30
echo ""

# Step 7: Check if Odoo is running
echo -e "${YELLOW}Step 7: Verifying Odoo status...${NC}"
if ps -p $ODOO_PID > /dev/null; then
    echo -e "${GREEN}✓ Odoo is running (PID: $ODOO_PID)${NC}"
else
    echo -e "${RED}✗ Odoo failed to start${NC}"
    echo "Last 50 lines of log:"
    tail -50 /var/odoo/scholarixv2/logs/odoo.log 2>/dev/null || tail -50 /var/odoo/scholarixv2/logs/startup.log
    exit 1
fi
echo ""

# Step 8: Check for errors in logs
echo -e "${YELLOW}Step 8: Checking for errors in logs...${NC}"
if grep -i "error\|critical\|serialization" /var/odoo/scholarixv2/logs/startup.log | tail -20; then
    echo -e "${YELLOW}Errors found in logs (showing last 20)${NC}"
else
    echo -e "${GREEN}✓ No critical errors in startup log${NC}"
fi
echo ""

# Step 9: Test database connection
echo -e "${YELLOW}Step 9: Testing database connection...${NC}"
sudo -u postgres psql -d scholarixv2 -c "SELECT count(*) FROM ir_module_module;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
fi
echo ""

# Final Summary
echo "=========================================="
echo -e "${GREEN}Fix Process Complete!${NC}"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Monitor logs: tail -f /var/odoo/scholarixv2/logs/odoo.log"
echo "2. Check Odoo web interface: http://your-server-ip:8069"
echo "3. If stable, restore normal worker config:"
echo "   - Edit /var/odoo/scholarixv2/odoo.conf"
echo "   - Set workers to appropriate value (e.g., 4-8)"
echo "   - Restart: sudo systemctl restart odoo"
echo ""
echo "Current Odoo PID: $ODOO_PID"
echo "Logs location: /var/odoo/scholarixv2/logs/"
echo ""
