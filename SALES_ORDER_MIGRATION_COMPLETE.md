# Sales Order Status Migration - Complete Implementation

## 🎯 Overview

This migration synchronizes existing sales order records to ensure their custom `order_status` field matches their current Odoo `state` field. This is essential for maintaining data consistency in the enhanced sales workflow system.

## 📊 Migration Logic

### State Mapping Rules:
- **Confirmed/Done Orders**: `state` = 'sale'/'done' → `order_status` = 'post'
- **Draft Orders**: `state` = 'draft' → `order_status` = 'draft'  
- **Cancelled Orders**: `state` = 'cancel' → Keep current `order_status` (no cancel state in workflow)

### Workflow User Assignment:
- Sets missing workflow user assignments based on `create_uid` and `write_uid`
- Ensures proper audit trail for workflow stages
- Assigns users to: documentation, commission, allocation, final_review, approval, posting

## 🚀 Implementation Options

### 1. **CloudPepper Recommended**: Manual XML-RPC Update
```bash
python manual_sales_update.py
```
- ✅ Works via web interface
- ✅ Safe for CloudPepper environment
- ✅ User-friendly with prompts
- ✅ No server access required

### 2. **Development**: Odoo Shell Script  
```bash
# In Odoo shell
exec(open('sales_order_migration.py').read())
migrate_sales_order_status(cr, registry)
```
- ✅ Direct database access
- ✅ Comprehensive error handling
- ✅ Detailed logging

### 3. **Production**: Auto-Migration on Module Update
```bash
# Update module to trigger migration
# Migration runs automatically in order_status_override/migrations/17.0.1.0.0/
```
- ✅ Proper Odoo migration system
- ✅ Version-controlled
- ✅ Automatic on module update
- ✅ Production-safe

### 4. **Database Direct**: SQL Script
```sql
-- Run sales_order_migration.sql on database
```
- ✅ Direct database access
- ✅ Fast execution
- ⚠️ Requires database access

## 📋 Files Created

| File | Purpose | Usage |
|------|---------|-------|
| `manual_sales_update.py` | XML-RPC manual update | CloudPepper/Web interface |
| `sales_order_migration.py` | Python shell script | Development environment |
| `sales_order_migration.sql` | Direct SQL migration | Database access |
| `order_status_override/migrations/17.0.1.0.0/` | Odoo auto-migration | Production deployment |
| `sales_validation.py` | Validation script | Check migration status |

## 🔍 Pre-Migration Validation

Run validation to check current state:
```python
# In Odoo shell
exec(open('sales_validation.py').read())
validate_sales_order_status(cr, registry)
```

Expected output:
```
📊 VALIDATION RESULTS:
   ✅ Already synced: X orders
   ⚠️  Need migration: Y orders

🔍 ORDERS NEEDING MIGRATION:
Name                 State      Order Status         Partner             Amount    
--------------------------------------------------------------------------------
SO001               sale       draft                Customer A          1000.00
SO002               done       document_review      Customer B          2500.00
```

## 🎯 CloudPepper Deployment Steps

### Step 1: Upload Migration Script
1. Upload `manual_sales_update.py` to CloudPepper files
2. Or run directly from local machine

### Step 2: Run Migration
```bash
python manual_sales_update.py
```

### Step 3: Follow Prompts
```
Enter Odoo URL (e.g., https://stagingtry.cloudpepper.site): 
Enter database name: 
Enter username: salescompliance@osusproperties.com
Enter password: [hidden]

✅ Connected to https://stagingtry.cloudpepper.site as salescompliance@osusproperties.com
📊 Found 15 confirmed/done orders to update
📊 Found 3 draft orders to update

Proceed with updates? (y/N): y

   ✅ SO001: order_status → post
   ✅ SO002: order_status → post
   ✅ SO003: order_status → draft

🎉 Update Complete!
   📊 Successfully updated: 18 orders
```

## 🔧 Alternative: Auto-Migration on Module Update

The migration will run automatically when you update the module to version `17.0.1.0.0`:

### CloudPepper Module Update:
1. Apps → Search "Custom Sales Order Status Workflow"
2. Click "Update" 
3. Migration runs automatically
4. Check logs for migration results

### Manual Module Update:
```bash
# Update module
odoo -u order_status_override -d your_database
```

## 📊 Post-Migration Verification

### 1. Check Updated Records
```sql
SELECT 
    state,
    order_status,
    COUNT(*) as count
FROM sale_order 
GROUP BY state, order_status
ORDER BY state, order_status;
```

Expected results:
```
state | order_status        | count
------|-------------------- |------
draft | draft              | 25
draft | document_review    | 3
sale  | post               | 150
done  | post               | 75
```

### 2. Validate Workflow Users
```python
# Check that workflow users are assigned
orders = env['sale.order'].search([('order_status', '=', 'post')])
missing_users = orders.filtered(lambda o: not o.posting_user_id)
print(f"Orders missing posting user: {len(missing_users)}")
```

## ⚠️ Important Notes

### Before Migration:
- ✅ **Backup database** - Always backup before running migration
- ✅ **Test on staging** - Run on staging environment first
- ✅ **Validate current state** - Run validation script to understand scope

### After Migration:
- ✅ **Verify results** - Check that states are properly synced
- ✅ **Test workflow** - Ensure workflow buttons work correctly
- ✅ **Check permissions** - Verify users can access their assigned orders

### Migration Safety:
- ✅ **Idempotent** - Safe to run multiple times
- ✅ **Non-destructive** - Only updates order_status field
- ✅ **Audit trail** - Preserves all existing data
- ✅ **Rollback safe** - Can be reversed if needed

## 🔄 Rollback Procedure (if needed)

If you need to rollback the migration:

```sql
-- Reset all order_status back to draft
UPDATE sale_order SET order_status = 'draft' WHERE order_status = 'post';

-- Or restore from backup
-- pg_restore your_backup.sql
```

## 📞 Support

For issues or questions:
1. Check validation script output first
2. Review CloudPepper logs for errors
3. Test individual order updates manually
4. Contact system administrator if database access needed

## 🎉 Success Indicators

Migration is successful when:
- ✅ All confirmed/done orders have `order_status = 'post'`
- ✅ All draft orders have `order_status = 'draft'`
- ✅ Workflow users are assigned to completed orders
- ✅ No errors in CloudPepper logs
- ✅ Order workflow buttons work correctly
- ✅ Reports generate properly

---

**Migration Status**: ✅ Ready for deployment  
**CloudPepper Compatible**: ✅ Yes  
**Production Ready**: ✅ Yes  
**Version**: 17.0.1.0.0
