# Automated CloudPepper Remediation Tool

**Automatically detect and fix CloudPepper compliance issues one by one**

---

## 🚀 Quick Start

### Interactive Mode (Recommended)
Asks for confirmation before each fix:
```bash
python3 auto_remediation.py
```

### Automatic Mode
Fixes all issues without prompting:
```bash
python3 auto_remediation.py --auto
```

### Dry Run Mode
See what would be fixed without making changes:
```bash
python3 auto_remediation.py --dry-run
```

---

## ✨ Features

- **Automatic Issue Detection** - Scans for all CloudPepper compliance issues
- **One-by-One Fixing** - Applies fixes systematically with verification
- **Interactive Confirmation** - Review and approve each fix (optional)
- **Safety First** - Dry-run mode to preview changes
- **Smart Prioritization** - Fixes critical issues first
- **Detailed Logging** - Complete report of all actions taken
- **Rollback Safe** - Each fix is verified before proceeding

---

## 🔍 What Gets Fixed Automatically

### ✅ Critical Issues (Auto-Fixed)

1. **PostgreSQL Service Down**
   - Starts PostgreSQL service
   - Enables on boot
   - Verifies service is running

2. **Odoo Service Down**
   - Detects Odoo service name
   - Starts Odoo service
   - Enables on boot
   - Verifies processes are running

3. **Missing Odoo User**
   - Creates odoo system user
   - Sets home directory to /opt/odoo
   - Creates odoo group
   - Disables login shell (security)

4. **Missing Directories**
   - Creates `/opt/odoo`
   - Creates `/var/log/odoo`
   - Creates `/opt/odoo/.local/share/Odoo`
   - Sets correct ownership (odoo:odoo)
   - Sets correct permissions

5. **Wrong Directory Ownership**
   - Fixes ownership to odoo:odoo
   - Applies recursively
   - Verifies changes

6. **Odoo User Has Login Shell**
   - Disables login shell
   - Sets to /usr/sbin/nologin
   - Security hardening

7. **Workers Not Configured**
   - Calculates optimal workers: (CPU cores * 2) + 1
   - Updates Odoo config
   - Adds memory limits
   - Restarts Odoo service

8. **Firewall Inactive**
   - Allows SSH (port 22) - CRITICAL!
   - Allows HTTP (port 80)
   - Allows HTTPS (port 443)
   - Enables UFW firewall
   - Verifies firewall is active

9. **Missing Backup Directory**
   - Creates `/backup/odoo`
   - Creates subdirectories (database, filestore)
   - Sets ownership to odoo:odoo
   - Sets secure permissions (750)

### ⚠️ Manual Intervention Required

These issues are detected but need manual fixing:

1. **Odoo Config Missing** - Needs database credentials
2. **PostgreSQL Exposed Externally** - Needs config edit & restart
3. **Low max_connections** - Needs PostgreSQL config edit
4. **Disk Space Critical** - Needs manual cleanup
5. **Backup Cron Missing** - Needs database name input
6. **Custom Module Errors** - Needs code review

---

## 📊 Example Output

