# Custom Fields Cleanup - Manual Instructions

Since you don't have direct database access, here are several alternative approaches:

## Option 1: Odoo Shell Script (Recommended)

If you have SSH access to your server:

1. **SSH into your server**:
   ```bash
   ssh your_user@your_server
   ```

2. **Navigate to Odoo directory**:
   ```bash
   cd /path/to/your/odoo
   ```

3. **Open Odoo shell**:
   ```bash
   python3 odoo-bin shell -d your_database_name --no-http
   ```

4. **Run the cleanup script** (copy and paste):
   ```python
   # Custom Fields Cleanup Script
   print("=== Starting Custom Fields Cleanup ===")
   
   cr = env.cr
   
   # Fix sale_order_type_id references
   cr.execute("""
       UPDATE account_move 
       SET sale_order_type_id = NULL 
       WHERE sale_order_type_id IS NOT NULL 
       AND NOT EXISTS (SELECT 1 FROM sale_order_type WHERE id = account_move.sale_order_type_id);
   """)
   print(f"Fixed {cr.rowcount} sale_order_type_id references")
   
   # Fix project references
   cr.execute("""
       UPDATE account_move 
       SET project = NULL 
       WHERE project IS NOT NULL 
       AND NOT EXISTS (SELECT 1 FROM product_template WHERE id = account_move.project);
   """)
   print(f"Fixed {cr.rowcount} project references")
   
   # Fix unit references
   cr.execute("""
       UPDATE account_move 
       SET unit = NULL 
       WHERE unit IS NOT NULL 
       AND NOT EXISTS (SELECT 1 FROM product_product WHERE id = account_move.unit);
   """)
   print(f"Fixed {cr.rowcount} unit references")
   
   # Fix buyer references
   cr.execute("""
       UPDATE account_move 
       SET buyer = NULL 
       WHERE buyer IS NOT NULL 
       AND NOT EXISTS (SELECT 1 FROM res_partner WHERE id = account_move.buyer);
   """)
   print(f"Fixed {cr.rowcount} buyer references")
   
   # Remove duplicate field definitions
   for field_name in ['sale_order_type_id', 'project', 'unit', 'buyer']:
       duplicates = env['ir.model.fields'].search([('model', '=', 'account.move'), ('name', '=', field_name)])
       if len(duplicates) > 1:
           duplicates[1:].unlink()
           print(f"Removed {len(duplicates)-1} duplicate {field_name} definitions")
   
   cr.commit()
   print("✅ Cleanup completed!")
   ```

## Option 2: Install Cleanup Module

1. **Copy the cleanup module** to your addons directory:
   ```bash
   cp -r custom_fields_cleanup_module /path/to/your/addons/
   ```

2. **Update apps list** in Odoo:
   - Go to Apps > Update Apps List

3. **Install the module**:
   - Search for "Custom Fields Cleanup"
   - Click Install

4. **Run the cleanup**:
   - Go to Settings > Technical > Server Actions
   - Find "Clean Custom Fields"
   - Click "Run"

## Option 3: Modify Your Custom Fields Module

**Temporarily disable problematic fields** by editing your custom_fields module:

1. **Edit** `custom_fields/models/account_move.py`:
   ```python
   # Comment out or add ondelete='set null' to problematic fields
   
   sale_order_type_id = fields.Many2one(
       'sale.order.type',
       string='Sales Order Type',
       tracking=True,
       ondelete='set null',  # Add this
   )
   
   buyer = fields.Many2one(
       'res.partner',
       string='Buyer Name',
       tracking=True,
       ondelete='set null',  # Add this
   )
   
   project = fields.Many2one(
       'product.template',
       string='Project Name',
       tracking=True,
       ondelete='set null',  # Add this
   )
   
   unit = fields.Many2one(
       'product.product',
       string='Unit',
       tracking=True,
       ondelete='set null',  # Add this
   )
   ```

2. **Upgrade the module**:
   ```bash
   python3 odoo-bin -d your_database -u custom_fields
   ```

## Option 4: Contact Your Hosting Provider

If you're using a managed Odoo hosting service:

1. **Send them the SQL script** (`custom_fields_cleanup.sql`)
2. **Ask them to run it** on your database
3. **Explain the issue**: "_unknown object error due to orphaned foreign key references"

## Option 5: Database Manager Interface

If your Odoo has the Database Manager enabled:

1. **Go to** `/web/database/manager`
2. **Login** with master password
3. **Use the SQL interface** (if available) to run the cleanup queries

## Quick Test Commands

After running any cleanup, test with these SQL queries:

```sql
-- Check for remaining orphaned references
SELECT COUNT(*) FROM account_move WHERE sale_order_type_id IS NOT NULL 
AND NOT EXISTS (SELECT 1 FROM sale_order_type WHERE id = account_move.sale_order_type_id);

-- Check for duplicate fields
SELECT name, COUNT(*) FROM ir_model_fields 
WHERE model = 'account.move' AND name IN ('sale_order_type_id', 'project', 'unit', 'buyer') 
GROUP BY name HAVING COUNT(*) > 1;
```

## Emergency Fix

If nothing else works, **temporarily comment out the problematic custom fields**:

1. **Edit** your custom fields files
2. **Comment out** the field definitions causing issues
3. **Restart Odoo** to get it working
4. **Then implement proper cleanup**

The key is to break the reference to non-existent records that are causing the `_unknown` object error.
