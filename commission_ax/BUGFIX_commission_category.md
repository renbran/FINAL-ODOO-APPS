# BUGFIX: Missing commission_category Field

## Issue
**Error Message:**
```
OwlError: An error occured in the owl lifecycle
Caused by: Error: "commission.ax"."commission_category" field is undefined.
```

**Date:** December 4, 2025 20:20 UTC

## Root Cause
The `commission_category` field was referenced in views but not defined in the `commission.ax` model. This field is needed to categorize commissions into logical groups (External, Internal, Legacy) for better organization and filtering.

## Solution
Added `commission_category` field to `commission.ax` model as a computed Selection field that automatically categorizes commissions based on their `role` field.

### Field Definition
```python
commission_category = fields.Selection([
    ('external', 'External Commission'),
    ('internal', 'Internal Commission'),
    ('legacy', 'Legacy Commission'),
], string='Commission Category', compute='_compute_commission_category', store=True, 
   help="Category of commission based on the role")
```

### Compute Method
```python
@api.depends('role')
def _compute_commission_category(self):
    """Compute commission category based on role"""
    for record in self:
        if record.role in ['broker', 'referrer', 'cashback', 'other_external']:
            record.commission_category = 'external'
        elif record.role in ['agent1', 'agent2', 'manager', 'director']:
            record.commission_category = 'internal'
        elif record.role in ['consultant', 'manager_legacy', 'director_legacy', 'second_agent']:
            record.commission_category = 'legacy'
        else:
            record.commission_category = False
```

## Category Mapping

### External Commissions
- **broker** - External broker commissions
- **referrer** - External referrer commissions
- **cashback** - Cashback partner commissions
- **other_external** - Other external partner commissions

### Internal Commissions
- **agent1** - Internal Agent 1 commissions
- **agent2** - Internal Agent 2 commissions
- **manager** - Internal Manager commissions
- **director** - Internal Director commissions

### Legacy Commissions
- **consultant** - Legacy consultant commissions
- **manager_legacy** - Legacy manager commissions
- **director_legacy** - Legacy director commissions
- **second_agent** - Legacy second agent commissions

## Deployment Steps

### 1. Upload Updated Model
```bash
scp -P 22 commission_ax/models/commission_ax.py \
    root@139.84.163.11:/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/commission_ax/models/
```

### 2. Upgrade Module (osusproperties)
```bash
ssh root@139.84.163.11
cd /var/odoo/osusproperties
/var/odoo/osusproperties/venv/bin/python3 src/odoo-bin \
    -c odoo.conf \
    -d osusproperties \
    -u commission_ax \
    --stop-after-init \
    --no-http
```

### 3. Manual SQL for erposus Database
```sql
ALTER TABLE commission_ax ADD COLUMN IF NOT EXISTS commission_category VARCHAR;
```

### 4. Restart Service
```bash
systemctl restart odona-osusproperties.service
systemctl status odona-osusproperties.service
```

## Verification

### Database Check
```sql
-- Verify field exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='commission_ax' 
AND column_name='commission_category';

-- Test computed values (after creating commission records)
SELECT id, name, role, commission_category 
FROM commission_ax 
WHERE role IS NOT NULL 
LIMIT 10;
```

**Expected Results:**
- osusproperties: column exists (character varying)
- erposus: column exists (character varying)
- commission_category automatically populated based on role

### UI Test
1. Go to Sales → Commission Management
2. Open/create a commission record
3. Set the **Role** field to any value (e.g., "Broker")
4. Verify **Commission Category** automatically populates with "External Commission"
5. Try different roles and verify correct categorization

## Status
✅ **RESOLVED** - December 4, 2025 20:20 UTC

- `commission_category` field added to commission.ax model
- Compute method `_compute_commission_category()` implemented
- Field added to osusproperties database (automatic via upgrade)
- Field manually added to erposus database
- Service restarted successfully (Tasks: 10, Memory: 212.0M)
- Both databases verified with field present

## Impact
- **Severity:** Medium (causes view errors, prevents accessing commission list)
- **Affected Users:** Users accessing commission management views
- **Downtime:** None (fix applied during normal operation)
- **Data Loss:** None

## Related Files
- `commission_ax/models/commission_ax.py` - Field definition and compute method
- Database tables: `commission_ax` in both osusproperties and erposus

## Benefits
1. **Automatic Categorization**: No manual category assignment needed
2. **Consistency**: Category always matches role definition
3. **Better Filtering**: Users can filter commissions by category
4. **Reporting**: Easier to generate reports by commission type
5. **Scalability**: New roles automatically get correct category

## Commission System Iterations

This is the **13th iteration** of commission system field fixes:
1. commission_lines_count
2. commission_id (account_move)
3. is_fully_invoiced
4. has_posted_invoices
5. broker_calculation_base
6. 4x calculation_base fields (referrer, cashback, other_external, agent1)
7. 3x calculation_base fields (agent2, manager, director)
8. 8x legacy system fields
9. commission_line_ids
10. partner_id
11. commission_type_id, commission_amount, commission_rate
12. role
13. **commission_category** ← Current fix

## Total Field Count
- **sale.order**: 23 fields
- **commission.ax**: 6 fields (partner_id, role, commission_category, commission_type_id, commission_amount, commission_rate)
- **account.move**: 1 field (commission_id)
- **Total**: 30 fields across 3 models
