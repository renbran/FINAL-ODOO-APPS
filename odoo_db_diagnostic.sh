#!/bin/bash
###############################################################################
# Comprehensive Odoo 17 Database Server Diagnostic Script
# For CloudPepper Setup Verification
# Server: 139.84.163.11
# Generated: 2025-11-21
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Output file
OUTPUT_FILE="/tmp/odoo_diagnostic_report_$(date +%Y%m%d_%H%M%S).txt"

echo "Starting Comprehensive Odoo 17 Database Diagnostic..."
echo "Report will be saved to: $OUTPUT_FILE"
echo ""

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}========================================${NC}" | tee -a "$OUTPUT_FILE"
    echo -e "${BLUE}$1${NC}" | tee -a "$OUTPUT_FILE"
    echo -e "${BLUE}========================================${NC}" | tee -a "$OUTPUT_FILE"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}" | tee -a "$OUTPUT_FILE"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}" | tee -a "$OUTPUT_FILE"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}" | tee -a "$OUTPUT_FILE"
}

###############################################################################
# 1. SYSTEM INFORMATION
###############################################################################
print_header "1. SYSTEM INFORMATION"

echo "Hostname:" | tee -a "$OUTPUT_FILE"
hostname | tee -a "$OUTPUT_FILE"

echo -e "\nOS Information:" | tee -a "$OUTPUT_FILE"
cat /etc/os-release | tee -a "$OUTPUT_FILE"

echo -e "\nKernel Version:" | tee -a "$OUTPUT_FILE"
uname -r | tee -a "$OUTPUT_FILE"

echo -e "\nSystem Uptime:" | tee -a "$OUTPUT_FILE"
uptime | tee -a "$OUTPUT_FILE"

echo -e "\nCurrent Date/Time:" | tee -a "$OUTPUT_FILE"
date | tee -a "$OUTPUT_FILE"

###############################################################################
# 2. SYSTEM HEALTH & RESOURCES
###############################################################################
print_header "2. SYSTEM HEALTH & RESOURCES"

echo "CPU Information:" | tee -a "$OUTPUT_FILE"
lscpu | grep -E "Model name|CPU\(s\)|Thread|Core" | tee -a "$OUTPUT_FILE"

echo -e "\nLoad Average:" | tee -a "$OUTPUT_FILE"
cat /proc/loadavg | tee -a "$OUTPUT_FILE"

echo -e "\nMemory Usage:" | tee -a "$OUTPUT_FILE"
free -h | tee -a "$OUTPUT_FILE"

echo -e "\nDisk Usage:" | tee -a "$OUTPUT_FILE"
df -h | tee -a "$OUTPUT_FILE"

echo -e "\nDisk I/O Stats:" | tee -a "$OUTPUT_FILE"
iostat -x 1 2 2>/dev/null || echo "iostat not available" | tee -a "$OUTPUT_FILE"

echo -e "\nTop 10 Processes by Memory:" | tee -a "$OUTPUT_FILE"
ps aux --sort=-%mem | head -11 | tee -a "$OUTPUT_FILE"

echo -e "\nTop 10 Processes by CPU:" | tee -a "$OUTPUT_FILE"
ps aux --sort=-%cpu | head -11 | tee -a "$OUTPUT_FILE"

###############################################################################
# 3. POSTGRESQL DATABASE STATUS
###############################################################################
print_header "3. POSTGRESQL DATABASE STATUS"

# Check PostgreSQL service
if systemctl is-active --quiet postgresql; then
    print_success "PostgreSQL service is running"
    systemctl status postgresql --no-pager | tee -a "$OUTPUT_FILE"
else
    print_error "PostgreSQL service is NOT running"
fi

# PostgreSQL version
echo -e "\nPostgreSQL Version:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SELECT version();" 2>/dev/null | tee -a "$OUTPUT_FILE" || echo "Cannot connect to PostgreSQL" | tee -a "$OUTPUT_FILE"

# PostgreSQL port
echo -e "\nPostgreSQL Listening Port:" | tee -a "$OUTPUT_FILE"
ss -tlnp | grep postgres | tee -a "$OUTPUT_FILE"

# Database list
echo -e "\nDatabases:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "\l" 2>/dev/null | tee -a "$OUTPUT_FILE" || echo "Cannot list databases" | tee -a "$OUTPUT_FILE"

