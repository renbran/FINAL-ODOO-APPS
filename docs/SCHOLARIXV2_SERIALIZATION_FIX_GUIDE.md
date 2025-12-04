# ScholarixV2 Serialization Error Fix Guide

## 🚨 Problem
```
psycopg2.errors.SerializationFailure: could not serialize access due to concurrent update
```

## 📋 System Information
- **Server**: 139.84.163.11
- **Odoo Path**: /var/odoo/scholarixv2/src
- **Config**: /var/odoo/scholarixv2/odoo.conf
- **Logs**: /var/odoo/scholarixv2/logs
- **Database**: scholarixv2
- **User**: odoo
- **Python**: /var/odoo/scholarixv2/venv/bin/python3

---

## 🔧 Quick Fix (Execute These Commands)

### **Option 1: Automated Script**
```bash
# 1. Connect to server
ssh root@139.84.163.11

# 2. Download and run fix script
cd /var/odoo/scholarixv2
wget -O fix_serialization.sh https://raw.githubusercontent.com/renbran/FINAL-ODOO-APPS/main/scripts/fixes/fix_scholarixv2_serialization_error.sh
chmod +x fix_serialization.sh
./fix_serialization.sh
```

### **Option 2: Manual Step-by-Step**

#### **Step 1: Stop All Odoo Processes**
```bash
# Check running processes
ps aux | grep odoo

# Stop systemd service (if exists)
sudo systemctl stop odoo

# Kill any remaining processes
sudo pkill -f odoo-bin
sudo pkill -f "python.*odoo"

# Verify all stopped
ps aux | grep odoo | grep -v grep
```

#### **Step 2: Clear Database Connections**
```bash
sudo -u postgres psql -d scholarixv2 -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'scholarixv2' 
  AND pid <> pg_backend_pid();"
```

#### **Step 3: Backup Configuration**
```bash
sudo cp /var/odoo/scholarixv2/odoo.conf /var/odoo/scholarixv2/odoo.conf.backup.$(date +%Y%m%d_%H%M%S)
```

#### **Step 4: Edit Configuration (Set Single Worker Mode)**
```bash
sudo nano /var/odoo/scholarixv2/odoo.conf
```

Add or modify these lines:
```ini
workers = 0
max_cron_threads = 0
db_maxconn = 64
limit_time_real = 1200
limit_time_cpu = 600
```

Save and exit (Ctrl+X, Y, Enter)

#### **Step 5: Start Odoo**
```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --log-level=info
```

Or run as background process:
```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --log-level=info > logs/odoo.log 2>&1 &
```

#### **Step 6: Monitor Logs**
```bash
tail -f /var/odoo/scholarixv2/logs/odoo.log
```

Look for:
- ✅ "Listening on http://0.0.0.0:8069"
- ❌ Any ERROR or CRITICAL messages

---

## 🔍 Verification Commands

### Check Odoo Status
```bash
ps aux | grep odoo | grep -v grep
```

### Check Database Connections
```bash
sudo -u postgres psql -d scholarixv2 -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'scholarixv2';"
```

### Test Odoo Shell
```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
```

### Check Web Access
```bash
curl -I http://localhost:8069
```

---

## 🔄 Restore Normal Configuration (After Stable)

Once Odoo runs successfully for 10-15 minutes:

```bash
sudo nano /var/odoo/scholarixv2/odoo.conf
```

Restore worker settings:
```ini
workers = 4
max_cron_threads = 2
```

Restart:
```bash
sudo systemctl restart odoo
# OR
sudo pkill -f odoo-bin
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --log-level=info > logs/odoo.log 2>&1 &
```

---

## 🚨 If Error Persists

### Check PostgreSQL Health
```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"
```

### Increase PostgreSQL Connection Limits
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```
Look for and increase:
```ini
max_connections = 200
shared_buffers = 256MB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Check Disk Space
```bash
df -h
```

### Check Memory
```bash
free -h
```

### Database Vacuum (If Needed)
```bash
sudo -u postgres psql -d scholarixv2 -c "VACUUM ANALYZE;"
```

---

## 📞 Emergency Recovery

If Odoo won't start at all:

1. **Create new database** (backup first):
```bash
sudo -u postgres pg_dump scholarixv2 > /tmp/scholarixv2_backup_$(date +%Y%m%d).sql
```

2. **Reset module states**:
```bash
sudo -u postgres psql -d scholarixv2 -c "UPDATE ir_module_module SET state='uninstalled' WHERE state='to upgrade';"
```

3. **Start with demo disabled**:
```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --without-demo=all
```

---

## 📊 Monitoring After Fix

```bash
# Watch logs continuously
tail -f /var/odoo/scholarixv2/logs/odoo.log

# Monitor database connections
watch -n 5 "sudo -u postgres psql -d scholarixv2 -c 'SELECT count(*) FROM pg_stat_activity;'"

# Check Odoo process
watch -n 5 "ps aux | grep odoo | grep -v grep"
```

---

**Last Updated**: December 2, 2025
**Issue**: Serialization Failure - Concurrent Updates
**Status**: Ready to Deploy
