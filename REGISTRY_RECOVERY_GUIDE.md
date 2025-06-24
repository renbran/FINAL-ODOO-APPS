
# 🚨 ODOO REGISTRY CORRUPTION - RECOVERY GUIDE

## 🔍 PROBLEM ANALYSIS
The error `KeyError: 'ir.http'` indicates that the Odoo registry is corrupted. 
This typically happens when:
- Module installation fails mid-way
- Database becomes inconsistent
- Python import errors during module loading
- Circular dependencies in custom modules

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

#### Option B: Update Module List
```bash
# Connect to your Odoo database and run:
# Go to Apps -> Update Apps List
# Then try to uninstall/reinstall the problematic module
```

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

#### Option B: Full Registry Reset
```sql
-- DANGER: This clears ALL custom modules
-- Only use if you have backups
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE state IN ('to install', 'to upgrade', 'to remove');
```

### STEP 3: ADVANCED RECOVERY

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
