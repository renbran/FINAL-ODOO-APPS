# Custom Fields '_unknown' Object Error Fix

## Problem Description

You're encountering this Odoo server error:

```
AttributeError: '_unknown' object has no attribute 'id'
```

This error occurs in the `convert_to_read` method when Odoo tries to access the `id` attribute of a relational field that references a record that doesn't exist or has been corrupted.

## Root Cause Analysis

After analyzing your custom fields, I found several issues:

### 1. Duplicate Field Definitions
Multiple modules are defining the same fields on `account.move`:
- `custom_fields` module adds: `buyer`, `project`, `unit`, `sale_order_type_id`
- `le_sale_type` module adds: `sale_order_type_id`

### 2. Orphaned References
The database contains records in `account_move` that reference:
- Non-existent `sale.order.type` records
- Non-existent `product.template` records (project field)
- Non-existent `product.product` records (unit field)
- Non-existent `res.partner` records (buyer field)

### 3. Database Inconsistencies
When records are deleted from referenced tables, the foreign key references in `account_move` become orphaned, causing the `_unknown` object error.

## Solution

I've created a comprehensive cleanup script that fixes all these issues.

### Quick Fix (Recommended)

1. **Run the PowerShell script** (Windows):
   ```powershell
   .\fix_custom_fields.ps1 -DatabaseName "your_database_name" -Username "your_db_user"
   ```

2. **Or run the SQL script directly**:
   ```bash
   psql -h localhost -U your_user -d your_database -f custom_fields_cleanup.sql
   ```

### What the Fix Does

1. **Removes Orphaned References**: Sets all foreign key fields to NULL where they reference non-existent records
2. **Cleans Duplicate Fields**: Removes duplicate field definitions in `ir_model_fields`
3. **Updates Statistics**: Refreshes database statistics for optimal performance
4. **Cleans ir_model_data**: Removes orphaned entries in the data registry

### Files Created

- `custom_fields_cleanup.sql` - Direct SQL script to fix the issues
- `fix_custom_fields.ps1` - PowerShell wrapper script for easier execution
- `custom_fields_cleanup.py` - Python script alternative (requires psycopg2)

## Manual Steps (Alternative)

If you prefer to run the fixes manually:

### 1. Connect to PostgreSQL
```bash
psql -h localhost -U your_user -d your_database
```

### 2. Fix Orphaned sale_order_type_id References
```sql
UPDATE account_move 
SET sale_order_type_id = NULL 
WHERE sale_order_type_id IS NOT NULL 
AND sale_order_type_id NOT IN (SELECT id FROM sale_order_type);
```

### 3. Fix Orphaned project References
```sql
UPDATE account_move 
SET project = NULL 
WHERE project IS NOT NULL 
AND project NOT IN (SELECT id FROM product_template);
```

### 4. Fix Orphaned unit References
```sql
UPDATE account_move 
SET unit = NULL 
WHERE unit IS NOT NULL 
AND unit NOT IN (SELECT id FROM product_product);
```

### 5. Fix Orphaned buyer References
```sql
UPDATE account_move 
SET buyer = NULL 
WHERE buyer IS NOT NULL 
AND buyer NOT IN (SELECT id FROM res_partner);
```

## Prevention

To prevent this issue in the future:

### 1. Avoid Duplicate Field Definitions
- Don't define the same field in multiple modules
- Use `_inherit` properly without conflicting field names
- Consider merging custom fields into a single module

### 2. Implement Proper Constraints
Add proper foreign key constraints and cascade rules:

```python
# In your model definition
sale_order_type_id = fields.Many2one(
    'sale.order.type', 
    string="Sale Order Type", 
    ondelete='set null'  # This prevents orphaned references
)
```

### 3. Use Database Cleanup Module
Install and regularly run the `database_cleanup` module to identify orphaned records.

## Verification

After running the fix:

1. **Check for remaining orphaned references**:
   ```sql
   SELECT COUNT(*) FROM account_move 
   WHERE sale_order_type_id IS NOT NULL 
   AND sale_order_type_id NOT IN (SELECT id FROM sale_order_type);
   ```

2. **Restart Odoo** and test the functionality that was failing

3. **Monitor logs** for any remaining `_unknown` object errors

## Custom Fields Module Issues

Your `custom_fields` module has some structural issues:

### Duplicate Field Names
The module defines both:
- `buyer` and `buyer_id`
- `project` and `project_id`  
- `unit` and `unit_id`

### Recommendation
Clean up the `custom_fields/models/account_move.py` file to use consistent field names and avoid duplication.

## Contact

If you continue to experience issues after running this fix, the problem might be with:
1. Other custom modules with similar issues
2. Database corruption requiring deeper investigation
3. Odoo version compatibility issues

The `_unknown` object error should be resolved after running this cleanup script.
