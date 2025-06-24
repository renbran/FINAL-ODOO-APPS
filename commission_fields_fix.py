#!/usr/bin/env python3
"""
Commission Fields Module Fix Script
This script fixes the missing field dependency error in the commission_fields module.
"""

import os
import sys

def create_commission_fix_guide():
    """Create a comprehensive fix guide for the commission fields issue"""
    
    fix_guide = """
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
"""
    
    return fix_guide

def validate_commission_fix(module_path):
    """Validate that the commission fields fix is properly implemented"""
    print("🔍 VALIDATING COMMISSION FIELDS FIX...")
    
    issues = []
    
    # Check purchase_order.py
    purchase_model_path = os.path.join(module_path, 'models', 'purchase_order.py')
    if os.path.exists(purchase_model_path):
        with open(purchase_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_fields = [
            'external_commission_type',
            'external_percentage', 
            'external_fixed_amount',
            'show_external_percentage',
            'show_external_fixed_amount'
        ]
        
        for field in required_fields:
            if field in content:
                print(f"✅ {field} field found")
            else:
                issues.append(f"❌ Missing field: {field}")
        
        if '_compute_show_commission_fields' in content:
            print("✅ Compute method found")
        else:
            issues.append("❌ Missing compute method: _compute_show_commission_fields")
        
        if "@api.depends('external_commission_type')" in content:
            print("✅ Proper @depends decorator found")
        else:
            issues.append("❌ Missing or incorrect @depends decorator")
    
    # Check views
    purchase_view_path = os.path.join(module_path, 'views', 'purchase_order_views.xml')
    if os.path.exists(purchase_view_path):
        with open(purchase_view_path, 'r', encoding='utf-8') as f:
            view_content = f.read()
        
        if 'external_commission_type' in view_content:
            print("✅ Commission fields added to views")
        else:
            issues.append("❌ Commission fields not added to views")
    
    return issues

if __name__ == "__main__":
    commission_module_path = r"d:\RUNNING APPS\ready production\odoo_17_final\commission_fields"
    
    print("🔧 COMMISSION FIELDS MODULE FIX")
    print("=" * 50)
    
    # Validate the fix
    if os.path.exists(commission_module_path):
        issues = validate_commission_fix(commission_module_path)
        
        if issues:
            print("\n❌ REMAINING ISSUES:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ ALL FIXES IMPLEMENTED CORRECTLY")
            print("   Ready for module upgrade in Odoo")
    
    # Generate fix guide
    fix_guide = create_commission_fix_guide()
    
    # Save to file
    with open('COMMISSION_FIELDS_FIX_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(fix_guide)
    
    print("\n📋 FIX GUIDE CREATED: COMMISSION_FIELDS_FIX_GUIDE.md")
    print("\n🎯 NEXT STEPS:")
    print("   1. Go to Odoo Apps")
    print("   2. Find 'Commission Fields' module") 
    print("   3. Click 'Upgrade'")
    print("   4. Test cron jobs")
    print("   5. Monitor logs for errors")
    
    if not issues:
        print("\n🟢 MODULE IS READY FOR UPGRADE!")
    else:
        print(f"\n🔴 FIX {len(issues)} REMAINING ISSUES FIRST")
