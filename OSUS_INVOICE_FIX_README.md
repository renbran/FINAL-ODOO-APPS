# OSUS Invoice Report Module - External ID Fix

## Problem Description

The error `ValueError: External ID not found in the system: osus_invoice_report.action_report_osus_invoice` occurs when the Odoo system cannot find the report action defined in the `osus_invoice_report` module. This typically happens when:

1. The module data has not been properly loaded into the database
2. The module needs to be upgraded after code changes
3. There was an error during module installation
4. The database cache needs to be refreshed

## Error Details

```
ValueError: External ID not found in the system: osus_invoice_report.action_report_osus_invoice
```

This error occurs in the following methods:
- `action_print_custom_invoice()` - Line 17
- `action_print_custom_bill()` - Line 24  
- `action_print_custom_receipt()` - Line 29

## Solutions Applied

### 1. Immediate Fix - Error Handling with Fallback

The `models/custom_invoice.py` file has been updated to include proper error handling. If the custom report actions are not found, the system will fall back to using the standard Odoo invoice report.

**Changes made:**
- Added try-catch blocks around `env.ref()` calls
- Added fallback to `account.account_invoices` (standard invoice report)
- Added logging to track when fallbacks are used

### 2. Module Upgrade Scripts

Three scripts have been created to help upgrade the module:

#### Windows PowerShell Script
**File:** `fix_osus_invoice_report.ps1`
- Run as Administrator
- Automatically detects Odoo installation
- Stops/starts Odoo service if needed
- Performs module upgrade

**Usage:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\fix_osus_invoice_report.ps1
```

#### Linux Shell Script
**File:** `fix_osus_invoice_report.sh`
- Works on Linux/Unix systems
- Automatically detects Odoo binary
- Handles process management
- Performs module upgrade

**Usage:**
```bash
chmod +x fix_osus_invoice_report.sh
./fix_osus_invoice_report.sh
```

#### Python Script
**File:** `upgrade_osus_invoice_module.py`
- Can be run in Odoo environment
- Provides detailed diagnostics
- Includes manual instructions

### 3. Manual Upgrade Instructions

If the automated scripts don't work, follow these manual steps:

#### Option A: Command Line Upgrade
```bash
# Stop Odoo first
# Then run:
python3 odoo-bin -d your_database_name -u osus_invoice_report --stop-after-init
```

#### Option B: Force Reinstall
```bash
# Uninstall
python3 odoo-bin -d your_database_name --uninstall osus_invoice_report --stop-after-init

# Reinstall
python3 odoo-bin -d your_database_name -i osus_invoice_report --stop-after-init
```

#### Option C: Odoo Shell
```bash
python3 odoo-bin shell -d your_database_name
```

Then in the shell:
```python
>>> module = env['ir.module.module'].search([('name', '=', 'osus_invoice_report')])
>>> module.button_upgrade()
>>> env.cr.commit()
>>> exit()
```

#### Option D: Web Interface
1. Go to Apps menu in Odoo
2. Remove "Apps" filter to show all modules
3. Search for "osus_invoice_report"
4. Click "Upgrade" button

## Verification Steps

After applying the fix:

1. **Check Module Status:**
   - Go to Apps → Search "osus_invoice_report"
   - Verify status shows "Installed"

2. **Test Report Actions:**
   - Go to Accounting → Invoices
   - Open any invoice
   - Try clicking the custom print buttons
   - Should work without RPC_ERROR

3. **Check Logs:**
   - Look for warning messages about fallback reports
   - If you see warnings, it means the external IDs are still missing but the fallback is working

## External IDs that Should Exist

After successful upgrade, these external IDs should be available:
- `osus_invoice_report.action_report_osus_invoice`
- `osus_invoice_report.action_report_osus_bill`
- `osus_invoice_report.report_osus_invoice_document`
- `osus_invoice_report.report_osus_bill_document`

## Troubleshooting

### If reports still don't work:

1. **Check module dependencies:**
   ```python
   # In Odoo shell
   >>> module = env['ir.module.module'].search([('name', '=', 'osus_invoice_report')])
   >>> print(module.dependencies_id.mapped('name'))
   ```

2. **Verify XML files are syntactically correct:**
   - Check `report/report_action.xml`
   - Check `report/bill_report_action.xml`
   - Look for XML syntax errors

3. **Check for conflicts with other modules:**
   - Look for modules that might override the same reports
   - Check for duplicate external IDs

4. **Database integrity:**
   ```sql
   -- Check if external IDs exist in database
   SELECT * FROM ir_model_data WHERE module = 'osus_invoice_report' AND name LIKE 'action_report%';
   ```

## Files Modified

- `models/custom_invoice.py` - Added error handling and fallback logic
- `fix_osus_invoice_report.ps1` - PowerShell upgrade script (NEW)
- `fix_osus_invoice_report.sh` - Shell upgrade script (NEW)  
- `upgrade_osus_invoice_module.py` - Python diagnostic script (UPDATED)

## Prevention

To prevent this issue in the future:
1. Always upgrade modules after making changes to XML data files
2. Test in a development environment before production
3. Keep backups of working module states
4. Monitor Odoo logs for deprecation warnings

## Support

If the issue persists after trying all solutions:
1. Check Odoo server logs for detailed error messages
2. Verify all dependencies are installed
3. Consider recreating the module from scratch if data corruption is suspected
4. Contact Odoo support or development team for advanced troubleshooting
