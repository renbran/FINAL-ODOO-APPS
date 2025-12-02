# 🔧 Rental Management Field Validation Error - Fix Guide

## 🎯 Problem Summary

**Error Pattern**: Multiple "Field does not exist" errors in Odoo logs for fields that DO exist in the code:
- `property.details`: Field 'is_payment_plan' (EXISTS in property_details.py line 148)
- `property.tag`: Field 'name' (EXISTS in property_details.py line 1146 as computed field)

**Root Cause**: Database schema out of sync with Python model definitions. The fields exist in code but are not reflected in the PostgreSQL database schema.

---

## 📋 Quick Fix (Automated)

### Option A: Run PowerShell Deployment Script
```powershell
cd "d:\RUNNING APPS\FINAL-ODOO-APPS"
.\deploy_rental_fix.ps1
```

This script will:
1. Upload the fix script to the server
2. Execute automated module upgrade
3. Clear invalid cached views
4. Restart Odoo service
5. Verify deployment

---

## 🛠️ Manual Fix (If Automated Fails)

### Step 1: SSH into Server
```bash
ssh root@139.84.163.11
# OR with SSH key:
ssh -i C:\Users\branm\.ssh\scholarix_vultr root@139.84.163.11
```

### Step 2: Stop Odoo Service
```bash
sudo systemctl stop odoo
```

### Step 3: Backup Database
```bash
sudo -u postgres pg_dump scholarixv2 > /tmp/scholarixv2_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 4: Clear Invalid Views (PostgreSQL)
```bash
sudo -u postgres psql -d scholarixv2
```

Then run in PostgreSQL:
```sql
-- Delete views referencing non-existent fields
DELETE FROM ir_ui_view 
WHERE id IN (
    SELECT v.id 
    FROM ir_ui_view v 
    WHERE v.arch_db LIKE '%is_payment_plan%' 
    AND v.model = 'property.details'
    AND NOT EXISTS (
        SELECT 1 FROM ir_model_fields 
        WHERE model = 'property.details' 
        AND name = 'is_payment_plan'
    )
);

-- Clear view cache
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view';

-- Exit
\q
```

### Step 5: Upgrade rental_management Module
```bash
sudo -u odoo /opt/odoo/odoo-bin \
    -d scholarixv2 \
    --addons-path=/var/odoo/scholarixv2 \
    -u rental_management \
    --stop-after-init \
    --log-level=warn
```

### Step 6: Start Odoo Service
```bash
sudo systemctl start odoo
sudo systemctl status odoo
```

### Step 7: Verify Fix
```bash
# Check logs for errors
sudo tail -f /var/log/odoo/odoo.log | grep -i error

# Test property dashboard menu access
curl -I https://scholarixglobal.com
```

---

## 🔍 Technical Details

### Field Verification (Confirmed Present in Code)

**is_payment_plan field** (property_details.py line 148):
```python
is_payment_plan = fields.Boolean(
    string='Payment Plan Available',
    default=False,
    help='Enable flexible payment plans for this property')
```

**PropertyTag.name field** (property_details.py line 1146):
```python
name = fields.Char(
    string='Tag Name', 
    translate=True, 
    compute='_compute_name', 
    store=True)
```

### Why Module Upgrade Fixes This

1. **Schema Sync**: `odoo-bin -u rental_management` reads Python model definitions and updates PostgreSQL schema
2. **Field Creation**: Creates missing database columns for new/modified fields
3. **View Validation**: Re-validates all XML views against updated schema
4. **Cache Clear**: Invalidates old cached views that reference outdated schema

---

## 🚨 Troubleshooting

### Issue: "Access Denied" when running odoo-bin
**Solution**: Ensure you're running as the `odoo` user:
```bash
sudo -u odoo /opt/odoo/odoo-bin -d scholarixv2 -u rental_management --stop-after-init
```

### Issue: Module update hangs
**Solution**: Check for locked database connections:
```bash
sudo -u postgres psql -d scholarixv2
SELECT * FROM pg_stat_activity WHERE datname = 'scholarixv2';
-- Kill blocking connections if needed:
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'scholarixv2' AND pid <> pg_backend_pid();
\q
```

### Issue: Errors persist after upgrade
**Solution**: Force reinstall the module:
```bash
sudo -u odoo /opt/odoo/odoo-bin \
    -d scholarixv2 \
    --addons-path=/var/odoo/scholarixv2 \
    -i rental_management \
    --stop-after-init
```

### Issue: "ModuleNotFoundError: rental_management"
**Solution**: Verify module location:
```bash
ls -la /var/odoo/scholarixv2/ | grep rental_management
# If missing, deploy from Git:
cd /var/odoo/scholarixv2
git pull origin main
```

---

## 📊 Validation Checklist

After running the fix, verify:

- [ ] Odoo service is running: `sudo systemctl status odoo`
- [ ] No field validation errors in logs: `sudo tail -n 100 /var/log/odoo/odoo.log`
- [ ] Property Dashboard menu accessible in UI
- [ ] No JavaScript console errors when accessing dashboard
- [ ] Database backup created in /tmp/

---

## 🔄 Rollback Procedure

If the fix causes issues:

```bash
# Stop Odoo
sudo systemctl stop odoo

# Restore database backup
sudo -u postgres psql -d scholarixv2 < /tmp/scholarixv2_backup_TIMESTAMP.sql

# Start Odoo
sudo systemctl start odoo
```

---

## 📞 Additional Support

**Server Details**:
- Host: 139.84.163.11
- Database: scholarixv2
- Odoo Path: /opt/odoo/odoo-bin
- Addons: /var/odoo/scholarixv2
- Logs: /var/log/odoo/odoo.log

**Key Files**:
- Model Definitions: rental_management/models/property_details.py
- Dashboard Component: rental_management/static/src/js/property_dashboard.js
- Client Action: rental_management/static/src/js/property_dashboard_action.js

**Latest Commits**:
- 7263e2e5: Fix property_dashboard registry error
- b5408b7b: Workspace cleanup

---

## 🎯 Expected Outcome

After successful fix:
✅ All field validation errors resolved
✅ Property Dashboard loads without errors
✅ rental_management module fully functional
✅ Database schema synchronized with code

**Estimated Time**: 5-10 minutes
**Risk Level**: Low (database backup created automatically)
**Downtime**: ~2-3 minutes during module upgrade

---

*Last Updated: December 2024*
*Module Version: rental_management 17.0.1.0.0*