# Database sizes
echo -e "\nDatabase Sizes:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) as size FROM pg_database ORDER BY pg_database_size(datname) DESC;" 2>/dev/null | tee -a "$OUTPUT_FILE"

# Active connections
echo -e "\nActive Database Connections:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SELECT datname, count(*) as connections FROM pg_stat_activity GROUP BY datname;" 2>/dev/null | tee -a "$OUTPUT_FILE"

# Connection details
echo -e "\nDetailed Connection Information:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SELECT pid, usename, datname, client_addr, state, query_start, state_change FROM pg_stat_activity WHERE state != 'idle';" 2>/dev/null | tee -a "$OUTPUT_FILE"

# PostgreSQL configuration
echo -e "\nKey PostgreSQL Configuration:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW max_connections;" 2>/dev/null | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW shared_buffers;" 2>/dev/null | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW effective_cache_size;" 2>/dev/null | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW maintenance_work_mem;" 2>/dev/null | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW work_mem;" 2>/dev/null | tee -a "$OUTPUT_FILE"

# PostgreSQL config file location
echo -e "\nPostgreSQL Config Files:" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW config_file;" 2>/dev/null | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SHOW hba_file;" 2>/dev/null | tee -a "$OUTPUT_FILE"

# Check pg_hba.conf
echo -e "\npg_hba.conf Contents:" | tee -a "$OUTPUT_FILE"
PG_HBA=$(sudo -u postgres psql -t -c "SHOW hba_file;" 2>/dev/null | xargs)
if [ -f "$PG_HBA" ]; then
    cat "$PG_HBA" | grep -v "^#" | grep -v "^$" | tee -a "$OUTPUT_FILE"
fi

# Database performance stats
echo -e "\nDatabase Cache Hit Ratio (should be > 90%):" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SELECT sum(heap_blks_read) as heap_read, sum(heap_blks_hit) as heap_hit, sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 AS cache_hit_ratio FROM pg_statio_user_tables;" 2>/dev/null | tee -a "$OUTPUT_FILE"

# Long running queries
echo -e "\nLong Running Queries (> 5 minutes):" | tee -a "$OUTPUT_FILE"
sudo -u postgres psql -c "SELECT pid, now() - query_start as duration, state, query FROM pg_stat_activity WHERE state != 'idle' AND (now() - query_start) > interval '5 minutes' ORDER BY duration DESC;" 2>/dev/null | tee -a "$OUTPUT_FILE"

###############################################################################
# 4. ODOO 17 SERVICE STATUS
###############################################################################
print_header "4. ODOO 17 SERVICE STATUS"

# Check Odoo service
if systemctl list-units --type=service | grep -i odoo; then
    ODOO_SERVICE=$(systemctl list-units --type=service | grep -i odoo | awk '{print $1}' | head -1)
    echo "Found Odoo service: $ODOO_SERVICE" | tee -a "$OUTPUT_FILE"

    if systemctl is-active --quiet "$ODOO_SERVICE"; then
        print_success "Odoo service is running"
    else
        print_error "Odoo service is NOT running"
    fi

    systemctl status "$ODOO_SERVICE" --no-pager | tee -a "$OUTPUT_FILE"
else
    print_warning "No Odoo systemd service found"
fi

# Check for Odoo processes
echo -e "\nOdoo Processes:" | tee -a "$OUTPUT_FILE"
ps aux | grep -i odoo | grep -v grep | tee -a "$OUTPUT_FILE"

# Check Odoo port
echo -e "\nOdoo Port (default 8069):" | tee -a "$OUTPUT_FILE"
ss -tlnp | grep 8069 | tee -a "$OUTPUT_FILE"

# Find Odoo installation
echo -e "\nOdoo Installation Paths:" | tee -a "$OUTPUT_FILE"
find /opt /usr /home -name "odoo-bin" 2>/dev/null | tee -a "$OUTPUT_FILE"
find /etc -name "odoo*.conf" 2>/dev/null | tee -a "$OUTPUT_FILE"

# Check Odoo configuration
ODOO_CONF=$(find /etc -name "odoo*.conf" 2>/dev/null | head -1)
if [ -f "$ODOO_CONF" ]; then
    echo -e "\nOdoo Configuration ($ODOO_CONF):" | tee -a "$OUTPUT_FILE"
    cat "$ODOO_CONF" | grep -v "^;" | grep -v "^$" | tee -a "$OUTPUT_FILE"
