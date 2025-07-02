# Testing and Installation Guide

## Step 1: Install the Custom Fields Cleanup Module

1. **Copy the cleanup module** to your Odoo addons directory:
   ```bash
   # If you have SSH access
   cp -r custom_fields_cleanup_module /path/to/your/odoo/addons/
   ```

2. **Update Apps List** in Odoo:
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Search for "Custom Fields Cleanup"

3. **Install the module**:
   - Click **Install** on the Custom Fields Cleanup module

## Step 2: Run the Cleanup

1. **Access the cleanup wizard**:
   - Go to **Settings** > **Technical** > **Server Actions**
   - Find "Clean Custom Fields" action
   - Click **Run**

   OR

   - Go to **Settings** > **General Settings**
   - Look for "Custom Fields Cleanup" in the menu

2. **Execute the cleanup**:
   - Click **Start Cleanup** button
   - Wait for the process to complete
   - Review the log messages

## Step 3: Test the osus_invoice_report Module

After running the cleanup:

1. **Try to install osus_invoice_report**:
   - Go to **Apps** menu
   - Search for "OSUS Invoice Report"
   - Click **Install**

2. **If it was already installed, try upgrading**:
   - Find the module in Apps
   - Click **Upgrade**

## Step 4: Verify Everything Works

1. **Test account moves**:
   - Go to **Accounting** > **Invoices**
   - Try to open an existing invoice
   - Check if the '_unknown' object error is gone

2. **Test reports**:
   - Open an invoice
   - Try to print using OSUS reports
   - Verify reports generate without errors

## Step 5: Alternative Quick Fix (If Module Installation Fails)

If you can't install the cleanup module, run this in Odoo shell:

```python
# Quick cleanup script
print("=== Quick Cleanup ===")

# Fix orphaned sale_order_type_id references
env.cr.execute("UPDATE account_move SET sale_order_type_id = NULL WHERE sale_order_type_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sale_order_type WHERE id = account_move.sale_order_type_id);")
print(f"Fixed {env.cr.rowcount} sale_order_type_id references")

# Fix orphaned project references
env.cr.execute("UPDATE account_move SET project = NULL WHERE project IS NOT NULL AND NOT EXISTS (SELECT 1 FROM product_template WHERE id = account_move.project);")
print(f"Fixed {env.cr.rowcount} project references")

# Fix orphaned unit references
env.cr.execute("UPDATE account_move SET unit = NULL WHERE unit IS NOT NULL AND NOT EXISTS (SELECT 1 FROM product_product WHERE id = account_move.unit);")
print(f"Fixed {env.cr.rowcount} unit references")

# Fix orphaned buyer references
env.cr.execute("UPDATE account_move SET buyer = NULL WHERE buyer IS NOT NULL AND NOT EXISTS (SELECT 1 FROM res_partner WHERE id = account_move.buyer);")
print(f"Fixed {env.cr.rowcount} buyer references")

# Create missing paper format
try:
    existing_xmlid = env['ir.model.data'].search([('module', '=', 'osus_invoice_report'), ('name', '=', 'paperformat_osus_invoice')])
    if not existing_xmlid:
        new_format = env['report.paperformat'].create({
            'name': 'OSUS Invoice Format',
            'format': 'A4',
            'orientation': 'Portrait',
            'margin_top': 50,
            'margin_bottom': 50,
            'margin_left': 10,
            'margin_right': 10,
            'header_line': False,
            'header_spacing': 40,
            'dpi': 90,
        })
        env['ir.model.data'].create({
            'module': 'osus_invoice_report',
            'name': 'paperformat_osus_invoice',
            'model': 'report.paperformat',
            'res_id': new_format.id,
            'noupdate': False,
        })
        print("Created missing paper format")
except:
    print("Paper format creation skipped (may already exist)")

env.cr.commit()
print("✅ Quick cleanup completed!")
```

## What to Expect

After running the cleanup, you should see:

✅ **No more '_unknown' object errors** when opening account moves
✅ **osus_invoice_report module installs successfully**
✅ **OSUS reports work properly**
✅ **All orphaned references cleaned up**

## If Issues Persist

If you still encounter problems:

1. **Check the cleanup log** for specific errors
2. **Restart Odoo** after running cleanup
3. **Check module dependencies** are all installed
4. **Review the error logs** for other issues

Let me know the results after running the cleanup!
