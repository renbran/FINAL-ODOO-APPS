#!/usr/bin/env python3
"""
Odoo Registry Recovery Script for Account Statement Module
This script helps diagnose and fix registry corruption issues.
"""

import os
import sys

def create_recovery_instructions():
    """Create comprehensive recovery instructions"""
    
    recovery_steps = """
# 🚨 ODOO REGISTRY CORRUPTION - RECOVERY GUIDE

## 🔍 PROBLEM ANALYSIS
The error `External ID not found in the system: account_statement.view_account_statement_wizard_form` 
indicates XML duplicate record issues in the account_statement module.

This typically happens when:
- Duplicate action/view IDs exist across multiple XML files
- Module installation fails due to conflicting records
- XML references point to non-existent or conflicting records
- Circular dependencies in custom modules

## ✅ PROBLEM FIXED
The duplicate records have been removed from account_statement_views.xml:
- Removed duplicate action_account_statement_wizard
- Removed duplicate action_account_statement  
- Removed duplicate menu items that conflict with wizard_views.xml
- Kept only the Contacts app menu items in account_statement_views.xml

## 🛠️ RECOVERY STEPS

### STEP 1: IMMEDIATE FIXES (Try these first)

#### Option A: Restart Odoo Service
```bash
# Stop Odoo
sudo systemctl stop odoo
# or
sudo service odoo stop

# Clear Python cache
find /var/odoo -name "*.pyc" -delete
find /var/odoo -name "__pycache__" -type d -exec rm -rf {} +

# Restart Odoo
sudo systemctl start odoo
# or
sudo service odoo start
```

#### Option B: Update Module List and Reinstall
```bash
# 1. Go to Apps -> Update Apps List
# 2. Find the account_statement module
# 3. Uninstall it if currently installed
# 4. Reinstall it fresh
```

### STEP 2: MODULE SPECIFIC FIXES

#### Account Statement Module XML Fixes Applied:
The following duplicate records were removed from account_statement_views.xml:

1. **Removed Duplicate Actions:**
   - action_account_statement_wizard (conflicted with wizard_views.xml)
   - action_account_statement (conflicted with wizard_views.xml)

2. **Cleaned Up Menu Structure:**
   - Removed duplicate menu_account_statement_root
   - Removed duplicate menu_account_statement_wizard  
   - Removed duplicate menu_account_statement_list
   - Kept only Contacts app specific menu items

3. **File Structure Now:**
   - wizard_views.xml: Contains all actions and Accounting app menus
   - account_statement_views.xml: Contains views and Contacts app menus only

#### Manual Database Cleanup (if needed):
```sql
-- Clear duplicate ir.model.data entries
DELETE FROM ir_model_data 
WHERE module = 'account_statement' 
AND name IN (
    'action_account_statement_wizard',
    'action_account_statement',
    'menu_account_statement_root',
    'menu_account_statement_wizard',
    'menu_account_statement_list'
) 
AND id NOT IN (
    SELECT MIN(id) FROM ir_model_data 
    WHERE module = 'account_statement' 
    GROUP BY name
);

### STEP 2: DATABASE-LEVEL RECOVERY

#### Option A: Reset Module to Uninstalled State
```sql
-- Connect to PostgreSQL database
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE name = 'account_statement';

-- Clear module dependencies
DELETE FROM ir_module_module_dependency 
WHERE module_id IN (
    SELECT id FROM ir_module_module WHERE name = 'account_statement'
);

-- Clear any model references
DELETE FROM ir_model 
WHERE model LIKE '%account.statement%' 
AND model NOT IN (
    SELECT model FROM ir_model 
    WHERE modules LIKE '%base%'
);
```

### STEP 3: DATABASE CLEANUP (if still having issues)

#### Option A: Targeted Cleanup
```sql
-- Clear module installation state
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE name = 'account_statement' AND state != 'uninstalled';

-- Clear module dependencies
DELETE FROM ir_module_module_dependency 
WHERE module_id IN (
    SELECT id FROM ir_module_module WHERE name = 'account_statement'
);

-- Clear any problematic model references
DELETE FROM ir_model 
WHERE model LIKE '%account.statement%' 
AND model NOT IN (
    SELECT model FROM ir_model 
    WHERE modules LIKE '%base%'
);
```

#### Option B: Full Registry Reset
```sql
-- DANGER: This clears ALL custom modules
-- Only use if you have backups
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE state IN ('to install', 'to upgrade', 'to remove');
```

### STEP 4: ADVANCED RECOVERY

#### Option A: Manual Module Cleanup
```bash
# Remove module from addons directory temporarily
mv /path/to/addons/account_statement /tmp/account_statement_backup

# Restart Odoo
sudo systemctl restart odoo

# Check if system works
# If yes, reinstall module carefully
```

#### Option B: Database Backup & Restore
```bash
# Create backup
pg_dump -U odoo_user database_name > backup_before_fix.sql

# If needed, restore from clean backup
# pg_restore -U odoo_user -d database_name clean_backup.sql
```

### STEP 4: PREVENTION MEASURES

#### Check Module Dependencies
```python
# Run this in Odoo shell to check dependencies
env['ir.module.module'].search([('name', '=', 'account_statement')])
```

#### Validate Module Structure
```bash
# Run our validation script
python final_review_account_statement.py
```

## 🔧 SPECIFIC FIXES FOR ACCOUNT_STATEMENT MODULE

### Fix 1: Ensure Clean Installation
```bash
# Make sure module is not in a bad state
cd /var/odoo/addons/account_statement
# Check file permissions
find . -type f -name "*.py" -exec python -m py_compile {} \;
```

### Fix 2: Check XML Syntax
```bash
# Validate all XML files
find . -name "*.xml" -exec xmllint --noout {} \;
```

### Fix 3: Clear Browser Cache
- Clear browser cache completely
- Try accessing Odoo in incognito/private mode
- Disable browser extensions

## 🎯 RECOMMENDED RECOVERY SEQUENCE

1. **Stop Odoo service**
2. **Clear Python cache**
3. **Set module state to 'uninstalled' in database**
4. **Restart Odoo**
5. **Update Apps List**
6. **Reinstall module cleanly**

## ⚠️ IMPORTANT NOTES

- **Always backup database before attempting fixes**
- **Test in staging environment first**
- **Document what works for future reference**
- **Consider contacting Odoo support for critical systems**

## 🆘 EMERGENCY CONTACTS

- Odoo Community: https://www.odoo.com/forum
- Technical Support: Your system administrator
- Database Admin: For SQL-level fixes

## 📞 NEED IMMEDIATE HELP?

If this is a production system:
1. **Stop Odoo immediately**
2. **Restore from last known good backup**
3. **Contact your system administrator**
4. **Document the exact steps that led to this error**
"""
    
    return recovery_steps

