# OSUS Invoice Report

This module provides custom invoice and bill reports for OSUS PROPERTIES in Odoo 17.

## Production Checklist

1. **Ensure all files are present:**
   - `__manifest__.py` and `__init__.py` in the module root
   - All referenced XML files in the `report/` directory
2. **No references to missing files:**
   - The module does not reference any non-existent files (e.g., `custom_report/report/report_template.xml`)
3. **Deployment steps:**
   - Update the module list in Odoo
   - Upgrade the module from the Apps menu
   - If you encounter a file not found error, clear the Odoo cache and restart the Odoo server

## Troubleshooting
- If you see a `FileNotFoundError` for a file not present in this module, check for old references in the database or Odoo cache.
- Remove or fix any such references, then restart the server and upgrade the module again.

## Support
For further assistance, contact OSUS PROPERTIES IT or your Odoo administrator.
