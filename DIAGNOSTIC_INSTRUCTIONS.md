# Odoo 17 Database Server Diagnostic Instructions

**Server:** root@139.84.163.11 (Port 22)
**Purpose:** Comprehensive health check and CloudPepper setup verification
**Date:** 2025-11-21

## 🔒 SSH Key Saved
The private key has been saved to `/tmp/ssh_key` with proper permissions (600).

---

## 📋 Diagnostic Options

### Option 1: Run Python Script Locally (Recommended)

The Python script (`remote_diagnostic.py`) can connect to the remote server and run all diagnostics automatically.

#### Prerequisites:
```bash
pip3 install paramiko
```

#### Execute from your local machine:
```bash
# Make sure you're in the project directory
cd /home/user/FINAL-ODOO-APPS

# Run the diagnostic
python3 remote_diagnostic.py
```

**What it checks:**
- ✓ System information (OS, kernel, uptime)
- ✓ System resources (CPU, memory, disk)
- ✓ PostgreSQL status and configuration
- ✓ Database list, sizes, and connections
- ✓ Active queries and performance
- ✓ Odoo 17 service and configuration
- ✓ CloudPepper setup verification
- ✓ Network and security settings
- ✓ Backup configurations
- ✓ Recent logs and errors
- ✓ Health summary with recommendations

**Output:**
- Console output with live progress
- Detailed report saved to `odoo_diagnostic_YYYYMMDD_HHMMSS.txt`

---

### Option 2: Run Bash Script on Remote Server

If Python/paramiko is not available, you can copy and run the bash script directly on the server.

#### Step 1: Copy script to server
```bash
scp -i /tmp/ssh_key odoo_db_diagnostic.sh root@139.84.163.11:/tmp/
```

#### Step 2: Connect to server
```bash
ssh -i /tmp/ssh_key root@139.84.163.11
```

#### Step 3: Run diagnostic on server
```bash
chmod +x /tmp/odoo_db_diagnostic.sh
/tmp/odoo_db_diagnostic.sh
```

#### Step 4: Download the report
```bash
# From your local machine
scp -i /tmp/ssh_key root@139.84.163.11:/tmp/odoo_diagnostic_report_*.txt .
```

---

### Option 3: Manual SSH Commands

If you prefer to run commands manually:

```bash
# Connect to server
ssh -i /tmp/ssh_key root@139.84.163.11

# Then run commands individually:

# 1. System Health
uptime
free -h
df -h

# 2. PostgreSQL Status
systemctl status postgresql
sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database;"

# 3. Odoo Status
ps aux | grep odoo
systemctl status odoo-server
cat /etc/odoo-server.conf

# 4. Check connections
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# 5. Check disk and memory
df -h
free -h
```

---

## 📊 What the Diagnostic Checks

### 1. System Information
- Hostname and OS version
- Kernel version
- System uptime
- Current date/time

### 2. System Health & Resources
- CPU information and load average
- Memory usage (RAM)
- Disk space and I/O
- Top processes by CPU and memory

### 3. PostgreSQL Database
- ✅ Service status (running/stopped)
- ✅ PostgreSQL version
- ✅ Listening ports
- ✅ Database list and sizes
- ✅ Active connections by database
- ✅ Configuration settings:
  - max_connections
  - shared_buffers
  - effective_cache_size
  - work_mem
- ✅ Cache hit ratio (performance)
- ✅ Long-running queries
- ✅ pg_hba.conf (access control)

### 4. Odoo 17 Service
- ✅ Service status
- ✅ Running processes
- ✅ Port 8069 (default Odoo port)
- ✅ Installation paths
- ✅ Configuration file contents
- ✅ Recent log entries

### 5. CloudPepper Setup Verification
- ✅ CloudPepper user existence
- ✅ Odoo user and permissions
- ✅ Standard directories (/opt/odoo, etc.)
- ✅ Deployment tools (Ansible, Docker)

### 6. Network & Security
- ✅ All listening ports
- ✅ Firewall status (UFW/iptables)
- ✅ SSL certificates
- ✅ Web server status (Nginx/Apache)
- ✅ SSH configuration

### 7. Backup Configuration
- ✅ Backup directories
- ✅ Cron jobs for automated backups
- ✅ Recent backup files
- ✅ Backup scripts

### 8. Performance Metrics
- ✅ Network statistics
- ✅ Disk I/O performance
- ✅ Resource utilization