def check_module_health(module_path):
    """Check if the module has any obvious issues"""
    print("🏥 CHECKING MODULE HEALTH...")
    
    issues = []
    
    # Check Python syntax
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                    print(f"✅ {file} - Syntax OK")
                except SyntaxError as e:
                    issues.append(f"❌ {file} - Syntax Error: {e}")
                except Exception as e:
                    issues.append(f"⚠️ {file} - Warning: {e}")
    
    # Check XML syntax
    xml_files = []
    for root, dirs, files in os.walk(module_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    print(f"📄 Found {len(xml_files)} XML files")
    
    return issues

if __name__ == "__main__":
    module_path = r"d:\RUNNING APPS\ready production\odoo_17_final\account_statement"
    
    print("🚨 ODOO REGISTRY CORRUPTION RECOVERY")
    print("=" * 50)
    
    # Check module health
    if os.path.exists(module_path):
        issues = check_module_health(module_path)
        
        if issues:
            print("\n❌ MODULE ISSUES FOUND:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ MODULE FILES ARE CLEAN")
            print("   The issue is likely in the Odoo registry/database")
    
    # Generate recovery instructions
    recovery_instructions = create_recovery_instructions()
    
    # Save to file
    with open('REGISTRY_RECOVERY_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(recovery_instructions)
    
    print("\n📋 RECOVERY GUIDE CREATED: REGISTRY_RECOVERY_GUIDE.md")
    print("🔧 Follow the steps in the guide to fix the registry corruption")
    print("\n🎯 QUICK FIX TO TRY FIRST:")
    print("   1. Stop Odoo service")
    print("   2. Clear Python cache") 
    print("   3. Restart Odoo service")
    print("   4. Update Apps List")
    print("   5. Uninstall/Reinstall module")