```bash
$ python3 auto_remediation.py

==================================================================
🤖 AUTOMATED CLOUDPEPPER REMEDIATION
Server: 139.84.163.11
Mode: LIVE FIX
Interactive: Yes
Time: 2025-11-21 10:30:00
==================================================================

🔍 DETECTING ISSUES
==================================================================

🐘 Checking PostgreSQL service...
  ✗ PostgreSQL is not running
🟣 Checking Odoo service...
  ✗ Odoo is not running
👥 Checking system users...
  ✓ Odoo user exists
📁 Checking directory structure...
  ✗ /var/log/odoo missing
  ⚠ /opt/odoo - wrong owner: root:root
⚙️  Checking Odoo configuration...
  ✓ Config file found: /etc/odoo.conf
  ⚠ Workers not configured
🔧 Checking PostgreSQL configuration...
  ✓ max_connections = 100
🔒 Checking firewall...
  ⚠ Firewall inactive
💾 Checking backups...
  ⚠ No backup directory
🔐 Checking security settings...
  ✓ PostgreSQL listening locally only
💽 Checking disk space...
  ✓ Disk space: 45%

📊 Found 6 issue(s) to address

==================================================================
📋 ISSUES SUMMARY
==================================================================

✅ Auto-fixable issues: 6
  • [CRITICAL] PostgreSQL service is not running
  • [CRITICAL] Odoo service is not running
  • [HIGH] Directory /var/log/odoo is missing
  • [HIGH] Directory /opt/odoo has wrong ownership (root:root)
  • [HIGH] Odoo workers not configured (single-process mode)
  • [HIGH] UFW firewall is not active

⚠️  Manual intervention needed: 0

==================================================================
Proceed with fixing 6 issue(s)? [Y/n]: y

==================================================================
🔧 APPLYING FIXES
==================================================================

[1/6]
==================================================================
🔧 Fixing: PostgreSQL service is not running
   Category: PostgreSQL
   Severity: CRITICAL
==================================================================
  Apply fix? [Y/n]: y
  → Starting PostgreSQL service...
  ✅ Fixed successfully!

[2/6]
==================================================================
🔧 Fixing: Odoo service is not running
   Category: Odoo
   Severity: CRITICAL
==================================================================
  Apply fix? [Y/n]: y
  → Found service: odoo-server.service
  → Starting Odoo service...
  ✅ Fixed successfully!

[3/6]
==================================================================
🔧 Fixing: Directory /var/log/odoo is missing
   Category: Directories
   Severity: HIGH
==================================================================
  Apply fix? [Y/n]: y
  → Creating directory: /var/log/odoo
  ✅ Fixed successfully!

[4/6]
==================================================================
🔧 Fixing: Directory /opt/odoo has wrong ownership (root:root)
   Category: Directories
   Severity: HIGH
==================================================================
  Apply fix? [Y/n]: y
  → Fixing ownership: /opt/odoo
  ✅ Fixed successfully!

[5/6]
==================================================================
🔧 Fixing: Odoo workers not configured (single-process mode)
   Category: Performance
   Severity: HIGH
==================================================================
  Apply fix? [Y/n]: y
  → Setting workers = 5 (based on 2 CPUs)
  → Restarting Odoo...
  ✅ Fixed successfully!

[6/6]
==================================================================
🔧 Fixing: UFW firewall is not active
   Category: Security
   Severity: HIGH
==================================================================
  ⚠ IMPORTANT: This will enable the firewall!
  → Ensuring SSH port 22 is allowed first...
  → Enabling firewall...
  Apply fix? [Y/n]: y
  ✅ Fixed successfully!

==================================================================
📊 REMEDIATION REPORT
==================================================================

✅ Issues Fixed: 6
  ✓ PostgreSQL service is not running
  ✓ Odoo service is not running
  ✓ Directory /var/log/odoo is missing
  ✓ Directory /opt/odoo has wrong ownership (root:root)
  ✓ Odoo workers not configured (single-process mode)
  ✓ UFW firewall is not active

❌ Issues Failed: 0

⊘ Issues Skipped: 0

💾 Detailed report saved: remediation_report_20251121_103045.json

==================================================================
✅ REMEDIATION COMPLETE
==================================================================
```

---

## 🎛️ Command Line Options

```bash
python3 auto_remediation.py [OPTIONS]

OPTIONS:
  --auto      Non-interactive mode (no confirmation prompts)
  --dry-run   Show what would be done without making changes
  -h, --help  Show help message

EXAMPLES:
  # Interactive mode (asks before each fix)
  python3 auto_remediation.py

  # Automatic mode (fix all without prompting)
  python3 auto_remediation.py --auto

  # Dry run (preview only)
  python3 auto_remediation.py --dry-run

  # Automatic dry run
  python3 auto_remediation.py --auto --dry-run
```

---

## 🔄 Recommended Workflow

### First Time Setup

1. **Run in dry-run mode** to see what would be fixed:
   ```bash
   python3 auto_remediation.py --dry-run
   ```

2. **Review the issues** that will be fixed

3. **Run in interactive mode** to apply fixes with confirmation:
   ```bash
   python3 auto_remediation.py
   ```

4. **Verify fixes** with compliance checker:
   ```bash
   python3 cloudpepper_compliance_checker.py
   ```

### Regular Maintenance

1. **Weekly automated run:**
   ```bash
   python3 auto_remediation.py --auto >> /var/log/odoo/auto_remediation.log 2>&1
   ```

2. **Review logs** periodically

3. **Run full compliance check** monthly:
   ```bash
   python3 cloudpepper_compliance_checker.py
   ```

---

## 🔒 Safety Features

### Built-in Protections

1. **SSH Port Protection**
   - Always allows SSH (port 22) before enabling firewall
   - Prevents lockout from server

2. **Service Verification**
   - Verifies each fix was successful
   - Waits for services to fully start
   - Checks process status after starting

3. **Dry Run Mode**
   - Preview all changes without applying
   - Safe to run anytime

4. **Interactive Confirmation**
   - Review each fix before applying
   - Skip problematic fixes

5. **Detailed Logging**
   - JSON report of all actions
   - Timestamps for each operation
   - Success/failure tracking

