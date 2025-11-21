# CloudPepper Compliance Remediation Guide

**Purpose:** Step-by-step guide to fix common CloudPepper setup issues
**Target:** Odoo 17 on Ubuntu/Debian servers
**Last Updated:** 2025-11-21

---

## 📋 Table of Contents

1. [User & Permission Issues](#user--permission-issues)
2. [Directory Structure Issues](#directory-structure-issues)
3. [PostgreSQL Configuration Issues](#postgresql-configuration-issues)
4. [Odoo Configuration Issues](#odoo-configuration-issues)
5. [Database Issues](#database-issues)
6. [Custom Module Issues](#custom-module-issues)
7. [Performance Issues](#performance-issues)
8. [Security Issues](#security-issues)
9. [Backup Issues](#backup-issues)

---

## 1. User & Permission Issues

### Issue: Odoo user does not exist

**Severity:** CRITICAL

**Fix:**
```bash
# Create odoo system user
sudo adduser --system --home=/opt/odoo --group odoo

# Set no login shell for security
sudo usermod -s /usr/sbin/nologin odoo

# Verify user created
id odoo
```

### Issue: Wrong directory ownership

**Severity:** HIGH

**Fix:**
```bash
# Fix ownership for all Odoo directories
sudo chown -R odoo:odoo /opt/odoo
sudo chown -R odoo:odoo /var/log/odoo
sudo chown -R odoo:odoo /opt/odoo/.local/share/Odoo

# Verify permissions
ls -la /opt/odoo
ls -la /var/log/odoo
```

### Issue: Odoo user has login shell (security risk)

**Severity:** MEDIUM

**Fix:**
```bash
# Disable login shell
sudo usermod -s /usr/sbin/nologin odoo

# Or use /bin/false
sudo usermod -s /bin/false odoo

# Verify
getent passwd odoo | cut -d: -f7
```

---

## 2. Directory Structure Issues

### Issue: Missing Odoo directories

**Severity:** HIGH

**Fix:**
```bash
# Create standard CloudPepper directory structure
sudo mkdir -p /opt/odoo
sudo mkdir -p /var/log/odoo
sudo mkdir -p /opt/odoo/.local/share/Odoo
sudo mkdir -p /opt/odoo/custom-addons
sudo mkdir -p /backup/odoo

# Set ownership
sudo chown -R odoo:odoo /opt/odoo
sudo chown -R odoo:odoo /var/log/odoo
sudo chown -R odoo:odoo /backup/odoo

# Set permissions
sudo chmod 755 /opt/odoo
sudo chmod 755 /var/log/odoo
sudo chmod 750 /backup/odoo

# Verify
ls -la /opt/ | grep odoo
ls -la /var/log/ | grep odoo
```

### Issue: Incorrect directory permissions

**Severity:** MEDIUM

**Fix:**
```bash
# Fix permissions
sudo chmod 755 /opt/odoo
sudo chmod 755 /var/log/odoo
sudo chmod 750 /opt/odoo/.local/share/Odoo

# Make Odoo binary executable (if exists)
sudo chmod +x /opt/odoo/odoo-bin

# Verify
stat -c '%a %n' /opt/odoo
stat -c '%a %n' /var/log/odoo
```

---

## 3. PostgreSQL Configuration Issues

### Issue: PostgreSQL not running

**Severity:** CRITICAL

**Fix:**
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Enable on boot
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql

# Verify port is listening
ss -tlnp | grep 5432
```

### Issue: Cannot connect to PostgreSQL

**Severity:** CRITICAL

**Fix:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection as postgres user
sudo -u postgres psql -c "\l"

# If connection fails, check logs
sudo tail -50 /var/log/postgresql/postgresql-*-main.log

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Issue: max_connections too low

**Severity:** MEDIUM

**Fix:**
```bash
# Find PostgreSQL config
sudo -u postgres psql -c "SHOW config_file;"

# Edit postgresql.conf (adjust path as needed)
sudo nano /etc/postgresql/14/main/postgresql.conf

# Change max_connections (recommend 100-200)
# max_connections = 100

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify
sudo -u postgres psql -c "SHOW max_connections;"
```

### Issue: shared_buffers too low

**Severity:** MEDIUM

**Fix:**
```bash
# Calculate 25% of total RAM
free -m | awk 'NR==2 {printf "Recommended shared_buffers: %dMB\n", $2*0.25}'

# Edit postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf

# Set shared_buffers (example for 8GB RAM = 2GB)
# shared_buffers = 2GB

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify
sudo -u postgres psql -c "SHOW shared_buffers;"
```

### Issue: PostgreSQL listening externally (security risk)

**Severity:** HIGH

**Fix:**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf

# Change listen_addresses to localhost only
# listen_addresses = 'localhost'

# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Ensure only local connections are allowed
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify
ss -tlnp | grep 5432
# Should show 127.0.0.1:5432, not 0.0.0.0:5432
```

---

## 4. Odoo Configuration Issues

### Issue: Odoo configuration file not found

**Severity:** CRITICAL

**Fix:**
```bash
# Create Odoo configuration file
sudo nano /etc/odoo.conf

# Basic CloudPepper-compliant configuration:
cat <<'EOF' | sudo tee /etc/odoo.conf
[options]
; Admin password (change this!)
admin_passwd = change_me_to_strong_password

; Database settings
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_db_password

; Odoo settings
addons_path = /opt/odoo/addons,/opt/odoo/custom-addons
data_dir = /opt/odoo/.local/share/Odoo
logfile = /var/log/odoo/odoo-server.log
log_level = info

; Performance settings
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

; Network settings
http_port = 8069
proxy_mode = True

EOF

# Set permissions
sudo chown odoo:odoo /etc/odoo.conf
sudo chmod 640 /etc/odoo.conf

# Verify
cat /etc/odoo.conf
```

### Issue: Workers not configured (single-process mode)

**Severity:** MEDIUM (HIGH for production)

**Fix:**
```bash
# Calculate recommended workers: (CPU cores * 2) + 1
WORKERS=$(( $(nproc) * 2 + 1 ))
echo "Recommended workers: $WORKERS"

# Edit Odoo config
sudo nano /etc/odoo.conf

# Add/update workers line
# workers = 4

# Also configure memory limits per worker
# limit_memory_hard = 2684354560  ; 2.5 GB
# limit_memory_soft = 2147483648  ; 2 GB

# Restart Odoo
sudo systemctl restart odoo-server

# Verify workers are running
ps aux | grep odoo-bin
# Should see multiple odoo processes
```

### Issue: Missing critical configuration parameters

**Severity:** HIGH

**Fix:**
```bash
# Edit Odoo configuration
sudo nano /etc/odoo.conf

# Ensure these are set:
# [options]
# db_host = localhost
# db_port = 5432
# db_user = odoo
# data_dir = /opt/odoo/.local/share/Odoo
# addons_path = /opt/odoo/addons,/opt/odoo/custom-addons
# logfile = /var/log/odoo/odoo-server.log

# Create directories if missing
sudo mkdir -p /opt/odoo/.local/share/Odoo
sudo mkdir -p /var/log/odoo
sudo chown -R odoo:odoo /opt/odoo
sudo chown -R odoo:odoo /var/log/odoo

# Restart Odoo
sudo systemctl restart odoo-server
```

---

## 5. Database Issues

### Issue: Database encoding not UTF8

**Severity:** HIGH

**Fix:**
```bash
# Check current encoding
sudo -u postgres psql -c "SELECT datname, pg_encoding_to_char(encoding) FROM pg_database;"

# Create new database with UTF8 encoding
sudo -u postgres createdb -E UTF8 -O odoo -T template0 new_database_name

# Migrate data from old database (if needed)
sudo -u postgres pg_dump old_database | sudo -u postgres psql new_database_name

# Update Odoo config to use new database
sudo nano /etc/odoo.conf
# db_name = new_database_name
```

### Issue: Bloated database (large size)

**Severity:** MEDIUM

**Fix:**
```bash
# Run VACUUM to reclaim space
sudo -u postgres psql -d database_name -c "VACUUM FULL VERBOSE;"

# Analyze tables for query optimization
sudo -u postgres psql -d database_name -c "ANALYZE;"

# Check for old/unused data
# - Archive old records
# - Delete unused attachments
# - Clean up mail_message table (often very large)

# Automated cleanup script
cat <<'EOF' | sudo -u postgres psql -d database_name
-- Delete old emails (older than 6 months)
DELETE FROM mail_message WHERE create_date < NOW() - INTERVAL '6 months';

-- Vacuum after cleanup
VACUUM FULL VERBOSE mail_message;
EOF
```

### Issue: Too many active connections

**Severity:** HIGH

**Fix:**
```bash
# Check current connections
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Kill idle connections
sudo -u postgres psql <<EOF
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '1 hour';
EOF

# Reduce Odoo workers to lower connection usage
sudo nano /etc/odoo.conf
# workers = 2  # Reduce from higher number

# Increase PostgreSQL max_connections if needed
sudo nano /etc/postgresql/14/main/postgresql.conf
# max_connections = 150

# Restart services
sudo systemctl restart postgresql
sudo systemctl restart odoo-server
```

### Issue: Long-running queries

**Severity:** MEDIUM

**Fix:**
```bash
# Identify long-running queries
sudo -u postgres psql <<EOF
SELECT pid, now() - query_start as duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND (now() - query_start) > interval '5 minutes'
ORDER BY duration DESC;
EOF

# Kill specific problematic query (use pid from above)
sudo -u postgres psql -c "SELECT pg_terminate_backend(12345);"

# Check for missing indexes (common cause)
sudo -u postgres psql -d database_name <<EOF
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND n_distinct > 100
ORDER BY n_distinct DESC;
EOF

# Update PostgreSQL statistics
sudo -u postgres psql -d database_name -c "ANALYZE;"
```

---

## 6. Custom Module Issues

### Issue: Custom module missing __init__.py

**Severity:** MEDIUM

**Fix:**
```bash
# Navigate to module directory
cd /opt/odoo/custom-addons/module_name

# Create __init__.py if missing
sudo -u odoo touch __init__.py

# Add import statements
sudo -u odoo nano __init__.py

# Content should import other Python files:
# from . import models
# from . import controllers
# from . import wizard

# Restart Odoo
sudo systemctl restart odoo-server
```

### Issue: Module marked as not installable

**Severity:** LOW

**Fix:**
```bash
# Edit module manifest
sudo -u odoo nano /opt/odoo/custom-addons/module_name/__manifest__.py

# Change installable flag
# 'installable': True,

# Update module list in Odoo
# - Login to Odoo
# - Go to Apps
# - Click "Update Apps List"
# - Search for module and install
```

### Issue: Module has Python syntax errors

**Severity:** HIGH

**Fix:**
```bash
# Check for syntax errors
python3 -m py_compile /opt/odoo/custom-addons/module_name/*.py

# Check Odoo logs for specific errors
sudo tail -100 /var/log/odoo/odoo-server.log | grep -i error

# Common fixes:
# 1. Fix indentation (use 4 spaces)
# 2. Fix import statements
# 3. Check for Python 3 compatibility
# 4. Validate XML/CSV files

# Test module installation
sudo -u odoo /opt/odoo/odoo-bin -c /etc/odoo.conf -d test_db -i module_name --stop-after-init

# If successful, restart Odoo
sudo systemctl restart odoo-server
```

### Issue: Module dependencies not installed

**Severity:** HIGH

**Fix:**
```bash
# Check module manifest for dependencies
sudo cat /opt/odoo/custom-addons/module_name/__manifest__.py | grep depends

# Install missing dependencies
# - Check if dependency exists in addons_path
find /opt/odoo -name "dependency_module_name"

# If missing, download from Odoo Apps Store or GitHub
cd /opt/odoo/custom-addons
sudo -u odoo git clone https://github.com/OCA/module-repo.git

# Update addons_path if needed
sudo nano /etc/odoo.conf
# addons_path = /opt/odoo/addons,/opt/odoo/custom-addons,/opt/odoo/custom-addons/module-repo

# Restart Odoo
sudo systemctl restart odoo-server
```

---

## 7. Performance Issues

### Issue: High CPU usage

**Severity:** MEDIUM

**Fix:**
```bash
# Check which process is using CPU
top -b -n 1 | head -20

# Check for long-running queries (see Database Issues)
# Reduce Odoo workers if CPU maxed out
sudo nano /etc/odoo.conf
# workers = 2  # Reduce

# Increase worker timeout limits
# limit_time_cpu = 600
# limit_time_real = 1200

# Restart Odoo
sudo systemctl restart odoo-server
```

### Issue: High memory usage

**Severity:** MEDIUM

**Fix:**
```bash
# Check memory usage
free -m

# Reduce Odoo memory limits
sudo nano /etc/odoo.conf

# Set memory limits per worker
# limit_memory_hard = 2147483648  ; 2GB
# limit_memory_soft = 1610612736  ; 1.5GB

# Reduce workers
# workers = 2

# Restart Odoo
sudo systemctl restart odoo-server

# Monitor memory
watch -n 2 free -m
```

### Issue: Disk I/O bottleneck

**Severity:** MEDIUM

**Fix:**
```bash
# Check I/O stats
iostat -x 1 5

# Move database to faster disk (SSD)
# Or enable PostgreSQL WAL on separate disk

# Optimize PostgreSQL for SSD
sudo nano /etc/postgresql/14/main/postgresql.conf

# effective_io_concurrency = 200  # For SSD
# random_page_cost = 1.1          # For SSD

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## 8. Security Issues

### Issue: UFW firewall not active

**Severity:** HIGH

**Fix:**
```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Odoo port (only if needed for direct access)
sudo ufw allow 8069/tcp

# Check status
sudo ufw status verbose

# Deny PostgreSQL external access (ensure it's not allowed)
sudo ufw status | grep 5432
# If 5432 is allowed, remove it:
sudo ufw delete allow 5432
```

### Issue: SSH root login permitted

**Severity:** HIGH

**Fix:**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Change or add these lines:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

# Restart SSH service
sudo systemctl restart sshd

# Verify settings
sudo sshd -T | grep -i permitrootlogin
```

### Issue: PostgreSQL exposed externally

**Severity:** CRITICAL

**Fix:**
```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/postgresql.conf

# Set to listen only on localhost
# listen_addresses = 'localhost'

# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Remove any lines with 0.0.0.0/0
# Keep only local and 127.0.0.1 entries

# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify
ss -tlnp | grep 5432
# Should show 127.0.0.1:5432, NOT 0.0.0.0:5432

# Block port 5432 in firewall
sudo ufw deny 5432/tcp
```

### Issue: Weak Odoo admin password

**Severity:** HIGH

**Fix:**
```bash
# Generate strong password
openssl rand -base64 32

# Edit Odoo config
sudo nano /etc/odoo.conf

# Update admin_passwd
# admin_passwd = <strong_password_here>

# Set restrictive permissions
sudo chmod 640 /etc/odoo.conf
sudo chown odoo:odoo /etc/odoo.conf

# Restart Odoo
sudo systemctl restart odoo-server
```

---

## 9. Backup Issues

### Issue: No backup directory

**Severity:** MEDIUM

**Fix:**
```bash
# Create backup directory
sudo mkdir -p /backup/odoo/database
sudo mkdir -p /backup/odoo/filestore

# Set ownership
sudo chown -R odoo:odoo /backup/odoo

# Set permissions
sudo chmod 750 /backup/odoo

# Verify
ls -la /backup/
```

### Issue: No backup cron job configured

**Severity:** HIGH

**Fix:**
```bash
# Create backup script
sudo nano /opt/odoo/backup_odoo.sh

# Add backup script content:
cat <<'EOF' | sudo tee /opt/odoo/backup_odoo.sh
#!/bin/bash
# Odoo Backup Script
BACKUP_DIR="/backup/odoo"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="your_database_name"  # Change this

# Backup database
sudo -u postgres pg_dump $DB_NAME | gzip > $BACKUP_DIR/database/${DB_NAME}_${DATE}.sql.gz

# Backup filestore
tar -czf $BACKUP_DIR/filestore/filestore_${DATE}.tar.gz /opt/odoo/.local/share/Odoo/filestore/$DB_NAME

# Keep only last 7 days of backups
find $BACKUP_DIR/database -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR/filestore -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# Make executable
sudo chmod +x /opt/odoo/backup_odoo.sh
sudo chown odoo:odoo /opt/odoo/backup_odoo.sh

# Add to cron (daily at 2 AM)
sudo -u odoo crontab -e

# Add this line:
# 0 2 * * * /opt/odoo/backup_odoo.sh >> /var/log/odoo/backup.log 2>&1

# Verify cron job
sudo -u odoo crontab -l

# Test backup script
sudo -u odoo /opt/odoo/backup_odoo.sh
```

### Issue: No recent backups found

**Severity:** HIGH

**Fix:**
```bash
# Check if backup script exists
ls -la /opt/odoo/backup_odoo.sh

# Check cron jobs
sudo -u odoo crontab -l

# Check backup logs
sudo tail -50 /var/log/odoo/backup.log

# Manually run backup to test
sudo -u odoo /opt/odoo/backup_odoo.sh

# Check backup directory
ls -lah /backup/odoo/database/
ls -lah /backup/odoo/filestore/

# If backups are failing, check permissions
sudo chown -R odoo:odoo /backup/odoo
sudo chmod 750 /backup/odoo
```

---

## 🔧 Complete CloudPepper Setup Script

For a fresh Odoo 17 installation following CloudPepper standards:

```bash
#!/bin/bash
# Complete CloudPepper Odoo 17 Setup

set -e

echo "Installing Odoo 17 with CloudPepper Standards..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y postgresql postgresql-client python3 python3-pip python3-dev \
  python3-venv libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
  libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev \
  liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev \
  libpq-dev git curl build-essential

# Create odoo user
sudo adduser --system --home=/opt/odoo --group odoo

# Install wkhtmltopdf
cd /tmp
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
sudo apt install -y ./wkhtmltox_0.12.6-1.focal_amd64.deb

# Clone Odoo 17
sudo su - odoo -s /bin/bash -c "git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo.git /opt/odoo/odoo17"

# Install Python dependencies
sudo su - odoo -s /bin/bash -c "python3 -m venv /opt/odoo/odoo17-venv"
sudo su - odoo -s /bin/bash -c "/opt/odoo/odoo17-venv/bin/pip install wheel"
sudo su - odoo -s /bin/bash -c "/opt/odoo/odoo17-venv/bin/pip install -r /opt/odoo/odoo17/requirements.txt"

# Create directories
sudo mkdir -p /opt/odoo/custom-addons
sudo mkdir -p /var/log/odoo
sudo mkdir -p /backup/odoo/{database,filestore}
sudo chown -R odoo:odoo /opt/odoo
sudo chown -R odoo:odoo /var/log/odoo
sudo chown -R odoo:odoo /backup/odoo

# Create PostgreSQL user
sudo -u postgres createuser -s odoo

# Create Odoo configuration
sudo cat <<'EOF' > /etc/odoo.conf
[options]
admin_passwd = $(openssl rand -base64 32)
db_host = localhost
db_port = 5432
db_user = odoo
addons_path = /opt/odoo/odoo17/addons,/opt/odoo/custom-addons
data_dir = /opt/odoo/.local/share/Odoo
logfile = /var/log/odoo/odoo-server.log
log_level = info
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
http_port = 8069
proxy_mode = True
EOF

sudo chown odoo:odoo /etc/odoo.conf
sudo chmod 640 /etc/odoo.conf

# Create systemd service
sudo cat <<'EOF' > /etc/systemd/system/odoo-server.service
[Unit]
Description=Odoo 17 Server
Documentation=https://www.odoo.com
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo17-venv/bin/python /opt/odoo/odoo17/odoo-bin -c /etc/odoo.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
EOF

# Start Odoo service
sudo systemctl daemon-reload
sudo systemctl enable odoo-server
sudo systemctl start odoo-server

# Setup firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "Odoo 17 installation complete!"
echo "Access Odoo at: http://your-server-ip:8069"
echo "Admin password is in /etc/odoo.conf"
```

---

## 📞 Support & Documentation

For more information about CloudPepper standards:
- CloudPepper Documentation
- Odoo Official Documentation: https://www.odoo.com/documentation/17.0
- PostgreSQL Tuning Guide: https://pgtune.leopard.in.ua

---

**Last Updated:** 2025-11-21
**Version:** 1.0
