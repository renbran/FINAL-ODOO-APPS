# ScholarixV2 Server Reference - CloudPepper/Vultr

**Server IP**: `139.84.163.11`
**User**: `root`
**SSH Connection**: `ssh -i "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt" root@139.84.163.11`

---

## 📁 Directory Structure

| Path | Description |
|------|-------------|
| **Source Code** | `/var/odoo/scholarixv2/src` |
| **Log Files** | `/var/odoo/scholarixv2/logs` |
| **Config File** | `/var/odoo/scholarixv2/odoo.conf` |
| **Python venv** | `/var/odoo/scholarixv2/venv/bin/python3` |
| **Custom Addons** | `/var/odoo/scholarixv2/src/addons` (typical location) |

---

## 🗄️ Database

**Database Name**: `scholarixv2`

---

## 🐍 Python Commands

### **Odoo Shell Access**
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
```

### **Install Python Packages**
```bash
sudo -u odoo /var/odoo/scholarixv2/venv/bin/python3 -m pip install <package_name>
```

**Example**:
```bash
sudo -u odoo /var/odoo/scholarixv2/venv/bin/python3 -m pip install jwt requests openai
```

---

## 🔄 Odoo Module Management

### **Update All Modules**
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update all
```

### **Update Specific Module**
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u <module_name>
```

**Example**:
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u rental_management
```

### **Install New Module**
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -i <module_name>
```

---

## 🚀 Service Management

### **Check Odoo Service Status**
```bash
systemctl status odoo-scholarixv2
# or
ps aux | grep odoo
```

### **Restart Odoo Service**
```bash
systemctl restart odoo-scholarixv2
# or if service name is different:
systemctl restart odoo
```

### **Stop Odoo Service**
```bash
systemctl stop odoo-scholarixv2
```

### **Start Odoo Service**
```bash
systemctl start odoo-scholarixv2
```

### **View Live Logs**
```bash
tail -f /var/odoo/scholarixv2/logs/odoo.log

# Or filter for errors:
tail -f /var/odoo/scholarixv2/logs/odoo.log | grep ERROR

# Or check systemd logs:
journalctl -u odoo-scholarixv2 -f
```

---

## 📦 Module Deployment Workflow

### **1. Upload Module to Server**
```powershell
# From Windows (PowerShell)
scp -i "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt" -r "D:\RUNNING APPS\FINAL-ODOO-APPS\rental_management" root@139.84.163.11:/var/odoo/scholarixv2/src/addons/
```

### **2. Set Correct Permissions**
```bash
# On server
chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/rental_management
chmod -R 755 /var/odoo/scholarixv2/src/addons/rental_management
```

### **3. Update/Install Module**
```bash
# For existing module update
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u rental_management

# For new module installation
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -i rental_management
```

### **4. Restart Odoo**
```bash
systemctl restart odoo-scholarixv2
```

### **5. Verify Deployment**
```bash
# Check logs for errors
tail -50 /var/odoo/scholarixv2/logs/odoo.log

# Check if module is loaded
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2
# Then in Odoo shell:
# self.env['ir.module.module'].search([('name', '=', 'rental_management')])
```

---

## 🔍 Troubleshooting Commands

### **Check Odoo Configuration**
```bash
cat /var/odoo/scholarixv2/odoo.conf
```

### **Check Python Version**
```bash
/var/odoo/scholarixv2/venv/bin/python3 --version
```

### **List Installed Python Packages**
```bash
/var/odoo/scholarixv2/venv/bin/pip list
```

### **Check Database Connection**
```bash
psql -U odoo -d scholarixv2 -c "SELECT datname FROM pg_database WHERE datname = 'scholarixv2';"
```

### **Check Disk Space**
```bash
df -h /var/odoo/scholarixv2
```

### **Check Module Directory**
```bash
ls -la /var/odoo/scholarixv2/src/addons/rental_management
```

### **Search for Module Files**
```bash
find /var/odoo/scholarixv2 -name "rental_management" -type d
```

### **Check Odoo Process**
```bash
ps aux | grep odoo | grep scholarixv2
```

---

## 🔐 Database Operations

### **Backup Database**
```bash
pg_dump -U odoo scholarixv2 > /tmp/scholarixv2_backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Restore Database**
```bash
psql -U odoo -d scholarixv2 < /tmp/scholarixv2_backup_20251201.sql
```

### **Connect to PostgreSQL**
```bash
psql -U odoo -d scholarixv2
```

### **List All Modules in Database**
```sql
-- In psql:
SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE '%rental%';
```

---

## 📝 Quick Reference Commands

```bash
# SSH Connect
ssh -i ~/.ssh/cloudpepper_rental_mgmt root@139.84.163.11

# Navigate to Odoo directory
cd /var/odoo/scholarixv2

# Update rental_management module
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u rental_management

# Restart Odoo
systemctl restart odoo-scholarixv2

# View logs
tail -f /var/odoo/scholarixv2/logs/odoo.log

# Odoo shell
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d scholarixv2
```

---

## 🎯 Sale Contract Payment Schedule Deployment

### **Deploy Updated rental_management Module**

```bash
# 1. Upload module from Windows
scp -i "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt" -r "D:\RUNNING APPS\FINAL-ODOO-APPS\rental_management" root@139.84.163.11:/tmp/

# 2. SSH to server
ssh -i "$env:USERPROFILE\.ssh\cloudpepper_rental_mgmt" root@139.84.163.11

# 3. Backup current module
cp -r /var/odoo/scholarixv2/src/addons/rental_management /var/odoo/scholarixv2/src/addons/rental_management.backup_$(date +%Y%m%d_%H%M%S)

# 4. Replace module
rm -rf /var/odoo/scholarixv2/src/addons/rental_management
mv /tmp/rental_management /var/odoo/scholarixv2/src/addons/

# 5. Set permissions
chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/rental_management
chmod -R 755 /var/odoo/scholarixv2/src/addons/rental_management

# 6. Update module
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u rental_management

# 7. Restart Odoo
systemctl restart odoo-scholarixv2

# 8. Check logs for errors
tail -100 /var/odoo/scholarixv2/logs/odoo.log | grep -E "(ERROR|WARNING)"
```

---

**Last Updated**: December 1, 2025
**Purpose**: Reference for ScholarixV2 server operations and rental_management deployment
