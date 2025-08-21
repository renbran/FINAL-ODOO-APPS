#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CloudPepper Emergency Syntax Error Fix
======================================

CRITICAL SERVER ERROR RESOLUTION:
SyntaxError: invalid syntax in manifest file during database initialization

This script provides emergency fixes for CloudPepper production deployment.
"""

import os
import sys
import shutil
from datetime import datetime

def create_emergency_fix_report():
    """Create comprehensive emergency fix report."""
    
    report = f"""
# 🚨 CLOUDPEPPER EMERGENCY SYNTAX ERROR - RESOLUTION GUIDE

## 📅 Emergency Response Report
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Environment**: CloudPepper Production (erposus.com)
**Error Type**: SyntaxError in __manifest__.py during database initialization
**Status**: 🔧 **EMERGENCY RESPONSE ACTIVE**

## 🚨 Critical Error Analysis

### Error Details
```
SyntaxError: invalid syntax
Failed to initialize database `erposus`
File: /var/odoo/erposus/src/odoo/modules/module.py, line 319
manifest.update(ast.literal_eval(f.read()))
```

### Root Cause Analysis
The error occurs when Odoo tries to parse a __manifest__.py file during module loading.
This indicates one of the following issues:

1. **Corrupted Upload**: A manifest file was partially uploaded or corrupted
2. **Encoding Issue**: Non-UTF-8 characters in a manifest file
3. **Syntax Error**: Invalid Python syntax in a manifest file
4. **Empty File**: A manifest file is empty or contains only whitespace
5. **File System Issue**: Disk corruption or permission problems

## 🔧 EMERGENCY FIX PROCEDURES

### Option 1: Quick Recovery (RECOMMENDED)
```bash
# On CloudPepper server:
cd /var/odoo/erposus/addons

# Find and check all manifest files
find . -name "__manifest__.py" -exec python3 -m py_compile {{}} \\;

# If a file shows syntax error, backup and replace:
cp problematic_module/__manifest__.py problematic_module/__manifest__.py.backup
# Upload clean version from development
```

### Option 2: Emergency Module Removal
```bash
# Temporarily move problematic module
mv problematic_module /tmp/problematic_module.backup

# Restart Odoo
sudo systemctl restart odoo
```

### Option 3: Emergency Database Reset (LAST RESORT)
```bash
# Only if database is completely corrupted
sudo -u postgres dropdb erposus
sudo -u postgres createdb erposus
# Restore from latest backup
```

## 🎯 IMMEDIATE ACTION PLAN

### Step 1: Identify Problematic Module
```bash
# Run this on CloudPepper server:
cd /var/odoo/erposus/addons
for manifest in $(find . -name "__manifest__.py"); do
    echo "Checking: $manifest"
    python3 -c "
import ast
try:
    with open('$manifest', 'r') as f:
        ast.literal_eval(f.read())
    print('✅ OK: $manifest')
except Exception as e:
    print('❌ ERROR in $manifest: ', str(e))
"
done
```

### Step 2: Emergency Backup
```bash
# Create emergency backup of current state
sudo tar -czf /tmp/emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/odoo/erposus/addons
```

### Step 3: Upload Clean Manifests
```bash
# Re-upload all manifest files from development environment
# Focus on recently modified modules:
# - oe_sale_dashboard_17
# - account_payment_approval  
# - account_payment_final
# - Any other recently modified modules
```

### Step 4: Verify and Restart
```bash
# Verify all manifests are clean
cd /var/odoo/erposus/addons
find . -name "__manifest__.py" -exec python3 -m py_compile {{}} \\;

# Restart Odoo service
sudo systemctl restart odoo

# Check logs
sudo journalctl -u odoo -f
```

## 🛡️ PREVENTION MEASURES

### File Upload Verification
1. **Always verify file integrity after upload**
2. **Check file encoding (must be UTF-8)**
3. **Validate Python syntax before deployment**
4. **Use atomic uploads (complete or nothing)**

### Deployment Checklist
- [ ] Run syntax checker before upload
- [ ] Verify file encoding
- [ ] Test in staging environment first
- [ ] Create backup before deployment
- [ ] Monitor logs during deployment

### Monitoring Setup
```bash
# Add to CloudPepper monitoring:
# File integrity checks
# Syntax validation on upload
# Automatic backup on failure
# Real-time log monitoring
```

## 🚀 RECOVERY VERIFICATION

### Success Indicators
- [ ] Odoo service starts without errors
- [ ] Database initializes successfully
- [ ] All modules load correctly
- [ ] Web interface accessible
- [ ] No syntax errors in logs

### Post-Recovery Testing
1. **Login Test**: Verify admin login works
2. **Module Test**: Check all installed modules
3. **Functionality Test**: Test critical business processes
4. **Performance Test**: Verify normal response times

## 📞 EMERGENCY CONTACTS

### If This Guide Doesn't Resolve the Issue:
1. **Check CloudPepper server disk space**: `df -h`
2. **Check file permissions**: `ls -la /var/odoo/erposus/addons`
3. **Review system logs**: `sudo journalctl -xe`
4. **Contact CloudPepper support** with error details

## 🎯 EXPECTED RESOLUTION TIME

- **Quick Fix**: 5-10 minutes (if simple syntax error)
- **Module Replacement**: 15-20 minutes (if corrupted upload)
- **Full Recovery**: 30-45 minutes (if multiple issues)

---

**CRITICAL**: This is a production system emergency. Act quickly but carefully.
All commands should be executed with proper backups in place.

**Status**: Emergency response procedures ready for immediate deployment.
"""
    
    return report

def main():
    """Generate emergency fix documentation."""
    
    print("🚨 GENERATING CLOUDPEPPER EMERGENCY FIX GUIDE...")
    
    # Create emergency fix report
    report_content = create_emergency_fix_report()
    
    # Save to file
    report_filename = f"CLOUDPEPPER_EMERGENCY_SYNTAX_FIX_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ Emergency fix guide created: {report_filename}")
    print()
    print("🎯 IMMEDIATE ACTION REQUIRED:")
    print("1. Upload this guide to CloudPepper server")
    print("2. Follow Step 1 to identify problematic manifest")
    print("3. Create emergency backup (Step 2)")
    print("4. Replace corrupted file (Step 3)")
    print("5. Restart and verify (Step 4)")
    print()
    print("🚀 Expected resolution time: 5-15 minutes")
    
if __name__ == "__main__":
    main()
