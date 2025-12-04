# BUGFIX: Missing commission_type_id Field in commission.line Model

## Issue
**Error Message:**
```
OwlError: An error occured in the owl lifecycle
Caused by: Error: "commission.line"."commission_type_id" field is undefined.
```

**Date:** December 4, 2025 20:27 UTC

## Root Cause
The `commission_type_id` field was referenced in views but not properly defined in the `commission.line` model (from the `commission_lines` module). The field existed in the database as a foreign key to `commission.type` table, but was missing from the Python model definition.

## Database Context
The `commission.line` table already had:
- `commission_type_id` column (INTEGER) with foreign key constraint
- Foreign key: `FOREIGN KEY (commission_type_id) REFERENCES commission_type(id) ON DELETE SET NULL`

## Solution
Added `commission_type_id` as a Many2one field in the `commission.line` model:

```python
commission_type_id = fields.Many2one(
    'commission.type',
    string='Commission Type Reference',
    help='Reference to commission type configuration'
)
```

### Why Many2one (not Char)?
Initially attempted to add as a computed Char field (similar to commission.ax), but database constraint revealed it must be a Many2one field referencing `commission.type` model.

**Error encountered with Char field:**
```
psycopg2.errors.DatatypeMismatch: foreign key constraint "commission_line_commission_type_id_fkey" 
cannot be implemented
DETAIL: Key columns "commission_type_id" of the referencing table and "id" of the referenced table 
are of incompatible types: character varying and integer.
```

## Commission Type Reference Data
The `commission.type` model contains commission type configurations:

| ID | Name |
|----|------|
| 1 | External Commission |
| 2 | Internal Commission |
| 3 | Referral Commission |
| 4 | Bonus Commission |
| 11 | Director Internal Commission |
| 12 | Agent Internal Commission |
| 13 | Manager Internal Commission |
| 14 | Consultant Internal Commission |
| 15 | Salesperson Internal Commission |
| 16 | Second Agent Internal Commission |

## Module Context
- **Module:** `commission_lines` (separate from `commission_ax`)
- **Model:** `commission.line`
- **File:** `/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_lines/models/commission_line.py`
- **Lines:** 437 lines total
- **State:** Installed on osusproperties, uninstalled on erposus

## Related Fields in commission.line
The model has both:
1. **commission_type** - Selection field for role type (consultant, manager, director, broker, etc.)
2. **commission_type_id** - Many2one field referencing commission.type configuration

These serve different purposes:
- `commission_type`: Identifies the role/position
- `commission_type_id`: Links to commission type configuration with rates and rules

## Deployment Steps

### 1. Download Original File
```bash
scp -P 22 root@139.84.163.11:/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_lines/models/commission_line.py \
    "d:/RUNNING APPS/FINAL-ODOO-APPS/.claude/"
```

### 2. Add Field Definition
Added after `commission_type` field around line 110.

### 3. Upload Fixed File
```bash
scp -P 22 "d:/RUNNING APPS/FINAL-ODOO-APPS/.claude/commission_line.py" \
    root@139.84.163.11:/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_lines/models/
```

### 4. Upgrade Module (osusproperties only)
```bash
ssh root@139.84.163.11
cd /var/odoo/osusproperties
/var/odoo/osusproperties/venv/bin/python3 src/odoo-bin \
    -c odoo.conf \
    -d osusproperties \
    -u commission_lines \
    --stop-after-init \
    --no-http
```

**Note:** Module not installed on erposus database, no action needed there.

### 5. Restart Service
```bash
systemctl restart odona-osusproperties.service
systemctl status odona-osusproperties.service
```

## Verification

### Database Check
```sql
-- Verify field and constraint
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='commission_line' 
AND column_name='commission_type_id';

-- Expected: commission_type_id | integer

-- Verify foreign key constraint
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid='commission_line'::regclass 
AND conname LIKE '%commission_type_id%';

-- Expected: FOREIGN KEY (commission_type_id) REFERENCES commission_type(id)
```

### UI Test
1. Navigate to commission lines view (if available in UI)
2. Open/create a commission line record
3. Verify **Commission Type Reference** field displays without errors
4. Verify field shows list of commission types from `commission.type` model

## Status
✅ **RESOLVED** - December 4, 2025 20:27 UTC

- `commission_type_id` field added as Many2one to commission.line model
- Module upgraded on osusproperties database
- Service restarted successfully (Tasks: 10, Memory: 203.8M)
- Field verified as INTEGER in database
- Foreign key constraint maintained

## Impact
- **Severity:** High (causes view errors, prevents accessing commission line lists)
- **Affected Users:** Users accessing commission lines via views referencing commission_type_id
- **Downtime:** None (fix applied during normal operation)
- **Data Loss:** None (database field already existed with data intact)

## Key Learning
When adding missing fields:
1. Always check database structure first (`information_schema.columns`)
2. Check for existing constraints (`pg_constraint`)
3. Match Python field type to database column type and constraints
4. Many2one for INTEGER with foreign key, not Char or computed field

## Related Files
- `commission_lines/models/commission_line.py` - Field definition added
- Database: `commission_line` table in osusproperties
- Related model: `commission.type` (referenced table)

## Commission System Field Count Update

This is the **14th iteration** of commission system field fixes:
1. commission_lines_count (sale.order)
2. commission_id (account.move)
3. is_fully_invoiced (sale.order)
4. has_posted_invoices (sale.order)
5. broker_calculation_base (sale.order)
6. 4x calculation_base fields (sale.order)
7. 3x calculation_base fields (sale.order)
8. 8x legacy system fields (sale.order)
9. commission_line_ids (sale.order)
10. partner_id (commission.ax)
11. commission_type_id, commission_amount, commission_rate (commission.ax)
12. role (commission.ax)
13. commission_category (commission.ax)
14. **commission_type_id (commission.line)** ← Current fix

## Total Field Count Across All Models
- **sale.order**: 23 fields
- **commission.ax**: 6 fields
- **commission.line**: 1 field (commission_type_id - was in DB, now in model)
- **account.move**: 1 field
- **Total**: 31 fields across 4 models
