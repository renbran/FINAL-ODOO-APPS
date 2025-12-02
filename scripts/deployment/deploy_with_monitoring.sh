#!/bin/bash
# ============================================================================
# RENTAL MANAGEMENT MODULE v3.4.0 DEPLOYMENT SCRIPT
# ============================================================================
# Purpose: Deploy rental_management v3.4.0 to CloudPepper with monitoring
# Database: scholarixv2
# Server: 139.84.163.11
# Features: Pre-deployment checks, backup, deployment, monitoring, rollback
# ============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MODULE_NAME="rental_management"
MODULE_VERSION="3.4.0"
MODULE_PATH="/opt/odoo/addons/$MODULE_NAME"
ODOO_PATH="/opt/odoo"
ODOO_CONFIG="/etc/odoo/odoo.conf"
BACKUP_PATH="/opt/backups"
LOG_DIR="/var/log/odoo"
DATABASE="scholarixv2"
ODOO_PORT="8069"
MONITORING_LOG="/tmp/deployment_monitor.log"

# Ensure backup directory exists
mkdir -p $BACKUP_PATH

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  RENTAL MANAGEMENT v3.4.0 - DEPLOYMENT & MONITORING${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# PHASE 1: PRE-DEPLOYMENT CHECKS
# ============================================================================
echo -e "${BLUE}PHASE 1: PRE-DEPLOYMENT CHECKS${NC}"
echo ""

# Check if running as appropriate user
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Running as root${NC}"
else
    echo -e "${GREEN}✅ Running as user: $(whoami)${NC}"
fi

# Check module exists locally
if [ ! -d "$MODULE_PATH" ]; then
    echo -e "${RED}❌ Module not found at: $MODULE_PATH${NC}"
    echo "Please ensure the module has been transferred to $MODULE_PATH"
    exit 1
fi
echo -e "${GREEN}✅ Module found at: $MODULE_PATH${NC}"

# Check module version
if grep -q '"version": "3.4.0"' "$MODULE_PATH/__manifest__.py"; then
    echo -e "${GREEN}✅ Module version verified: 3.4.0${NC}"
else
    echo -e "${RED}❌ Module version not 3.4.0${NC}"
    grep '"version"' "$MODULE_PATH/__manifest__.py"
    exit 1
fi

# Check Odoo service status
echo ""
echo -e "${BLUE}Checking Odoo service status...${NC}"
if systemctl is-active --quiet odoo; then
    echo -e "${GREEN}✅ Odoo service is running${NC}"
    ODOO_WAS_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Odoo service is not running${NC}"
    ODOO_WAS_RUNNING=false
fi

# Check database connectivity
echo ""
echo -e "${BLUE}Checking database connectivity...${NC}"
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is accessible${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not accessible${NC}"
    exit 1
fi

# Check disk space
echo ""
echo -e "${BLUE}Checking available disk space...${NC}"
AVAILABLE_SPACE=$(df /opt | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_SPACE" -gt 1000000 ]; then
    echo -e "${GREEN}✅ Sufficient disk space available: $(($AVAILABLE_SPACE / 1024 / 1024))GB${NC}"
else
    echo -e "${RED}❌ Low disk space available: $(($AVAILABLE_SPACE / 1024))MB${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All pre-deployment checks passed!${NC}"

# ============================================================================
# PHASE 2: BACKUP EXISTING MODULE & DATABASE
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 2: BACKUP EXISTING MODULE & DATABASE${NC}"
echo ""

BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MODULE_BACKUP="$BACKUP_PATH/${MODULE_NAME}_${BACKUP_TIMESTAMP}.tar.gz"
DB_BACKUP="$BACKUP_PATH/${DATABASE}_${BACKUP_TIMESTAMP}.sql.gz"

# Backup existing module
if [ -d "$MODULE_PATH" ]; then
    echo -e "${BLUE}Backing up existing module...${NC}"
    tar -czf "$MODULE_BACKUP" -C "$(dirname $MODULE_PATH)" "$MODULE_NAME" 2>/dev/null || true
    if [ -f "$MODULE_BACKUP" ]; then
        echo -e "${GREEN}✅ Module backup created: $MODULE_BACKUP${NC}"
        echo "   Size: $(du -h $MODULE_BACKUP | cut -f1)"
    fi
fi

# Backup database
echo -e "${BLUE}Backing up database...${NC}"
pg_dump -U odoo "$DATABASE" 2>/dev/null | gzip > "$DB_BACKUP"
if [ -f "$DB_BACKUP" ]; then
    echo -e "${GREEN}✅ Database backup created: $DB_BACKUP${NC}"
    echo "   Size: $(du -h $DB_BACKUP | cut -f1)"
else
    echo -e "${RED}❌ Database backup failed${NC}"
    exit 1
fi

# Store backup info for rollback
ROLLBACK_INFO="/tmp/deployment_${BACKUP_TIMESTAMP}.info"
cat > "$ROLLBACK_INFO" << EOF
DEPLOYMENT_TIMESTAMP=$BACKUP_TIMESTAMP
MODULE_BACKUP=$MODULE_BACKUP
DB_BACKUP=$DB_BACKUP
MODULE_PATH=$MODULE_PATH
DATABASE=$DATABASE
DEPLOYMENT_DATE=$(date)
EOF
echo -e "${GREEN}✅ Rollback information saved: $ROLLBACK_INFO${NC}"

# ============================================================================
# PHASE 3: STOP ODOO SERVICE
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 3: STOPPING ODOO SERVICE${NC}"
echo ""

if [ "$ODOO_WAS_RUNNING" = true ]; then
    echo -e "${BLUE}Stopping Odoo service...${NC}"
    systemctl stop odoo
    
    # Wait for graceful shutdown
    sleep 5
    
    if systemctl is-active --quiet odoo; then
        echo -e "${RED}❌ Odoo did not stop gracefully, forcing...${NC}"
        killall -9 python3 2>/dev/null || true
        sleep 2
    else
        echo -e "${GREEN}✅ Odoo service stopped${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Odoo service was not running, skipping stop${NC}"
fi

# ============================================================================
# PHASE 4: CLEAR PYTHON CACHE
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 4: CLEARING PYTHON CACHE${NC}"
echo ""

echo -e "${BLUE}Removing __pycache__ directories...${NC}"
find "$MODULE_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Python cache cleared${NC}"

# ============================================================================
# PHASE 5: UPDATE MODULE
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 5: UPDATING RENTAL_MANAGEMENT MODULE${NC}"
echo ""

echo -e "${BLUE}Starting Odoo with module update...${NC}"
echo "Running: /opt/odoo/odoo-bin -u $MODULE_NAME -d $DATABASE --stop-after-init"
echo ""

# Start logging
{
    echo "=== Module Update Started: $(date) ==="
    echo "Database: $DATABASE"
    echo "Module: $MODULE_NAME (v3.4.0)"
    echo ""
} > "$MONITORING_LOG"

# Run update
timeout 300 /opt/odoo/odoo-bin -u "$MODULE_NAME" -d "$DATABASE" --stop-after-init >> "$MONITORING_LOG" 2>&1 || UPDATE_STATUS=$?

if [ -z "$UPDATE_STATUS" ]; then
    UPDATE_STATUS=0
fi

# Check update result
if grep -q "update_rental_management" "$LOG_DIR/odoo.log" 2>/dev/null || grep -q "module updated\|module installed" "$MONITORING_LOG" 2>/dev/null; then
    echo -e "${GREEN}✅ Module update completed successfully${NC}"
    UPDATE_SUCCESS=true
elif [ "$UPDATE_STATUS" -eq 0 ]; then
    echo -e "${GREEN}✅ Module update command completed (status: 0)${NC}"
    UPDATE_SUCCESS=true
else
    echo -e "${YELLOW}⚠️  Module update returned status: $UPDATE_STATUS${NC}"
    UPDATE_SUCCESS=false
fi

# ============================================================================
# PHASE 6: RESTART ODOO SERVICE
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 6: RESTARTING ODOO SERVICE${NC}"
echo ""

echo -e "${BLUE}Starting Odoo service...${NC}"
systemctl start odoo

# Wait for service to start
echo -e "${BLUE}Waiting for Odoo to start (max 30 seconds)...${NC}"
COUNTER=0
while [ $COUNTER -lt 30 ]; do
    if systemctl is-active --quiet odoo; then
        echo -e "${GREEN}✅ Odoo service started successfully${NC}"
        sleep 3  # Wait for full initialization
        break
    fi
    sleep 1
    COUNTER=$((COUNTER + 1))
done

if [ $COUNTER -ge 30 ]; then
    echo -e "${RED}❌ Odoo service failed to start within 30 seconds${NC}"
    UPDATE_SUCCESS=false
fi

# ============================================================================
# PHASE 7: VERIFY DEPLOYMENT
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 7: VERIFYING DEPLOYMENT${NC}"
echo ""

# Check if Odoo is responding
echo -e "${BLUE}Checking Odoo HTTP endpoint (port $ODOO_PORT)...${NC}"
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$ODOO_PORT" | grep -q "200\|302"; then
    echo -e "${GREEN}✅ Odoo is responding on port $ODOO_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  Odoo not responding immediately (may still be initializing)${NC}"
fi

# Check module in manifest
echo -e "${BLUE}Verifying module files...${NC}"
if [ -f "$MODULE_PATH/__manifest__.py" ]; then
    MODULE_VERSION_INSTALLED=$(grep '"version"' "$MODULE_PATH/__manifest__.py" | grep -o '"[^"]*"' | head -1 | tr -d '"')
    echo -e "${GREEN}✅ Module manifest found - Version: $MODULE_VERSION_INSTALLED${NC}"
else
    echo -e "${RED}❌ Module manifest not found${NC}"
    UPDATE_SUCCESS=false
fi

# ============================================================================
# PHASE 8: LOG ANALYSIS & MONITORING
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 8: LOG ANALYSIS & MONITORING${NC}"
echo ""

echo -e "${BLUE}Analyzing recent log entries...${NC}"
echo ""

# Check for errors in recent logs
if tail -100 "$LOG_DIR/odoo.log" 2>/dev/null | grep -i "error\|traceback" | head -5; then
    echo -e "${YELLOW}⚠️  Recent errors detected in logs${NC}"
else
    echo -e "${GREEN}✅ No critical errors in recent logs${NC}"
fi

# Check module loading
echo ""
echo -e "${BLUE}Checking module status in database...${NC}"
psql -U odoo -d "$DATABASE" -t -c "SELECT name, state, installed_version FROM ir_module_module WHERE name='$MODULE_NAME';" 2>/dev/null || echo "Could not query database directly"

# ============================================================================
# PHASE 9: MONITORING SETUP
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 9: SETTING UP MONITORING${NC}"
echo ""

# Create monitoring script
MONITOR_SCRIPT="/opt/monitoring/check_rental_management.sh"
mkdir -p /opt/monitoring 2>/dev/null || true

cat > "$MONITOR_SCRIPT" << 'MONITOR_EOF'
#!/bin/bash
# Monitor rental_management module health

HEALTH_CHECK_INTERVAL=300  # 5 minutes
MAX_FAILURES=3
FAILURE_COUNT=0

while true; do
    echo "[$(date)] Checking rental_management module..."
    
    # Check Odoo service
    if ! systemctl is-active --quiet odoo; then
        echo "[$(date)] ERROR: Odoo service is down!"
        ((FAILURE_COUNT++))
    else
        FAILURE_COUNT=0
    fi
    
    # Check HTTP endpoint
    if ! curl -s -f "http://localhost:8069" > /dev/null 2>&1; then
        echo "[$(date)] WARNING: Odoo HTTP endpoint not responding"
        ((FAILURE_COUNT++))
    fi
    
    # Check module in database
    psql -U odoo -d scholarixv2 -t -c "SELECT state FROM ir_module_module WHERE name='rental_management';" 2>/dev/null | grep -q "installed" || {
        echo "[$(date)] WARNING: rental_management module status unclear"
    }
    
    if [ $FAILURE_COUNT -ge $MAX_FAILURES ]; then
        echo "[$(date)] CRITICAL: Multiple failures detected - consider rollback!"
        # Could trigger alert/notification here
    fi
    
    sleep $HEALTH_CHECK_INTERVAL
done
MONITOR_EOF

chmod +x "$MONITOR_SCRIPT" 2>/dev/null || true
echo -e "${GREEN}✅ Monitoring script created: $MONITOR_SCRIPT${NC}"

# ============================================================================
# PHASE 10: ROLLBACK READINESS
# ============================================================================
echo ""
echo -e "${BLUE}PHASE 10: ROLLBACK READINESS${NC}"
echo ""

# Create rollback script
ROLLBACK_SCRIPT="/opt/rollback/rollback_rental_management_${BACKUP_TIMESTAMP}.sh"
mkdir -p /opt/rollback 2>/dev/null || true

cat > "$ROLLBACK_SCRIPT" << ROLLBACK_EOF
#!/bin/bash
# Rollback rental_management module to previous version
# Generated: $(date)

set -e

echo "=========================================="
echo "ROLLBACK: rental_management module"
echo "Backup Timestamp: $BACKUP_TIMESTAMP"
echo "=========================================="
echo ""

MODULE_BACKUP="$MODULE_BACKUP"
DB_BACKUP="$DB_BACKUP"
MODULE_PATH="$MODULE_PATH"
DATABASE="$DATABASE"

echo "[1/4] Stopping Odoo service..."
systemctl stop odoo
sleep 3
killall -9 python3 2>/dev/null || true
sleep 2

echo "[2/4] Restoring database from backup..."
psql -U odoo -d template1 -c "DROP DATABASE IF EXISTS $DATABASE;" 2>/dev/null || true
psql -U odoo -d template1 -c "CREATE DATABASE $DATABASE;" 2>/dev/null
gunzip -c "$DB_BACKUP" | psql -U odoo "$DATABASE" > /dev/null 2>&1
echo "✅ Database restored"

echo "[3/4] Restoring module from backup..."
rm -rf "$MODULE_PATH" 2>/dev/null || true
tar -xzf "$MODULE_BACKUP" -C "$(dirname $MODULE_PATH)"
echo "✅ Module restored"

echo "[4/4] Starting Odoo service..."
systemctl start odoo
sleep 5

if systemctl is-active --quiet odoo; then
    echo "✅ Rollback completed successfully!"
    echo "   Database: $DATABASE"
    echo "   Module: rental_management"
    systemctl status odoo --no-pager
else
    echo "❌ Odoo service failed to start after rollback"
    exit 1
fi
ROLLBACK_EOF

chmod +x "$ROLLBACK_SCRIPT" 2>/dev/null || true
echo -e "${GREEN}✅ Rollback script created: $ROLLBACK_SCRIPT${NC}"
echo -e "${YELLOW}   Use this to rollback if issues occur${NC}"

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  DEPLOYMENT SUMMARY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Deployment Status:${NC}"
if [ "$UPDATE_SUCCESS" = true ]; then
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL${NC}"
else
    echo -e "${RED}❌ DEPLOYMENT ISSUES DETECTED${NC}"
fi

echo ""
echo -e "${BLUE}Deployment Details:${NC}"
echo "  Module: $MODULE_NAME"
echo "  Version: $MODULE_VERSION"
echo "  Database: $DATABASE"
echo "  Timestamp: $BACKUP_TIMESTAMP"
echo ""

echo -e "${BLUE}Backup Information:${NC}"
echo "  Module Backup: $MODULE_BACKUP"
echo "  Database Backup: $DB_BACKUP"
echo "  Rollback Info: $ROLLBACK_INFO"
echo ""

echo -e "${BLUE}Rollback Command (if needed):${NC}"
echo -e "${YELLOW}  sudo bash $ROLLBACK_SCRIPT${NC}"
echo ""

echo -e "${BLUE}Monitoring:${NC}"
echo "  Log File: $MONITORING_LOG"
echo "  Monitor Script: $MONITOR_SCRIPT"
echo "  Check Logs: tail -f $LOG_DIR/odoo.log"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Monitor Odoo logs for the next 15 minutes"
echo "  2. Test rental_management features (SPA generation, payment plans)"
echo "  3. If issues occur, run rollback script"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Save summary
{
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "Date: $(date)"
    echo "Module: $MODULE_NAME v$MODULE_VERSION"
    echo "Database: $DATABASE"
    echo "Status: $([ "$UPDATE_SUCCESS" = true ] && echo 'SUCCESS' || echo 'ISSUES DETECTED')"
    echo ""
    echo "Backups:"
    echo "  Module: $MODULE_BACKUP"
    echo "  Database: $DB_BACKUP"
    echo ""
    echo "Rollback: $ROLLBACK_SCRIPT"
} >> "$MONITORING_LOG"

exit 0
