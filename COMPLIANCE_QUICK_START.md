# CloudPepper Compliance Check - Quick Start Guide

**Server:** 139.84.163.11
**Purpose:** Identify and fix CloudPepper setup issues, database problems, and problematic custom apps
**Date:** 2025-11-21

---

## 🚀 Quick Start (3 Steps)

### Step 1: Run the Compliance Checker

```bash
# Make sure you're in the project directory
cd /home/user/FINAL-ODOO-APPS

# Install dependencies (if not already installed)
pip3 install paramiko

# Run the compliance checker
python3 cloudpepper_compliance_checker.py
```

**What it checks:**
- ✅ CloudPepper user configuration
- ✅ Directory structure and permissions
- ✅ Odoo configuration files
- ✅ PostgreSQL setup and performance
- ✅ Database health (size, connections, bloat, encoding)
- ✅ Custom module issues (syntax errors, missing files)
- ✅ System resources (disk, memory, CPU)
- ✅ Security configuration (firewall, SSH, PostgreSQL)
- ✅ Backup configuration and recent backups

### Step 2: Review the Report

The script will output:
- **Green (✓)**: Everything working correctly
- **Yellow (⚠)**: Warnings - needs attention
- **Red (✗)**: Critical issues - immediate fix required

Example output:
```
✅ SUCCESSES (15):
  ✓ [Users] Odoo user exists
  ✓ [PostgreSQL] PostgreSQL service is running
  ...

⚠️  WARNINGS (5):
  ⚠ [Security] UFW firewall is inactive
  ⚠ [Performance] Workers set to 0 (low for production)
  ...

❌ CRITICAL ISSUES (2):
  ✗ [CRITICAL] [Directories] /var/log/odoo does not exist
  ✗ [HIGH] [Databases] Database 'production' has 75 active connections (high)
  ...

💡 RECOMMENDATIONS (7):
  1. Create directory: sudo mkdir -p /var/log/odoo && sudo chown odoo:odoo /var/log/odoo
  2. Increase workers for production: workers = (CPU cores * 2) + 1
  ...

📈 OVERALL HEALTH SCORE: 65.2%
   Status: ⚠️  FAIR - Improvements needed
```

A detailed JSON report will be saved: `cloudpepper_compliance_YYYYMMDD_HHMMSS.json`

### Step 3: Fix Issues Using the Remediation Guide

Open the remediation guide:
```bash
cat CLOUDPEPPER_REMEDIATION_GUIDE.md
```

Or use your favorite editor:
```bash
nano CLOUDPEPPER_REMEDIATION_GUIDE.md
```

Follow the step-by-step fixes for each issue identified.

---

## 📊 What Gets Checked

### 1. CloudPepper Users (👥)
- ✓ Odoo system user exists
- ✓ PostgreSQL user exists
- ✓ Correct user permissions
- ✓ Secure shell configuration

**Issues detected:**
- Missing users
- Wrong shell permissions
- Incorrect user configuration

### 2. Directory Structure (📁)
- ✓ `/opt/odoo` - Main installation
- ✓ `/var/log/odoo` - Log files
- ✓ `/opt/odoo/.local/share/Odoo` - Data directory
- ✓ Correct ownership (odoo:odoo)
- ✓ Proper permissions

**Issues detected:**
- Missing directories
- Wrong ownership
- Incorrect permissions

### 3. Odoo Configuration (⚙️)
- ✓ Config file location
- ✓ Critical settings (db_host, db_port, addons_path)
- ✓ Worker configuration
- ✓ Memory limits
- ✓ Log file configuration

**Issues detected:**
- Missing configuration file
- Workers not configured (single-process mode)
- Missing critical parameters
- Wrong paths

### 4. PostgreSQL Setup (🐘)
- ✓ Service running
- ✓ Version compatibility
- ✓ Connection accessibility
- ✓ max_connections setting
- ✓ shared_buffers configuration
- ✓ Listen addresses (security)

**Issues detected:**
- Service not running
- Low max_connections
- Poor memory configuration
- External exposure (security risk)

### 5. Database Health (💾)
- ✓ Database list and sizes
- ✓ Active connections per database
- ✓ Bloated tables detection
- ✓ Long-running queries
- ✓ Database encoding (UTF8)
- ✓ Unused databases

**Issues detected:**
- Very large databases (>50GB)
- Too many connections
- Non-UTF8 encoding
- Long-running queries
- Bloated tables

### 6. Custom Modules (🔌)
- ✓ Module detection in addons_path
- ✓ Missing `__init__.py`
- ✓ Manifest file validation
- ✓ Python syntax errors
- ✓ Installable flag
- ✓ Recent error logs

**Issues detected:**
- Missing `__init__.py`
- Python syntax errors
- Modules marked as not installable
- Missing version information
- Recent errors in logs

### 7. System Resources (💻)
- ✓ Disk usage and available space
- ✓ Memory usage
- ✓ CPU load average
- ✓ Performance thresholds

**Issues detected:**
- High disk usage (>80%)
- High memory usage (>90%)
- High CPU load
- Resource constraints

