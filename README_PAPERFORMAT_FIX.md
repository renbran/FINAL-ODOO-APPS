# Fix for osus_invoice_report Paper Format Error

## Problem Description

You're getting this error when trying to install/upgrade the `osus_invoice_report` module:

```
ValueError: External ID not found in the system: osus_invoice_report.paperformat_osus_invoice
```

This happens because the report actions are trying to reference a paper format that doesn't exist in the database.

## Solution Options

### Option 1: Quick Fix - Use Base Paper Format (Recommended)

I've already updated the `osus_invoice_report` module to use the base paper format instead. This should work immediately:

1. **The module files have been updated** to use `base.paperformat_euro` instead of the missing paper format
2. **Try to install/upgrade** the module again - it should work now

### Option 2: Create the Missing Paper Format via Odoo Shell

If you have SSH access to your server:

1. **SSH into your server** and navigate to Odoo directory
2. **Open Odoo shell**:
   ```bash
   python3 odoo-bin shell -d your_database_name --no-http
   ```
3. **Run this script** (copy and paste):
   ```python
   # Create missing paper format
   existing_xmlid = env['ir.model.data'].search([
       ('module', '=', 'osus_invoice_report'),
       ('name', '=', 'paperformat_osus_invoice'),
       ('model', '=', 'report.paperformat')
   ])
   
   if not existing_xmlid:
       # Create new paper format
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
       
       # Create external ID
       env['ir.model.data'].create({
           'module': 'osus_invoice_report',
           'name': 'paperformat_osus_invoice',
           'model': 'report.paperformat',
           'res_id': new_format.id,
           'noupdate': False,
       })
       
       env.cr.commit()
       print("✅ Created missing paper format")
   else:
       print("✅ Paper format already exists")
   ```

### Option 3: Use the Enhanced Cleanup Module

The `custom_fields_cleanup_module` now includes a fix for this paper format issue:

1. **Install the cleanup module** if you haven't already
2. **Run the cleanup wizard** - it will fix both the custom fields and paper format issues

### Option 4: Restore Original Paper Format Reference

If you want to keep the original paper format reference:

1. **Revert the changes** I made to `osus_invoice_report/views/account_move_views.xml`
2. **Use Option 2** to create the missing paper format
3. **Then install/upgrade** the module

## What I Changed

I modified these files:

1. **`osus_invoice_report/views/account_move_views.xml`**:
   - Changed all `paperformat_id` references from `osus_invoice_report.paperformat_osus_invoice` to `base.paperformat_euro`
   - This uses the standard Odoo Euro paper format instead

2. **`osus_invoice_report/__manifest__.py`**:
   - Moved `data/report_paperformat.xml` to load before the views
   - This ensures paper format is created before reports try to reference it

3. **`custom_fields_cleanup_module/models/cleanup_wizard.py`**:
   - Added function to create missing paper format if needed

## Verification

After applying the fix:

1. **Try to install/upgrade** the `osus_invoice_report` module
2. **Check that reports work** by going to an invoice and testing the OSUS reports
3. **Verify paper format** in Settings > Technical > Reporting > Paper Format

## If Issues Persist

If you still get errors:

1. **Check module dependencies**: Make sure all required modules are installed
2. **Check file permissions**: Ensure Odoo can read the module files
3. **Check logs**: Look for other error messages in the Odoo logs
4. **Try safe mode**: Install the module in safe mode to bypass some checks

The main issue was that the module was trying to reference a paper format that didn't exist in the database. By using the base paper format, this reference issue is resolved.
