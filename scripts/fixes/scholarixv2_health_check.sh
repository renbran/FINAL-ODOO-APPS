#!/bin/bash
# ScholarixV2 System Monitoring and Health Check
# Run this periodically to prevent serialization errors

echo "================================================"
echo "   ScholarixV2 Health Check & Monitoring"
echo "   Date: $(date)"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Check Odoo processes
echo -e "${YELLOW}1. Checking Odoo Processes...${NC}"
ODOO_PROCS=$(ps aux | grep "scholarixv2.*odoo-bin" | grep -v grep | wc -l)
if [ "$ODOO_PROCS" -gt 0 ]; then
    echo -e "${GREEN}✓ $ODOO_PROCS Odoo processes running${NC}"
    ps aux | grep "scholarixv2.*odoo-bin" | grep -v grep | head -3
else
    echo -e "${RED}✗ No Odoo processes found!${NC}"
fi
echo ""

# 2. Check database connections
echo -e "${YELLOW}2. Checking Database Connections...${NC}"
DB_CONN=$(sudo -u postgres psql -d scholarixv2 -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'scholarixv2';" 2>/dev/null | tr -d ' ')
if [ ! -z "$DB_CONN" ]; then
    if [ "$DB_CONN" -lt 50 ]; then
        echo -e "${GREEN}✓ Database connections: $DB_CONN (healthy)${NC}"
    elif [ "$DB_CONN" -lt 80 ]; then
        echo -e "${YELLOW}⚠ Database connections: $DB_CONN (moderate)${NC}"
    else
        echo -e "${RED}✗ Database connections: $DB_CONN (high!)${NC}"
    fi
else
    echo -e "${RED}✗ Cannot check database connections${NC}"
fi
echo ""

# 3. Check disk space
echo -e "${YELLOW}3. Checking Disk Space...${NC}"
DISK_USAGE=$(df -h /var/odoo/scholarixv2 | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓ Disk usage: ${DISK_USAGE}%${NC}"
else
    echo -e "${RED}✗ Disk usage: ${DISK_USAGE}% (cleanup needed!)${NC}"
fi
df -h /var/odoo/scholarixv2
echo ""

# 4. Check memory usage
echo -e "${YELLOW}4. Checking Memory Usage...${NC}"
free -h | head -2
echo ""

# 5. Check for recent errors
echo -e "${YELLOW}5. Checking for Recent Errors...${NC}"
ERROR_COUNT=$(grep -i "error\|critical\|serialization" /var/odoo/scholarixv2/logs/odoo-server.log 2>/dev/null | tail -100 | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No recent errors found${NC}"
else
    echo -e "${YELLOW}⚠ Found $ERROR_COUNT error entries in last 100 lines${NC}"
    echo "Last 5 errors:"
    grep -i "error\|critical" /var/odoo/scholarixv2/logs/odoo-server.log 2>/dev/null | tail -5
fi
echo ""

# 6. Check configuration
echo -e "${YELLOW}6. Current Configuration:${NC}"
echo "Workers: $(grep '^workers' /var/odoo/scholarixv2/odoo.conf 2>/dev/null || echo 'Not set')"
echo "Max Cron Threads: $(grep '^max_cron_threads' /var/odoo/scholarixv2/odoo.conf 2>/dev/null || echo 'Not set')"
echo "DB Max Connections: $(grep '^db_maxconn' /var/odoo/scholarixv2/odoo.conf 2>/dev/null || echo 'Not set')"
echo ""

# 7. Log rotation check
echo -e "${YELLOW}7. Checking Log Size...${NC}"
if [ -f /var/odoo/scholarixv2/logs/odoo-server.log ]; then
    LOG_SIZE=$(du -h /var/odoo/scholarixv2/logs/odoo-server.log | cut -f1)
    echo "Current log size: $LOG_SIZE"
else
    echo "Log file not found"
fi
echo ""

# 8. Recent activity
echo -e "${YELLOW}8. Recent Activity (Last 5 log entries):${NC}"
tail -5 /var/odoo/scholarixv2/logs/odoo-server.log 2>/dev/null || echo "Cannot read log file"
echo ""

echo "================================================"
echo -e "${GREEN}Health Check Complete!${NC}"
echo "================================================"
echo ""
echo "Recommendations:"
echo "- Keep database connections below 50"
echo "- Monitor disk space regularly"
echo "- Review errors weekly"
echo "- Backup config before changes"
echo ""
