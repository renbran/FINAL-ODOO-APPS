# Odoo 17 NOT NULL Constraint Error Fix

## Problem Description

You're encountering these database schema errors when starting Odoo 17:

```
ERROR: Table 'hr_employee': unable to set NOT NULL on column 'agent_id'
ERROR: Table 'hr_employee': unable to set NOT NULL on column 'labour_card_number'  
ERROR: Table 'hr_employee': unable to set NOT NULL on column 'salary_card_number'
ERROR: Table 'res_bank': unable to set NOT NULL on column 'routing_code'
```

## Root Cause

These errors occur because:

1. The `uae_wps_report` module adds required fields (`required=True`) to existing models
2. Your database has existing records with NULL values in these fields
3. PostgreSQL cannot add NOT NULL constraints to columns that contain NULL values
4. This commonly happens during module updates or when installing modules on existing databases

## Solution Options

### Option 1: Cloud/Server SQL Script (Recommended for Cloudpepper)

If your Odoo/PostgreSQL is hosted on a Linux server (like Cloudpepper), use this method:

1. **Upload the SQL script to your server** (e.g., `/var/odoo/os-us/database_migration_fix_cloudpepper.sql`).
2. **SSH into your server**:
   ```bash
   ssh root@139.84.163.11
   ```
3. **Run the script using psql**:
   ```bash
   psql -h 139.84.163.11 -U root -d os-us -f /var/odoo/os-us/database_migration_fix_cloudpepper.sql
   ```
   (Enter your password when prompted)

### Option 1b: Using PowerShell (Windows, if you have direct DB access)

```powershell
.\fix_database.ps1 -DatabaseName "os-us" -Username "root"
```

### Option 2: Manual Database Fix

If you prefer to run the fixes manually:

#### Step 1: Connect to your PostgreSQL database
```bash
psql -U postgres -d os-us```

#### Step 2: Fix res_bank.routing_code field
```sql
-- Update NULL routing codes with padded bank ID
UPDATE res_bank 
SET routing_code = LPAD(CAST(id AS TEXT), 9, '0')
WHERE routing_code IS NULL OR routing_code = '';
```

#### Step 3: Fix hr_employee fields
```sql
-- Create default bank if none exists
INSERT INTO res_bank (name, routing_code, create_date, write_date, create_uid, write_uid)
SELECT 'Default Bank', '000000000', NOW(), NOW(), 1, 1
WHERE NOT EXISTS (SELECT 1 FROM res_bank LIMIT 1);

-- Get default bank ID
SELECT id FROM res_bank ORDER BY id LIMIT 1;

-- Update agent_id (replace 1 with actual bank ID from above query)
UPDATE hr_employee 
SET agent_id = 1 
WHERE agent_id IS NULL;

-- Update labour_card_number with padded employee ID
UPDATE hr_employee 
SET labour_card_number = LPAD(CAST(id AS TEXT), 14, '0')
WHERE labour_card_number IS NULL OR labour_card_number = '';

-- Update salary_card_number with padded employee ID  
UPDATE hr_employee 
SET salary_card_number = LPAD(CAST(id AS TEXT), 16, '0')
WHERE salary_card_number IS NULL OR salary_card_number = '';
```

#### Step 4: Verify the fixes
```sql
-- Check for remaining NULL values
SELECT COUNT(*) FROM hr_employee 
WHERE agent_id IS NULL 
   OR labour_card_number IS NULL 
   OR salary_card_number IS NULL;

SELECT COUNT(*) FROM res_bank 
WHERE routing_code IS NULL OR routing_code = '';
```

### Option 3: Module Configuration Approach

If you want to make the fields optional instead:

1. **Modify the module** (not recommended for UAE WPS compliance):
   ```python
   # In uae_wps_report/models/hr_employee.py
   labour_card_number = fields.Char(
       string="Employee Card Number", size=14, required=False,  # Changed to False
       help="Labour Card Number Of Employee")
   ```

2. **Update the module**:
   ```bash
   ./odoo-bin -d your_database -u uae_wps_report
   ```

## Files Provided

1. **`database_migration_fix.sql`** - Complete SQL script to fix all issues
2. **`fix_database.ps1`** - PowerShell helper script for Windows users  
3. **`database_migration_fix.py`** - Python script alternative (requires psycopg2)

## Step-by-Step Instructions

### For Windows Users:

1. **Open PowerShell as Administrator**
2. **Navigate to your Odoo directory**:
   ```powershell
   cd "d:\RUNNING APPS\ready production\odoo_17_final"
   ```
3. **Run the fix script**:
   ```powershell
   .\fix_database.ps1 -DatabaseName "os-us" -Username "root"
   ```
4. **Follow the prompts** and confirm when asked
5. **Start Odoo** once the script completes successfully

### For Linux/Mac Users:

1. **Navigate to your Odoo directory**:
   ```bash
   cd "/path/to/your/odoo/directory"
   ```
2. **Run the SQL script directly**:
   ```bash
   psql -U your_user -d your_database -f database_migration_fix.sql
   ```
3. **Start Odoo** once the script completes successfully

### For Linux/Cloudpepper Users:

1. **Upload the PowerShell script to your server** (e.g., `/var/odoo/os-us/fix_database.ps1`).
2. **SSH into your server**:
   ```bash
   ssh root@139.84.163.11
   ```
3. **Run the script using PowerShell Core (pwsh)**:
   ```bash
   pwsh /var/odoo/os-us/fix_database.ps1 -DatabaseName "os-us" -Username "root"
   ```
   (If you do not have PowerShell Core, use the SQL method above.)

## What the Fix Does

The migration script:

1. **Creates a default bank** if none exists for the `agent_id` field
2. **Updates NULL `agent_id`** values to point to the default bank
3. **Generates `labour_card_number`** using zero-padded employee IDs (14 digits)
4. **Generates `salary_card_number`** using zero-padded employee IDs (16 digits)  
5. **Generates `routing_code`** using zero-padded bank IDs (9 digits)
6. **Verifies** that all NULL values have been resolved

## After Running the Fix

1. **Start Odoo normally** - the NOT NULL constraint errors should be resolved
2. **Check the employee records** in the HR module to ensure data looks correct
3. **Update the generated values** with real data as needed for compliance

## Important Notes

- ⚠️ **Backup your database** before running any migration scripts
- 🔒 The generated values are **placeholder data** - update them with real values for production use
- 📋 For UAE WPS compliance, ensure all employee and bank data is accurate
- 🔄 This fix is **one-time only** - future employees/banks should have proper data entry

## Troubleshooting

### If you still see errors after the fix:

1. **Check if all NULL values were updated**:
   ```sql
   SELECT id, name, agent_id, labour_card_number, salary_card_number 
   FROM hr_employee 
   WHERE agent_id IS NULL OR labour_card_number IS NULL OR salary_card_number IS NULL;
   ```

2. **Restart PostgreSQL** service:
   ```bash
   sudo systemctl restart postgresql
   # or on Windows: restart the PostgreSQL service
   ```

3. **Update the module** after database fix:
   ```bash
   ./odoo-bin -d your_database -u uae_wps_report --stop-after-init
   ```

4. **Check Odoo logs** for other potential issues:
   ```bash
   tail -f /var/log/odoo/odoo.log
   ```

## Support

If you continue to experience issues:

1. Check that all required modules are installed and up to date
2. Verify your PostgreSQL version is compatible with Odoo 17
3. Review the complete Odoo error logs for additional context
4. Consider updating all modules: `./odoo-bin -d your_database -u all`

---

**This solution specifically addresses the UAE WPS Report module requirements while maintaining data integrity and Odoo 17 compatibility.**
