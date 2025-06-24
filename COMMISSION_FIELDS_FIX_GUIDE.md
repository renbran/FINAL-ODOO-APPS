
# 🔧 COMMISSION FIELDS MODULE FIX GUIDE

## 🚨 PROBLEM IDENTIFIED
**Error:** `KeyError: 'external_commission_type'` in purchase.order model
**Root Cause:** Missing commission fields in purchase.order model that are referenced by computed fields

## 📊 ERROR ANALYSIS
The error traceback shows:
1. **Cron Job Failure:** Document expiry dashboard update fails
2. **Field Dependency Error:** `show_external_percentage` field depends on missing `external_commission_type`
3. **Registry Corruption:** Missing field dependencies cause registry resolution failure

## ✅ SOLUTION IMPLEMENTED

### Fixed Files:
1. **`models/purchase_order.py`** - Added missing commission fields
2. **`views/purchase_order_views.xml`** - Added UI for commission fields

### Added Fields to purchase.order:
- `external_commission_type` - Selection field for commission type
- `external_percentage` - Float field for percentage commission
- `external_fixed_amount` - Monetary field for fixed commission
- `show_external_percentage` - Boolean computed field
- `show_external_fixed_amount` - Boolean computed field

### Added Compute Method:
- `_compute_show_commission_fields()` - Controls field visibility

## 🚀 RECOVERY STEPS

### Step 1: Update the Module
```bash
# The files have been updated with the missing fields
# Now update the module in Odoo
```

### Step 2: Upgrade Module in Odoo
1. Go to **Apps** → **Search "Commission Fields"**
2. Click **Upgrade** (or uninstall/reinstall if needed)
3. Wait for the upgrade to complete

### Step 3: Verify the Fix
```sql
-- Check if the fields were created
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'purchase_order' 
AND column_name LIKE '%commission%';
```

### Step 4: Restart Services (if needed)
```bash
# Stop Odoo
sudo systemctl stop odoo

# Clear Python cache
find /var/odoo -name "*.pyc" -delete
find /var/odoo -name "__pycache__" -type d -exec rm -rf {} +

# Restart Odoo
sudo systemctl start odoo
```

### Step 5: Test Cron Jobs
1. Go to **Settings** → **Technical** → **Automation** → **Scheduled Actions**
2. Find "Update Document Expiry Dashboard"
3. Click **Run Manually** to test

## 🔍 VERIFICATION CHECKLIST

- [ ] Module upgrades without errors
- [ ] Purchase order form shows commission fields
- [ ] Cron jobs run without errors
- [ ] No more `external_commission_type` KeyError in logs
- [ ] Document expiry dashboard updates successfully

## 📋 ALTERNATIVE RECOVERY (If upgrade fails)

### Option A: Clean Reinstall
```bash
# Remove problematic data
UPDATE ir_module_module 
SET state = 'uninstalled' 
WHERE name = 'commission_fields';

# Clear related model data
DELETE FROM ir_model_fields 
WHERE model = 'purchase.order' 
AND name LIKE '%commission%';
```

### Option B: Database-Level Fix
```sql
-- Add missing columns manually (if needed)
ALTER TABLE purchase_order 
ADD COLUMN external_commission_type VARCHAR(50) DEFAULT 'unit_price';

ALTER TABLE purchase_order 
ADD COLUMN external_percentage NUMERIC(16,2) DEFAULT 0.0;

ALTER TABLE purchase_order 
ADD COLUMN external_fixed_amount NUMERIC(16,2) DEFAULT 0.0;
```

## ⚠️ PREVENTION MEASURES

1. **Always test module upgrades in staging first**
2. **Keep database backups before major changes**
3. **Monitor Odoo logs for field dependency errors**
4. **Use proper @api.depends decorators in computed fields**

## 🆘 IF PROBLEMS PERSIST

1. **Check Odoo logs** for additional errors
2. **Verify all custom modules** are compatible
3. **Consider rolling back** to previous backup
4. **Contact system administrator** for production systems

## 📞 SUPPORT RESOURCES

- Odoo Community Forum
- Module documentation
- System administrator
- Database administrator (for SQL fixes)
