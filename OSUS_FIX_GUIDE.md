# OSUS Invoice Report Installation Fix - Complete Guide

This guide provides multiple solutions to fix the `osus_invoice_report` module installation issues, specifically the "External ID not found in the system: osus_invoice_report.paperformat_osus_invoice" error.

## Available Solutions

### 🚀 Quick Fix (Recommended)

**Option 1: Comprehensive PowerShell Script**
```powershell
.\fix_osus_comprehensive.ps1
```

This script handles everything automatically:
- Fixes the paper format external ID issue
- Installs/upgrades the module
- Provides detailed progress feedback

**Option 2: Paper Format Only (If you just need to fix the external ID)**
```powershell
.\fix_osus_comprehensive.ps1 -OnlyPaperFormatFix
```

### 🔧 Manual Odoo Shell Methods

**Method 1: Direct Paper Format Fix**
```bash
# Windows (PowerShell)
& "C:\Program Files\Odoo 17.0\server\odoo-bin" shell -d odoo17_final --addons-path="." < fix_paperformat_direct.py

# Linux/Mac
odoo-bin shell -d your_database --addons-path=. < fix_paperformat_direct.py
```

**Method 2: Complete Module Fix**
```bash
# Windows (PowerShell)
& "C:\Program Files\Odoo 17.0\server\odoo-bin" shell -d odoo17_final --addons-path="." < fix_osus_module.py

# Linux/Mac
odoo-bin shell -d your_database --addons-path=. < fix_osus_module.py
```

### 🖥️ GUI Method (Using Cleanup Module)

1. Install the cleanup module:
   ```powershell
   .\install_cleanup_module.ps1
   ```

2. In Odoo:
   - Go to **Settings** > **Technical** > **Actions** > **Server Actions**
   - Find "Clean Database Fields and References"
   - Click **Run**

3. Install the OSUS module:
   - Go to **Apps** > **Update Apps List**
   - Search for "OSUS Invoice Report"
   - Click **Install**

### 📁 Available Files

| File | Purpose |
|------|---------|
| `fix_osus_comprehensive.ps1` | Complete PowerShell solution (recommended) |
| `fix_paperformat_direct.py` | Direct paper format fix via Odoo shell |
| `fix_osus_module.py` | Complete module fix via Odoo shell |
| `install_cleanup_module.ps1` | Install cleanup module for GUI approach |
| `custom_fields_cleanup_module/` | Odoo module for GUI-based cleanup |

## Troubleshooting

### Common Issues

**1. "Odoo binary not found"**
- Update the `-OdooPath` parameter in PowerShell scripts
- Example: `.\fix_osus_comprehensive.ps1 -OdooPath "C:\Odoo\odoo-bin"`

**2. "Database not found"**
- Update the `-Database` parameter
- Example: `.\fix_osus_comprehensive.ps1 -Database "my_database"`

**3. "Module still fails to install"**
- Try running the paper format fix first:
  ```powershell
  .\fix_osus_comprehensive.ps1 -OnlyPaperFormatFix
  ```
- Then try manual installation via Odoo UI

**4. "Config file not found"**
- The scripts will work without config file
- Or specify correct path: `.\fix_osus_comprehensive.ps1 -ConfigPath "C:\path\to\odoo.conf"`

### Verification Steps

After running any fix:

1. **Check if paper format exists:**
   ```python
   # In Odoo shell
   env.ref('osus_invoice_report.paperformat_osus_invoice')
   ```

2. **Check module status:**
   ```python
   # In Odoo shell
   module = env['ir.module.module'].search([('name', '=', 'osus_invoice_report')])
   print(f"Module state: {module.state}")
   ```

3. **Test invoice report:**
   - Create a test invoice
   - Try to print it
   - Verify the formatting is correct

## Script Parameters

### PowerShell Script Parameters

```powershell
.\fix_osus_comprehensive.ps1 [parameters]
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `-Database` | "odoo17_final" | Odoo database name |
| `-OdooPath` | "C:\Program Files\Odoo 17.0\server\odoo-bin" | Path to Odoo binary |
| `-ConfigPath` | "C:\Program Files\Odoo 17.0\server\odoo.conf" | Path to Odoo config file |
| `-AddonsPath` | Current directory | Path to addons |
| `-OnlyPaperFormatFix` | False | Only fix paper format, skip module installation |
| `-SkipPaperFormatFix` | False | Skip paper format fix, only install module |

### Usage Examples

```powershell
# Basic usage
.\fix_osus_comprehensive.ps1

# Custom database
.\fix_osus_comprehensive.ps1 -Database "production_db"

# Only fix paper format
.\fix_osus_comprehensive.ps1 -OnlyPaperFormatFix

# Custom Odoo installation
.\fix_osus_comprehensive.ps1 -OdooPath "D:\Odoo\odoo-bin" -ConfigPath "D:\Odoo\odoo.conf"
```

## What Each Solution Does

### Paper Format Fix
- Creates the missing `report.paperformat` record
- Creates the missing `ir.model.data` (external ID) record
- Links them together so `osus_invoice_report.paperformat_osus_invoice` resolves correctly

### Module Installation Fix
- Updates the module list
- Handles various module states (uninstalled, installed, to install, to upgrade)
- Provides multiple installation methods
- Verifies successful installation

### Cleanup Module
- Removes orphaned Many2one references
- Cleans up duplicate field definitions
- Provides a user-friendly GUI interface
- Creates missing external IDs

## Support

If you continue to have issues:

1. Check the Odoo server logs for detailed error messages
2. Verify all module dependencies are installed
3. Ensure the `osus_invoice_report` module files are in the correct location
4. Try restarting the Odoo server after running the fixes

For persistent issues, consider:
- Checking file permissions
- Verifying database connectivity
- Ensuring sufficient disk space
- Reviewing Odoo configuration settings
