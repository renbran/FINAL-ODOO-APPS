# Account Vacuum Fix Module

## Overview
This module fixes the autovacuum error that occurs with the `account.tax.report` model in Odoo 17:
```
UserError: You can't delete a report that has variants.
```

This error prevents the automatic cleanup of transient records and can cause performance issues over time.

## Problem Description
The error occurs when Odoo's autovacuum process tries to clean up old transient records from the `account.tax.report` model, but encounters reports that have dependent variant records that cannot be automatically deleted.

## Solution
This module provides:

1. **Automated Fix**: Safely removes orphaned report variants and problematic transient records
2. **Manual Control**: Allows administrators to run fixes manually through the UI
3. **Safe Process**: Temporarily disables autovacuum during fixes to prevent conflicts
4. **Comprehensive Logging**: Detailed logs of all fix operations

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Account Vacuum Fix" module

## Usage

### Method 1: UI-Based Fix (Recommended)
1. Go to **Accounting → Configuration → Fix Vacuum Issues**
2. Click "Fix Vacuum Issues" button
3. Wait for the process to complete
4. Review the fix log for details

### Method 2: Server Action (Quick Fix)
1. Go to **Settings → Technical → Server Actions**
2. Find "Quick Vacuum Fix" action
3. Click "Run" to execute immediately

### Method 3: Programmatic Fix
```python
# From Odoo shell or custom code
fix_wizard = env['account.vacuum.fix'].create({})
fix_wizard.action_fix_vacuum_issues()
```

## What the Fix Does

1. **Temporarily Disables Autovacuum**: Prevents conflicts during the fix process
2. **Cleans Report Variants**: Removes orphaned or inactive tax report variants
3. **Removes Problematic Records**: Safely deletes transient records that cause vacuum issues
4. **Re-enables Autovacuum**: Restores normal cleanup operations
5. **Provides Detailed Logging**: Records all actions taken during the fix

## Safety Notes

- ✅ **Safe to run**: Only removes orphaned/inactive records
- ✅ **Non-destructive**: Does not affect active tax reports or important data
- ✅ **Reversible**: Re-enables autovacuum after fixes
- ✅ **Logged**: All actions are logged for audit purposes

## Troubleshooting

### If the fix doesn't work:
1. Check the fix log for specific error messages
2. Verify that the user has accounting manager permissions
3. Try running the fix multiple times (some issues may require multiple passes)

### If autovacuum is still disabled after fix:
```python
# Re-enable autovacuum manually
cron = env['ir.cron'].search([('model_id.model', '=', 'ir.autovacuum')])
cron.active = True
```

## Maintenance

This module can be:
- **Kept installed**: For periodic maintenance and monitoring
- **Uninstalled**: After the fix is successfully applied (if no recurring issues)

### Periodic Maintenance
The module includes an optional cron job (disabled by default) that can run weekly vacuum fixes. To enable:
1. Go to **Settings → Technical → Scheduled Actions**
2. Find "Periodic Account Vacuum Fix"
3. Set it to Active

## Technical Details

### Models Extended
- `account.tax.report`: Patched to handle variant dependencies during unlink operations
- `account.vacuum.fix`: New transient model for fix operations

### Dependencies
- `base`: Core Odoo functionality
- `account`: Accounting module with tax reports

### Files Structure
```
account_vacuum_fix/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── account_vacuum_fix.py
├── views/
│   └── account_vacuum_fix_views.xml
├── data/
│   └── fix_actions.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

## Support

For issues or questions:
1. Check the fix logs for detailed error information
2. Verify all dependencies are properly installed
3. Ensure user has appropriate accounting permissions
4. Contact the OSUS Development Team for advanced support

## License
This module is licensed under LGPL-3.
