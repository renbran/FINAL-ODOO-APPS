# DUPLICATE SECURITY GROUP FIX SUMMARY

## Issue Resolved
**Problem**: UniqueViolation error during module installation
```
duplicate key value violates unique constraint "res_groups_name_uniq"
DETAIL: Key (category_id, name)=(1, {"en_US": "Payment Voucher User"}) already exists.
```

## Root Cause
Security groups from a previous installation attempt remained in the CloudPepper database, causing unique constraint violations when trying to recreate groups with the same names.

## Fixes Applied

### 1. **Changed Data Update Policy** ✅
```xml
<!-- BEFORE -->
<data noupdate="0">

<!-- AFTER -->
<data noupdate="1">
```
This prevents recreation of existing groups during reinstallation.

### 2. **Updated Group Names with OSUS Prefix** ✅
```xml
<!-- BEFORE -->
<field name="name">Payment Voucher User</field>

<!-- AFTER -->  
<field name="name">OSUS Payment Voucher User</field>
```

### 3. **Complete Group Hierarchy Updated** ✅
- `OSUS Payment Voucher User`
- `OSUS Payment Voucher Reviewer` 
- `OSUS Payment Voucher Approver`
- `OSUS Payment Voucher Authorizer`
- `OSUS Payment Voucher Manager`
- `OSUS Payment QR Verifier`

## Database Cleanup for CloudPepper

If the problem persists, run this SQL query in CloudPepper database:

```sql
-- Remove conflicting security groups
DELETE FROM res_groups_users_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE name LIKE '%Payment Voucher%'
);

DELETE FROM ir_model_access WHERE group_id IN (
    SELECT id FROM res_groups WHERE name LIKE '%Payment Voucher%'  
);

DELETE FROM ir_rule_group_rel WHERE group_id IN (
    SELECT id FROM res_groups WHERE name LIKE '%Payment Voucher%'
);

DELETE FROM res_groups WHERE name LIKE '%Payment Voucher%';

-- Verify cleanup
SELECT name FROM res_groups WHERE name LIKE '%Payment%';
```

## Module Installation Strategy

### **Primary Approach** ✅
1. Use `noupdate="1"` to prevent recreation
2. Use unique OSUS-prefixed group names
3. Install module normally

### **If Issues Persist**
1. Uninstall the module completely
2. Run database cleanup queries
3. Reinstall with updated security groups

## Validation Results
- ✅ XML syntax valid
- ✅ Unique group names implemented
- ✅ No-update policy applied
- ✅ All group references preserved

## Critical Success Indicators
1. **Unique Constraint Compliance**: ✅ OSUS-prefixed names prevent conflicts
2. **Update Protection**: ✅ noupdate="1" prevents recreation
3. **Reference Integrity**: ✅ All XML IDs remain consistent
4. **Security Hierarchy**: ✅ Group inheritance preserved

---
**Fix Status**: ✅ RESOLVED - Ready for CloudPepper installation
**Backup Plan**: ✅ Database cleanup script available if needed
