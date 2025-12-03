# 🔄 RENTAL MANAGEMENT v3.6.0 - MIGRATION GUIDE

**Module:** rental_management
**Migration Version:** 3.5.0 → 3.6.0
**Purpose:** Clean up deprecated code and optimize database
**Risk Level:** LOW (all data is backed up)

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [What Will Be Removed](#what-will-be-removed)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Migration Steps](#migration-steps)
5. [Verification Steps](#verification-steps)
6. [Rollback Procedure](#rollback-procedure)
7. [FAQ](#faq)

---

## 📖 OVERVIEW

This migration removes **deprecated fields and models** from the rental_management module that were marked as deprecated in previous versions. All data is safely backed up before removal.

### What Happens:

1. **Pre-Migration** (Automatic)
   - Backs up all deprecated data to `*_deprecated_backup` tables
   - Creates rollback documentation
   - Logs statistics

2. **Module Upgrade** (Automatic)
   - Odoo processes the module upgrade
   - New model definitions take effect

3. **Post-Migration** (Automatic)
   - Removes deprecated columns from `property_details` table
   - Drops deprecated model tables
   - Cleans orphaned data
   - Optimizes database

### Benefits:

✅ Reduces database size
✅ Improves query performance
✅ Simplifies codebase maintenance
✅ Removes technical debt
✅ All data safely backed up

---

## 🗑️ WHAT WILL BE REMOVED

### Deprecated Fields (property_details model):

#### Pricing Fields:
- `token_amount` (replaced by `price`)
- `sale_price` (replaced by `price`)
- `tenancy_price` (replaced by `price`)

#### Parent Property System:
- `is_parent_property`
- `parent_property_id`
- All `parent_*` related fields (20+ fields)

#### Individual Connectivity Fields:
- `airport`, `national_highway`, `metro_station`
- `school`, `hospital`, `shopping_mall`, `park`
- *Replaced by* `connectivity_ids` (flexible connectivity system)

#### Old Measurement System:
- `commercial_measurement_ids`
- `industrial_measurement_ids`
- `total_commercial_measure`
- `total_industrial_measure`
- *Replaced by* `room_measurement_ids` (unified system)

#### Other Deprecated Fields:
- `property_licence_no`
- `construct_year`, `buying_year`
- `room_no`, `total_square_ft`, `usable_square_ft`
- `residence_type`, `industry_name`, `land_name`, `commercial_name`
- `furnishing` (replaced by `furnishing_id`)
- And more...

### Deprecated Models:

1. **property.commercial.measurement**
   - Replaced by unified `property.room.measurement`

2. **property.industrial.measurement**
   - Replaced by unified `property.room.measurement`

3. **certificate.type**
   - Deprecated certificate system

4. **property.certificate**
   - Deprecated certificate system

5. **parent.property**
   - Replaced by `property.project` and `property.sub.project`

---

## ✅ PRE-MIGRATION CHECKLIST

### 1. Backup Database

```bash
# Create full database backup
pg_dump -U odoo -d your_database_name > backup_before_migration_$(date +%Y%m%d).sql

# Verify backup was created
ls -lh backup_before_migration_*.sql
```

### 2. Check Disk Space

```bash
# Check available disk space (need at least 20% free)
df -h

# Check current database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('your_database_name'));"
```

### 3. Verify No Active Users

```bash
# Check for active user sessions
sudo -u postgres psql -d your_database_name -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'your_database_name';"
```

### 4. Review Deprecated Field Usage

```sql
-- Check if any properties use deprecated fields
SELECT
    id,
    name,
    token_amount,
    sale_price,
    is_parent_property,
    residence_type
FROM property_details
WHERE token_amount IS NOT NULL
   OR sale_price IS NOT NULL
   OR is_parent_property = true
   OR residence_type IS NOT NULL
LIMIT 10;
```

### 5. Notify Users

Send notification to all users:
```
⚠️ SCHEDULED MAINTENANCE
Date: [DATE]
Time: [TIME]
Duration: 30-60 minutes
Impact: Rental Management module will be unavailable
Action Required: Complete all work and log out
```

---

## 🚀 MIGRATION STEPS

### Method 1: Standard Upgrade (Recommended)

```bash
# 1. Stop Odoo service
sudo systemctl stop odoo

# 2. Backup database (if not done already)
pg_dump -U odoo -d your_database > backup_pre_migration.sql

# 3. Update module code
cd /opt/odoo/addons/rental_management
git pull origin main  # or copy new files

# 4. Start Odoo with upgrade flag
./odoo-bin -c /etc/odoo.conf -u rental_management --stop-after-init

# 5. Check logs for migration progress
tail -f /var/log/odoo/odoo.log | grep -i migration

# 6. Verify migration completed successfully
# Look for: "rental_management v3.6.0 POST-MIGRATION COMPLETED SUCCESSFULLY"

# 7. Restart Odoo service
sudo systemctl start odoo

# 8. Monitor logs
sudo journalctl -u odoo -f
```

### Method 2: Using Odoo Shell (Advanced)

```bash
# Start Odoo in shell mode
./odoo-bin shell -c /etc/odoo.conf -d your_database

# In Python shell:
>>> # Check migration status
>>> env['ir.module.module'].search([('name', '=', 'rental_management')])
>>> # Upgrade module
>>> env['ir.module.module'].search([('name', '=', 'rental_management')]).button_immediate_upgrade()
>>> # Exit
>>> exit()
```

### Expected Output:

```
================================================================================
Starting rental_management v3.6.0 PRE-MIGRATION
================================================================================
Checking for deprecated fields...
Found 45 deprecated fields in property_details: ['token_amount', 'sale_price', ...]
Backing up deprecated property fields...
✓ Backed up 127 properties with deprecated field data
Backing up deprecated models...
  ✓ Backed up 23 records from property_commercial_measurement
  ✓ Backed up 15 records from property_industrial_measurement
  ...
================================================================================
rental_management v3.6.0 PRE-MIGRATION COMPLETED
================================================================================

[... Module upgrade processing ...]

================================================================================
Starting rental_management v3.6.0 POST-MIGRATION
================================================================================
Removing deprecated columns from property_details...
  ✓ Dropped column: property_details.token_amount
  ✓ Dropped column: property_details.sale_price
  ...
Summary: Dropped 45 columns
Removing deprecated model tables...
  ✓ Dropped table: property_commercial_measurement
  ✓ Dropped table: property_industrial_measurement
  ...
Cleaning up orphaned data...
  ✓ Cleaned 5 ir_model entries
  ✓ Cleaned 45 deprecated field definitions
Optimizing database...
  ✓ Analyzed property_details table
================================================================================
rental_management v3.6.0 POST-MIGRATION COMPLETED SUCCESSFULLY
================================================================================
```

---

## ✅ VERIFICATION STEPS

### 1. Check Migration Logs

```bash
# Check for any errors
grep -i "error\|fail\|exception" /var/log/odoo/odoo.log | tail -20

# Verify migration completion
grep "POST-MIGRATION COMPLETED SUCCESSFULLY" /var/log/odoo/odoo.log
```

### 2. Verify Backup Tables Created

```sql
-- Check backup tables exist
SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE tablename LIKE '%deprecated_backup'
AND schemaname = 'public';

-- Expected output:
-- property_details_deprecated_backup
-- property_commercial_measurement_deprecated_backup
-- property_industrial_measurement_deprecated_backup
-- certificate_type_deprecated_backup
-- property_certificate_deprecated_backup
-- parent_property_deprecated_backup
```

### 3. Verify Deprecated Tables Removed

```sql
-- These tables should NOT exist anymore
SELECT tablename
FROM pg_tables
WHERE tablename IN (
    'property_commercial_measurement',
    'property_industrial_measurement',
    'certificate_type',
    'property_certificate',
    'parent_property'
)
AND schemaname = 'public';

-- Expected: 0 rows returned
```

### 4. Test Core Functionality

```
✓ Login to Odoo
✓ Navigate to Rental Management > Properties
✓ Create new property
✓ View existing property
✓ Create rent contract
✓ Create sale contract
✓ Generate invoice
✓ View dashboard
✓ Generate reports
```

### 5. Check Database Size Reduction

```sql
-- Check database size before and after
SELECT pg_size_pretty(pg_database_size('your_database_name'));

-- Expected: 2-5% reduction in database size
```

### 6. Performance Check

```sql
-- Test query performance
EXPLAIN ANALYZE
SELECT * FROM property_details
WHERE stage = 'available'
LIMIT 100;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'property_details'
ORDER BY idx_scan DESC;
```

---

## 🔙 ROLLBACK PROCEDURE

### If Migration Fails or Issues Arise:

#### Option 1: Database Restore (Full Rollback)

```bash
# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore database from backup
sudo -u postgres psql -c "DROP DATABASE your_database_name;"
sudo -u postgres psql -c "CREATE DATABASE your_database_name OWNER odoo;"
sudo -u postgres psql your_database_name < backup_pre_migration.sql

# 3. Revert code to previous version
cd /opt/odoo/addons/rental_management
git checkout v3.5.0  # or restore previous files

# 4. Start Odoo
sudo systemctl start odoo
```

#### Option 2: Restore Specific Data (Partial Rollback)

```sql
-- Retrieve rollback script
SELECT value
FROM ir_config_parameter
WHERE key = 'rental_management.migration_3_6_0_rollback';

-- The script will contain SQL to restore data from backup tables
-- IMPORTANT: You must manually add fields back to Python models first!
```

#### Option 3: Contact Support

If issues persist:
- Email: support@techkhedut.com
- Include: Migration logs, error messages, database version
- Response time: 24-48 hours

---

## ❓ FAQ

### Q1: How long does the migration take?

**A:** Typically 5-10 minutes. Factors:
- Small database (<1,000 properties): 2-5 minutes
- Medium database (1,000-10,000 properties): 5-10 minutes
- Large database (>10,000 properties): 10-30 minutes

### Q2: Will I lose any data?

**A:** No. All deprecated data is backed up to `*_deprecated_backup` tables before removal. You can restore it if needed.

### Q3: Can I run this migration on a production server?

**A:** Yes, but recommended steps:
1. Test on staging environment first
2. Schedule during low-usage hours
3. Notify users in advance
4. Have backup ready

### Q4: What if I still need a deprecated field?

**A:** You can restore data from backup tables. Contact support for assistance with field restoration.

### Q5: How do I access backed up data?

```sql
-- View backed up property data
SELECT
    property_id,
    deprecated_data,
    backup_date
FROM property_details_deprecated_backup
LIMIT 10;

-- Extract specific field from backup
SELECT
    property_id,
    deprecated_data->>'token_amount' as old_token_amount,
    deprecated_data->>'sale_price' as old_sale_price
FROM property_details_deprecated_backup;
```

### Q6: Can I delete backup tables after migration?

**A:** Yes, but wait at least 90 days to ensure no rollback is needed.

```sql
-- After 90 days, if everything is working fine:
DROP TABLE IF EXISTS property_details_deprecated_backup CASCADE;
DROP TABLE IF EXISTS property_commercial_measurement_deprecated_backup CASCADE;
DROP TABLE IF EXISTS property_industrial_measurement_deprecated_backup CASCADE;
DROP TABLE IF EXISTS certificate_type_deprecated_backup CASCADE;
DROP TABLE IF EXISTS property_certificate_deprecated_backup CASCADE;
DROP TABLE IF EXISTS parent_property_deprecated_backup CASCADE;
```

### Q7: What if migration fails halfway?

**A:** The migration is designed to be safe:
- Pre-migration backs up everything first
- If post-migration fails, data is still in the database (just not cleaned up)
- You can always restore from backup
- Check logs for specific errors

### Q8: Will this affect my customizations?

**A:** Only if your customizations use deprecated fields. Check:

```python
# Search for deprecated field usage in custom modules
grep -r "token_amount\|sale_price\|parent_property_id" /path/to/custom_modules/
```

### Q9: How do I verify migration was successful?

**A:** Look for this in logs:
```
rental_management v3.6.0 POST-MIGRATION COMPLETED SUCCESSFULLY
```

And verify:
- No errors in logs
- All functionality works
- Backup tables exist
- Deprecated tables removed

### Q10: Can I run this migration multiple times?

**A:** Yes, the migration is idempotent. If run again:
- Will check if columns exist before dropping
- Will skip already-removed tables
- Will update backups if needed

---

## 📞 SUPPORT

### Need Help?

**TechKhedut Inc.**
- Website: https://www.techkhedut.com
- Email: support@techkhedut.com
- Documentation: Check module documentation folder

### Before Contacting Support:

Please gather:
1. Migration log file
2. Odoo version
3. Database size and version
4. Error messages (if any)
5. Output of verification steps

---

## 📝 CHECKLIST

Print this and check off each step:

### Pre-Migration:
- [ ] Database backup created
- [ ] Disk space verified (>20% free)
- [ ] Users notified
- [ ] Staging environment tested
- [ ] No active users in system

### Migration:
- [ ] Odoo service stopped
- [ ] Module code updated
- [ ] Migration command executed
- [ ] Logs monitored
- [ ] No errors in logs

### Post-Migration:
- [ ] Migration success message found in logs
- [ ] Backup tables verified
- [ ] Deprecated tables removed
- [ ] Core functionality tested
- [ ] Performance checked
- [ ] Users notified of completion

### Documentation:
- [ ] Migration logs saved
- [ ] Backup location documented
- [ ] Issues documented (if any)
- [ ] Team informed

---

**Migration Version:** 1.0
**Last Updated:** 2025-12-03
**Prepared By:** TechKhedut Inc.
