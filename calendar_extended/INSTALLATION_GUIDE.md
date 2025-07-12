# Calendar Extended Module - Installation Guide

## 🎯 Module Overview

The Calendar Extended module provides advanced internal meeting management with approval workflows and department-wise employee grouping for Odoo 17.

## ✅ Pre-Installation Checklist

- [x] All critical errors fixed (selection field, model conflicts, dependencies)
- [x] Python syntax validated
- [x] Model references verified
- [x] Security access rules defined
- [x] Modern Odoo 17 syntax compliance

## 🚀 Installation Steps

**IMPORTANT:** The module has been updated with a critical fix for the `recurrence_pattern` field. Please follow these steps:

### Option 1: Server Shell Access
1. **Navigate to Odoo directory:**
   ```bash
   cd /var/odoo/osuserp
   ```

2. **Update the module:**
   ```bash
   sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update calendar_extended
   ```

3. **Restart Odoo service:**
   ```bash
   sudo systemctl restart odoo
   ```

### Option 2: Via Odoo Interface (Recommended if no shell access)
1. **Go to Apps menu** in Odoo
2. **Remove the Calendar Extended module** (if already installed)
3. **Upload/sync the updated module files** to your server
4. **Install Calendar Extended** again from Apps menu

### Option 3: Development Mode
1. **Enable Developer Mode** in Odoo
2. **Go to Apps → Update Apps List**
3. **Find Calendar Extended** and click **Upgrade**

## 📋 Post-Installation Verification

1. **Check Odoo log** for any installation messages
2. **Access Calendar app** in Odoo
3. **Verify new features** are available:
   - Internal Meeting creation
   - Approval workflow buttons
   - Department-wise employee grouping
   - Enhanced recurrence options

## 🎨 Key Features

### Internal Meeting Management
- **Draft → Pending Approval → Approved → Confirmed** workflow
- **Department-wise employee grouping** for easy navigation
- **Approval button** prevents immediate sending (as requested)
- **Enhanced attendee management**

### Technical Features
- Modern Odoo 17 compliance
- OWL JavaScript components
- Clean email templates
- Comprehensive security rules

## 🔧 Module Structure

```
calendar_extended/
├── __manifest__.py          # Module definition
├── models/                  # Python models
├── views/                   # XML views
├── static/                  # JavaScript/CSS
├── security/                # Access rules
└── data/                   # Default data
```

## 📞 Support

If you encounter any issues during installation:
1. Check the Odoo log files
2. Verify all dependencies are available
3. Ensure proper file permissions

**Status:** ✅ **Ready for Production**
