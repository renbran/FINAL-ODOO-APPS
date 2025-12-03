# 📂 Server Path Reference - scholarixv2

**Last Updated**: December 3, 2025  
**Server**: scholarixglobal.com (139.84.163.11)  
**Database**: scholarixv2

---

## ✅ Correct Server Paths

### Base Installation
```bash
# Main Odoo directory
/var/odoo/scholarixv2/

# Directory Structure:
├── src/                          # Odoo source code
│   ├── odoo-bin                  # Main executable
│   ├── addons/                   # Core Odoo modules
│   └── odoo/                     # Odoo framework
│
├── extra-addons/                 # Custom module repositories
│   ├── cybroaddons.git-68f85fe88986a/   # Cybro addons (rental_management is here)
│   └── odooapps.git-68ee71eda34bc/      # Other custom modules
│
├── venv/                         # Python virtual environment
│   └── bin/
│       └── python3               # Python interpreter
│
├── logs/                         # Log files
├── backups/                      # Database backups
└── odoo.conf                     # Configuration file
```

---

## 🎯 Critical Paths for Operations

### 1. Odoo Source Code
```bash
/var/odoo/scholarixv2/src
```

### 2. Odoo Executable
```bash
/var/odoo/scholarixv2/src/odoo-bin
```

### 3. Configuration File
```bash
/var/odoo/scholarixv2/odoo.conf
```

### 4. Python Virtual Environment
```bash
/var/odoo/scholarixv2/venv/bin/python3
```

### 5. Log Files Directory
```bash
/var/odoo/scholarixv2/logs/
```

### 6. Custom Modules (Extra Addons)

**Primary Path** (where rental_management is located):
```bash
/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/
```

**Example - rental_management module**:
```bash
/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/
```

**Secondary Path** (other modules):
```bash
/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/
```

### 7. Database Filestore
```bash
/var/odoo/.local/share/Odoo/filestore/scholarixv2/
```

---

## 📝 Configuration File Contents

**File**: `/var/odoo/scholarixv2/odoo.conf`

```ini
[options]
db_name = scholarixv2
db_user = odoo
proxy_mode = True
list_db = False
workers = 2
addons_path = /var/odoo/scholarixv2/src/addons,/var/odoo/scholarixv2/src/odoo,/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc,/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a
data_dir = /var/odoo/.local/share/Odoo/filestore/scholarixv2
database_secret = db719cf9-6984-42b0-bc2d-ae4784d38b62
```

---

## 🚀 Common Operations with Correct Paths

### Access Odoo Shell
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
```

### Update Specific Module
```bash
cd /var/odoo/scholarixv2 && \
sudo -u odoo venv/bin/python3 src/odoo-bin \
  -c odoo.conf \
  -d scholarixv2 \
  --update=rental_management \
  --stop-after-init
```

### Update All Modules
```bash
cd /var/odoo/scholarixv2 && \
sudo -u odoo venv/bin/python3 src/odoo-bin \
  -c odoo.conf \
  -d scholarixv2 \
  --update=all \
  --stop-after-init
```

### Install Python Packages
```bash
sudo -u odoo /var/odoo/scholarixv2/venv/bin/python3 -m pip install <package_name>
```

### View Recent Logs
```bash
sudo tail -100 /var/odoo/scholarixv2/logs/odoo.log
```

### Check Odoo Service Status
```bash
sudo systemctl status odoo
```

### Restart Odoo Service
```bash
sudo systemctl restart odoo
```

---

## 📦 Module Installation Paths

When deploying custom modules, use these paths:

### From Local to Server (SCP)
```bash
# Upload module to cybroaddons directory
scp -r local_module_name/ root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/

# Fix permissions after upload
ssh cloudpepper "chown -R odoo:odoo /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/module_name"
```

### Git Clone Method (If using Git)
```bash
cd /var/odoo/scholarixv2/extra-addons/
git clone <repository_url> new_module_directory
chown -R odoo:odoo new_module_directory/
```

---

## 🔍 Verification Commands

### Check if Module Exists
```bash
ls -la /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management
```

### Verify Python Interpreter
```bash
/var/odoo/scholarixv2/venv/bin/python3 --version
```

### Check Odoo Version
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin --version
```

### List Installed Modules (via Python)
```bash
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 -c "
import sys
sys.path.insert(0, 'src')
import odoo
from odoo.tools import config
config.parse_config(['-c', 'odoo.conf'])
from odoo.modules.registry import Registry
r = Registry('scholarixv2')
with r.cursor() as cr:
    env = odoo.api.Environment(cr, 1, {})
    modules = env['ir.module.module'].search([('state', '=', 'installed')])
    for m in modules:
        print(f'{m.name}: {m.latest_version}')
"
```

---

## ⚠️ Common Path Mistakes to Avoid

### ❌ WRONG Paths (DO NOT USE):
```bash
# These paths DON'T EXIST:
/opt/odoo/                        # Wrong base directory
/home/odoo/                       # Wrong user directory
/var/odoo/odoo/                   # Wrong subdirectory
/var/odoo/addons/                 # Missing scholarixv2
```

### ✅ CORRECT Paths (ALWAYS USE):
```bash
# Always use these:
/var/odoo/scholarixv2/src/
/var/odoo/scholarixv2/extra-addons/
/var/odoo/scholarixv2/venv/
/var/odoo/scholarixv2/odoo.conf
```

---

## 🔐 User Permissions

**Odoo Process User**: `odoo`  
**File Ownership**: `odoo:odoo`

Always run Odoo commands as the `odoo` user:
```bash
sudo -u odoo <command>
```

---

## 📊 Module Locations Map

| Module Type | Location |
|-------------|----------|
| Core Odoo Modules | `/var/odoo/scholarixv2/src/addons/` |
| Custom Cybro Modules | `/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/` |
| Custom OdooApps Modules | `/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/` |
| rental_management | `/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/` |

---

## 🔄 Path Usage in Recent Fixes

### rental_management attrs Fix (Dec 3, 2025)
```bash
# File modified:
/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/views/res_config_setting_view.xml

# Update command used:
cd /var/odoo/scholarixv2 && \
sudo -u odoo venv/bin/python3 src/odoo-bin \
  -c odoo.conf \
  -d scholarixv2 \
  --update=rental_management \
  --stop-after-init
```

---

## 📝 Quick Reference Card

```bash
# Base Directory
BASE=/var/odoo/scholarixv2

# Source Code
SRC=$BASE/src

# Python Interpreter
PYTHON=$BASE/venv/bin/python3

# Config File
CONFIG=$BASE/odoo.conf

# Custom Modules
MODULES=$BASE/extra-addons/cybroaddons.git-68f85fe88986a

# Odoo Binary
ODOO_BIN=$SRC/odoo-bin

# Logs
LOGS=$BASE/logs
```

---

**Last Verified**: December 3, 2025, 07:35 UTC  
**Verified By**: GitHub Copilot AI Agent  
**Server Status**: ✅ Operational