fi

# Check Odoo logs
echo -e "\nOdoo Log Files:" | tee -a "$OUTPUT_FILE"
find /var/log -name "*odoo*" 2>/dev/null | tee -a "$OUTPUT_FILE"

ODOO_LOG=$(find /var/log -name "*odoo*.log" 2>/dev/null | head -1)
if [ -f "$ODOO_LOG" ]; then
    echo -e "\nRecent Odoo Log Entries (last 50 lines):" | tee -a "$OUTPUT_FILE"
    tail -50 "$ODOO_LOG" | tee -a "$OUTPUT_FILE"
fi

###############################################################################
# 5. CLOUDPEPPER SETUP VERIFICATION
###############################################################################
print_header "5. CLOUDPEPPER SETUP VERIFICATION"

# Check for CloudPepper markers
echo "Checking for CloudPepper setup indicators..." | tee -a "$OUTPUT_FILE"

# Check hostname patterns
HOSTNAME=$(hostname)
echo "Hostname: $HOSTNAME" | tee -a "$OUTPUT_FILE"

# Check for CloudPepper user
if id cloudpepper 2>/dev/null; then
    print_success "CloudPepper user exists"
    id cloudpepper | tee -a "$OUTPUT_FILE"
else
    print_warning "CloudPepper user not found"
fi

# Check for Odoo user
if id odoo 2>/dev/null; then
    print_success "Odoo user exists"
    id odoo | tee -a "$OUTPUT_FILE"
else
    print_warning "Odoo user not found"
fi

# Check common CloudPepper directories
echo -e "\nChecking CloudPepper directories:" | tee -a "$OUTPUT_FILE"
for dir in /opt/odoo /opt/cloudpepper /home/odoo; do
    if [ -d "$dir" ]; then
        print_success "Directory exists: $dir"
        ls -la "$dir" | head -20 | tee -a "$OUTPUT_FILE"
    else
        echo "Directory not found: $dir" | tee -a "$OUTPUT_FILE"
    fi
done

# Check for automation/deployment tools
echo -e "\nDeployment Tools:" | tee -a "$OUTPUT_FILE"
which ansible 2>/dev/null && ansible --version | tee -a "$OUTPUT_FILE" || echo "Ansible not found" | tee -a "$OUTPUT_FILE"
which docker 2>/dev/null && docker --version | tee -a "$OUTPUT_FILE" || echo "Docker not found" | tee -a "$OUTPUT_FILE"

###############################################################################
# 6. NETWORK & SECURITY
###############################################################################
print_header "6. NETWORK & SECURITY"

# Listening ports
echo "Listening Ports:" | tee -a "$OUTPUT_FILE"
ss -tlnp | tee -a "$OUTPUT_FILE"

# Firewall status
echo -e "\nFirewall Status (UFW):" | tee -a "$OUTPUT_FILE"
ufw status verbose 2>/dev/null | tee -a "$OUTPUT_FILE" || echo "UFW not available" | tee -a "$OUTPUT_FILE"

echo -e "\nFirewall Status (iptables):" | tee -a "$OUTPUT_FILE"
iptables -L -n -v 2>/dev/null | head -50 | tee -a "$OUTPUT_FILE" || echo "Cannot list iptables" | tee -a "$OUTPUT_FILE"

# SSL certificates
echo -e "\nSSL Certificates:" | tee -a "$OUTPUT_FILE"
find /etc/ssl /etc/nginx /etc/apache2 -name "*.crt" -o -name "*.pem" 2>/dev/null | head -20 | tee -a "$OUTPUT_FILE"

# Nginx/Apache status
echo -e "\nWeb Server Status:" | tee -a "$OUTPUT_FILE"
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running"
    systemctl status nginx --no-pager | tee -a "$OUTPUT_FILE"
elif systemctl is-active --quiet apache2; then
    print_success "Apache is running"
    systemctl status apache2 --no-pager | tee -a "$OUTPUT_FILE"
else
    print_warning "No web server (Nginx/Apache) detected"
fi

###############################################################################
# 7. BACKUP CONFIGURATION
###############################################################################
print_header "7. BACKUP CONFIGURATION"