### 9. Security Checks
- ✅ Security updates available
- ✅ SSH hardening settings
- ✅ Failed login attempts

### 10. Health Summary
- ✅ PostgreSQL: Running/Not Running
- ✅ Odoo: Running/Not Running
- ✅ Disk Usage: Good/Monitor/Critical
- ✅ Memory Usage: Good/Monitor/Critical

---

## 🎯 Expected CloudPepper Setup

The diagnostic will verify if the following CloudPepper standards are in place:

1. **User Configuration**
   - `odoo` system user for running Odoo
   - Proper permissions and ownership

2. **Directory Structure**
   - `/opt/odoo` - Odoo installation
   - `/var/log/odoo` - Log files
   - `/etc/odoo-server.conf` - Configuration
   - Backup directories

3. **Services**
   - PostgreSQL configured for Odoo
   - Odoo service managed by systemd
   - Nginx/Apache reverse proxy

4. **Security**
   - Firewall configured (UFW/iptables)
   - SSL certificates installed
   - Proper PostgreSQL access controls

5. **Backups**
   - Automated backup cron jobs
   - Database backup scripts
   - Filestore backup scripts

---

## 🚨 Common Issues to Check

### PostgreSQL Issues
- **Not running**: `systemctl start postgresql`
- **Connection errors**: Check pg_hba.conf
- **High connections**: Check max_connections setting
- **Slow queries**: Check cache hit ratio

### Odoo Issues
- **Not running**: `systemctl start odoo-server`
- **Port not listening**: Check Odoo config and logs
- **Permission errors**: Check odoo user permissions
- **Database connection**: Check db_host, db_port in config

### System Issues
- **High disk usage (>80%)**: Clean old logs, backups
- **High memory usage (>90%)**: Check Odoo workers config
- **High load**: Check long-running queries

### CloudPepper Compliance
- **Missing directories**: Recreate standard structure
- **Wrong permissions**: `chown -R odoo:odoo /opt/odoo`
- **Missing services**: Reinstall/reconfigure services
- **No backups**: Set up automated backup scripts

---

## 📝 Report Interpretation

The diagnostic generates a comprehensive report with:

1. **Green (✓)**: Everything is working correctly
2. **Yellow (⚠)**: Warning - monitor the situation
3. **Red (✗)**: Error - immediate attention required

### Critical Thresholds
- **Disk usage > 90%**: Critical - clean up space immediately
- **Memory usage > 90%**: Critical - optimize or add RAM
- **PostgreSQL not running**: Critical - start service
- **Odoo not running**: Critical - start service
- **No recent backups**: Warning - verify backup system

---

## 🔧 Troubleshooting

### Cannot Connect via SSH
```bash
# Test connection
nc -zv 139.84.163.11 22

# Verify key permissions
chmod 600 /tmp/ssh_key

# Verbose SSH connection for debugging
ssh -vvv -i /tmp/ssh_key root@139.84.163.11
```

### Python Script Fails
```bash
# Install paramiko
pip3 install paramiko

# Run with debug output
python3 -u remote_diagnostic.py
```

### Bash Script Permissions
```bash
# If permission denied
chmod +x odoo_db_diagnostic.sh

# Run with bash explicitly
bash odoo_db_diagnostic.sh
```

---

## 📞 Next Steps

After running the diagnostic:

1. **Review the report** - Look for any red (✗) or yellow (⚠) indicators
2. **Check health summary** - Verify all critical services are running
3. **Verify CloudPepper compliance** - Ensure standard structure is present
4. **Address any issues** - Fix critical problems first
5. **Document findings** - Save the report for future reference
6. **Schedule regular checks** - Run diagnostics weekly/monthly

---

## 📄 Files Created

1. **odoo_db_diagnostic.sh** - Comprehensive bash diagnostic script
2. **remote_diagnostic.py** - Python script for remote execution
3. **DIAGNOSTIC_INSTRUCTIONS.md** - This documentation file

---

## 🔐 Security Notes

- The SSH private key is stored at `/tmp/ssh_key` with 600 permissions
- The key should be removed after use: `rm /tmp/ssh_key`
- Never commit private keys to version control
- Rotate keys regularly for security

---

**Generated by Claude Code - Odoo Database Diagnostic Tool**
**Version:** 1.0
**Date:** 2025-11-21