---

## 📝 Output Files

### Remediation Report (JSON)
Detailed report saved as: `remediation_report_YYYYMMDD_HHMMSS.json`

```json
{
  "timestamp": "2025-11-21T10:30:45",
  "server": "139.84.163.11",
  "dry_run": false,
  "fixed": [
    {
      "issue": "PostgreSQL service is not running",
      "status": "fixed",
      "details": "",
      "timestamp": "2025-11-21T10:30:47"
    }
  ],
  "failed": [],
  "skipped": []
}
```

---

## 🆘 Troubleshooting

### Connection Failed
```bash
# Verify SSH key exists
ls -la /tmp/ssh_key

# Fix permissions
chmod 600 /tmp/ssh_key

# Test connection
ssh -i /tmp/ssh_key root@139.84.163.11 "echo OK"
```

### Fix Failed
```bash
# Check the error message in output
# Review logs on server
ssh -i /tmp/ssh_key root@139.84.163.11
tail -100 /var/log/odoo/odoo-server.log
tail -100 /var/log/postgresql/postgresql-*-main.log

# Consult remediation guide
cat CLOUDPEPPER_REMEDIATION_GUIDE.md
```

### Service Won't Start
```bash
# Check service status manually
ssh -i /tmp/ssh_key root@139.84.163.11

# PostgreSQL
systemctl status postgresql
journalctl -u postgresql -n 50

# Odoo
systemctl status odoo-server
journalctl -u odoo-server -n 50
```

---

## 🔄 Integration with Other Tools

### Combined Workflow

1. **Initial Diagnosis:**
   ```bash
   python3 remote_diagnostic.py
   ```

2. **Compliance Check:**
   ```bash
   python3 cloudpepper_compliance_checker.py
   ```

3. **Auto-Fix Issues:**
   ```bash
   python3 auto_remediation.py
   ```

4. **Verify Fixes:**
   ```bash
   python3 cloudpepper_compliance_checker.py
   ```

5. **Manual Fixes** (if needed):
   ```bash
   cat CLOUDPEPPER_REMEDIATION_GUIDE.md
   ```

---

## 🎯 Success Criteria

After running auto-remediation:

- ✅ PostgreSQL service running
- ✅ Odoo service running
- ✅ All standard directories exist
- ✅ Correct ownership (odoo:odoo)
- ✅ Workers configured for production
- ✅ Firewall enabled and configured
- ✅ Backup directory structure created
- ✅ Security hardening applied

---

## 📊 Comparison: Manual vs Automated

| Task | Manual | Automated |
|------|--------|-----------|
| Detect issues | ~30 minutes | ~2 minutes |
| Fix PostgreSQL down | 2 minutes | 10 seconds |
| Create directories | 5 minutes | 5 seconds |
| Fix ownership | 5 minutes | 5 seconds |
| Configure workers | 10 minutes | 30 seconds |
| Enable firewall | 5 minutes | 10 seconds |
| Verify all fixes | 15 minutes | Automatic |
| **TOTAL** | **~72 minutes** | **~3 minutes** |

---

## 🔐 Security Notes

1. **SSH Key** - Private key stored at `/tmp/ssh_key`
2. **Root Access** - Script runs as root on remote server
3. **Firewall** - Always enables SSH before activating firewall
4. **Audit Trail** - All actions logged in JSON report
5. **Verification** - Each fix is verified before proceeding

---

## 📚 Related Documentation

- **CLOUDPEPPER_REMEDIATION_GUIDE.md** - Manual fix instructions
- **COMPLIANCE_QUICK_START.md** - Quick reference guide
- **cloudpepper_compliance_checker.py** - Detection-only tool
- **remote_diagnostic.py** - General diagnostics
- **DIAGNOSTIC_INSTRUCTIONS.md** - Comprehensive documentation

---

## 💡 Tips & Best Practices

1. **Always run dry-run first** on production systems
2. **Use interactive mode** for critical servers
3. **Review logs** after automated runs
4. **Schedule regular checks** (weekly/monthly)
5. **Backup before major fixes** (config files, databases)
6. **Test in staging** before production
7. **Document custom changes** that might conflict

---

## 🆘 Support

If auto-remediation fails:

1. Review the JSON report for details
2. Check server logs (PostgreSQL, Odoo)
3. Consult CLOUDPEPPER_REMEDIATION_GUIDE.md
4. Run manual compliance check
5. Fix remaining issues manually

---

**Version:** 1.0
**Last Updated:** 2025-11-21
**Tested On:** Ubuntu 20.04/22.04, Debian 11/12
**Odoo Version:** 17.0