# Check for backup directories
echo "Backup Directories:" | tee -a "$OUTPUT_FILE"
for dir in /backup /backups /var/backups/odoo /opt/odoo/backups; do
    if [ -d "$dir" ]; then
        print_success "Backup directory found: $dir"
        ls -lah "$dir" | head -20 | tee -a "$OUTPUT_FILE"
    fi
done

# Check cron jobs
echo -e "\nCron Jobs (root):" | tee -a "$OUTPUT_FILE"
crontab -l 2>/dev/null | tee -a "$OUTPUT_FILE" || echo "No root crontab" | tee -a "$OUTPUT_FILE"

echo -e "\nCron Jobs (odoo user):" | tee -a "$OUTPUT_FILE"
sudo -u odoo crontab -l 2>/dev/null | tee -a "$OUTPUT_FILE" || echo "No odoo user crontab" | tee -a "$OUTPUT_FILE"

# Check for backup scripts
echo -e "\nBackup Scripts:" | tee -a "$OUTPUT_FILE"
find /opt /home /usr/local/bin -name "*backup*" -type f 2>/dev/null | head -20 | tee -a "$OUTPUT_FILE"

###############################################################################
# 8. PERFORMANCE METRICS
###############################################################################
print_header "8. PERFORMANCE METRICS"

# Network statistics
echo "Network Statistics:" | tee -a "$OUTPUT_FILE"
netstat -s | grep -E "segments|packets" | head -20 | tee -a "$OUTPUT_FILE"

# Disk performance
echo -e "\nDisk I/O Performance:" | tee -a "$OUTPUT_FILE"
iostat -dx 1 3 2>/dev/null | tee -a "$OUTPUT_FILE" || echo "iostat not available" | tee -a "$OUTPUT_FILE"

###############################################################################
# 9. SECURITY CHECKS
###############################################################################
print_header "9. SECURITY CHECKS"

# Check for security updates
echo "Security Updates:" | tee -a "$OUTPUT_FILE"
apt list --upgradable 2>/dev/null | grep -i security | head -20 | tee -a "$OUTPUT_FILE" || echo "apt not available or no security updates" | tee -a "$OUTPUT_FILE"

# Check SSH configuration
echo -e "\nSSH Configuration:" | tee -a "$OUTPUT_FILE"
grep -E "^PermitRootLogin|^PasswordAuthentication|^Port" /etc/ssh/sshd_config | tee -a "$OUTPUT_FILE"

# Check failed login attempts
echo -e "\nRecent Failed Login Attempts:" | tee -a "$OUTPUT_FILE"
grep "Failed password" /var/log/auth.log 2>/dev/null | tail -20 | tee -a "$OUTPUT_FILE" || echo "No auth.log or no failed attempts" | tee -a "$OUTPUT_FILE"

###############################################################################
# 10. SUMMARY & RECOMMENDATIONS
###############################################################################
print_header "10. SUMMARY & HEALTH CHECK"

echo -e "\nHealth Check Summary:" | tee -a "$OUTPUT_FILE"

# PostgreSQL health
if systemctl is-active --quiet postgresql; then
    print_success "PostgreSQL: Running"
else
    print_error "PostgreSQL: NOT Running"
fi

# Odoo health
if ps aux | grep -i odoo | grep -v grep > /dev/null; then
    print_success "Odoo: Running"
else
    print_error "Odoo: NOT Running"
fi

# Disk space check
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "Disk Usage: ${DISK_USAGE}% (Good)"
elif [ "$DISK_USAGE" -lt 90 ]; then
    print_warning "Disk Usage: ${DISK_USAGE}% (Monitor)"
else
    print_error "Disk Usage: ${DISK_USAGE}% (Critical)"
fi

# Memory check
MEMORY_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    print_success "Memory Usage: ${MEMORY_USAGE}% (Good)"
elif [ "$MEMORY_USAGE" -lt 90 ]; then
    print_warning "Memory Usage: ${MEMORY_USAGE}% (Monitor)"
else
    print_error "Memory Usage: ${MEMORY_USAGE}% (Critical)"
fi

###############################################################################
# FINISH
###############################################################################
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Diagnostic Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Full report saved to: ${BLUE}$OUTPUT_FILE${NC}"
echo -e "\nTo view the report:"
echo -e "  cat $OUTPUT_FILE"
echo -e "\nTo download the report (from your local machine):"
echo -e "  scp root@139.84.163.11:$OUTPUT_FILE ."
echo ""
