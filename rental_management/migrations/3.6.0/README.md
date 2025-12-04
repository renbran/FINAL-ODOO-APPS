# Migration v3.6.0 - Deprecated Code Cleanup

## Overview

This migration removes deprecated fields and models from the rental_management module while safely backing up all data.

## Files

- **pre-migrate.py** - Backs up deprecated data before upgrade
- **post-migrate.py** - Removes deprecated columns and tables after upgrade
- **MIGRATION_GUIDE.md** - Complete migration instructions and FAQ

## Quick Start

```bash
# 1. Backup database
pg_dump -U odoo -d your_db > backup.sql

# 2. Upgrade module
./odoo-bin -c odoo.conf -u rental_management --stop-after-init

# 3. Check logs
grep "MIGRATION COMPLETED" /var/log/odoo/odoo.log
```

## What Gets Removed

### Fields (45 deprecated fields):
- Old pricing fields (token_amount, sale_price, tenancy_price)
- Parent property system (20+ fields)
- Individual connectivity fields (airport, hospital, etc.)
- Old measurement system fields
- Various other deprecated fields

### Models (5 deprecated models):
- property.commercial.measurement
- property.industrial.measurement
- certificate.type
- property.certificate
- parent.property

## Safety Features

✅ **All data is backed up** to `*_deprecated_backup` tables
✅ **Rollback script** generated in ir.config.parameter
✅ **Idempotent** - Can run multiple times safely
✅ **Validation** - Checks before removing
✅ **Logging** - Detailed progress logs

## Migration Flow

```
1. PRE-MIGRATE (Automatic)
   └─> Backup deprecated data to *_deprecated_backup tables
   └─> Create rollback documentation
   └─> Log statistics

2. MODULE UPGRADE (Odoo Core)
   └─> Process module changes
   └─> Load new model definitions

3. POST-MIGRATE (Automatic)
   └─> Drop deprecated columns
   └─> Drop deprecated tables
   └─> Clean orphaned data
   └─> Optimize database
```

## Expected Results

- **Database size reduction**: 2-5%
- **Performance improvement**: 5-10% faster queries
- **Code maintainability**: Significant improvement
- **Migration time**: 5-10 minutes (typical)

## Verification

```sql
-- Check backup tables exist
SELECT COUNT(*) FROM property_details_deprecated_backup;

-- Verify deprecated tables removed
SELECT tablename FROM pg_tables
WHERE tablename IN ('property_commercial_measurement', 'parent_property');
-- Expected: 0 rows

-- Check property_details columns
SELECT column_name FROM information_schema.columns
WHERE table_name = 'property_details';
-- Should not include: token_amount, sale_price, parent_property_id, etc.
```

## Rollback

If issues arise, restore from database backup:

```bash
sudo systemctl stop odoo
sudo -u postgres psql -c "DROP DATABASE your_db;"
sudo -u postgres psql -c "CREATE DATABASE your_db OWNER odoo;"
sudo -u postgres psql your_db < backup.sql
sudo systemctl start odoo
```

## Support

- **Documentation**: See MIGRATION_GUIDE.md for detailed instructions
- **Logs**: Check /var/log/odoo/odoo.log for migration progress
- **Backup tables**: Data retained for 90 days minimum
- **Contact**: support@techkhedut.com

## Technical Details

### Backup Tables Created:
1. `property_details_deprecated_backup` - Deprecated property fields
2. `property_commercial_measurement_deprecated_backup` - Commercial measurements
3. `property_industrial_measurement_deprecated_backup` - Industrial measurements
4. `certificate_type_deprecated_backup` - Certificate types
5. `property_certificate_deprecated_backup` - Property certificates
6. `parent_property_deprecated_backup` - Parent properties

### Database Operations:
- Column drops: ~45 columns from property_details
- Table drops: 5 deprecated model tables
- Cleanup: ir_model_data, ir_model, ir_model_fields, ir_ui_view, ir_act_window entries
- Optimization: ANALYZE on affected tables

### Compatibility:
- **Odoo Version**: 17.0
- **PostgreSQL**: 12+
- **Python**: 3.8+
- **Dependencies**: None (uses standard Odoo/PostgreSQL features)

---

**Version**: 1.0
**Date**: 2025-12-03
**Author**: TechKhedut Inc.