### 8. Security Configuration (🔒)
- ✓ UFW firewall status
- ✓ SSH configuration
- ✓ PostgreSQL external exposure
- ✓ Port security
- ✓ Root login settings

**Issues detected:**
- Firewall disabled
- Root SSH login enabled
- PostgreSQL exposed externally
- Weak security settings

### 9. Backup Configuration (💾)
- ✓ Backup directories exist
- ✓ Recent backups found (last 7 days)
- ✓ Backup cron jobs configured
- ✓ Backup scripts present

**Issues detected:**
- No backup directory
- No recent backups
- Missing cron jobs
- No backup automation

---

## 🎯 Common Issues & Quick Fixes

### Issue: "PostgreSQL service is NOT running"
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Issue: "Odoo user does not exist"
```bash
sudo adduser --system --home=/opt/odoo --group odoo
```

### Issue: "Directory /var/log/odoo does not exist"
```bash
sudo mkdir -p /var/log/odoo
sudo chown odoo:odoo /var/log/odoo
```

### Issue: "Workers set to 0 (low for production)"
```bash
sudo nano /etc/odoo.conf
# Add: workers = 4
sudo systemctl restart odoo-server
```

### Issue: "UFW firewall is inactive"
```bash
sudo ufw allow 22/tcp  # SSH - IMPORTANT!
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Issue: "No backup cron job found"
```bash
# See full backup setup in CLOUDPEPPER_REMEDIATION_GUIDE.md section 9
```

---

## 📈 Health Score Interpretation

| Score | Status | Action Required |
|-------|--------|----------------|
| 90-100% | ✅ EXCELLENT | Maintain current setup |
| 75-89% | ✅ GOOD | Minor improvements recommended |
| 60-74% | ⚠️ FAIR | Improvements needed |
| Below 60% | ❌ POOR | Immediate attention required |

---

## 🔄 Running Periodic Checks

### Recommended Schedule

1. **After initial setup** - Run compliance check
2. **After configuration changes** - Verify no issues introduced
3. **Weekly** - Quick health check
4. **Monthly** - Full compliance audit
5. **Before major updates** - Baseline check

### Automated Monitoring

Create a cron job for weekly checks:

```bash
# Add to root crontab
sudo crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /home/user/FINAL-ODOO-APPS && python3 cloudpepper_compliance_checker.py >> /var/log/odoo/compliance_check.log 2>&1
```

---

## 🆘 Troubleshooting

### Cannot Connect to Server

```bash
# Test network connectivity
nc -zv 139.84.163.11 22

# Verify SSH key
ls -la /tmp/ssh_key
# Should show: -rw------- (600 permissions)

# Test SSH connection
ssh -i /tmp/ssh_key root@139.84.163.11 "echo 'Connection successful'"
```

### Script Fails with Import Error

```bash
# Install missing dependency
pip3 install paramiko

# Verify installation
python3 -c "import paramiko; print('OK')"
```

### Script Times Out

```bash
# Increase timeout in script or run checks individually
# Or run the bash script version directly on server
```

---

## 📚 Additional Resources

1. **CLOUDPEPPER_REMEDIATION_GUIDE.md** - Detailed fix instructions for all issues
2. **remote_diagnostic.py** - General diagnostic script (broader checks)
3. **odoo_db_diagnostic.sh** - Bash script version (run on server)
4. **DIAGNOSTIC_INSTRUCTIONS.md** - Original diagnostic documentation

---

## 🔐 Security Note

The SSH private key is stored at `/tmp/ssh_key`. After completing the checks:

```bash
# Remove the key for security
rm /tmp/ssh_key
```

If you need to run checks again, you'll need to recreate the key file.

---

## 📝 Example Workflow

```bash
# 1. Run compliance check
python3 cloudpepper_compliance_checker.py > check_output.txt 2>&1

# 2. Review output
cat check_output.txt

# 3. Review JSON report (more detailed)
cat cloudpepper_compliance_*.json | jq '.'

# 4. For each critical issue, open remediation guide
cat CLOUDPEPPER_REMEDIATION_GUIDE.md | grep -A 20 "Issue: <your issue>"

# 5. Apply fixes (SSH to server)
ssh -i /tmp/ssh_key root@139.84.163.11

# 6. Re-run compliance check to verify
python3 cloudpepper_compliance_checker.py
```

---

## ✅ Success Criteria

Your Odoo 17 CloudPepper setup is compliant when:

- ✅ Health score > 90%
- ✅ No critical issues (red)
- ✅ Less than 3 warnings (yellow)
- ✅ PostgreSQL running and optimized
- ✅ Odoo running with workers configured
- ✅ All standard directories exist with correct permissions
- ✅ Firewall enabled and configured
- ✅ Automated backups running
- ✅ No custom module errors
- ✅ System resources within healthy ranges

---

**For detailed remediation steps, see:** `CLOUDPEPPER_REMEDIATION_GUIDE.md`

**For general diagnostics, see:** `DIAGNOSTIC_INSTRUCTIONS.md`

---

Generated: 2025-11-21
Version: 1.0
