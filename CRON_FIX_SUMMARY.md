# Cron Job Fix Summary
## Issue: KeyError: None in ir_cron interval_type

### 🚨 **Problem Identified:**
- **Error**: `KeyError: None` in `odoo.addons.base.models.ir_cron`
- **Cause**: Cron job "CRM: Lead Assignment" (ID: 21) has `interval_type = NULL`
- **Impact**: Prevents cron jobs from running properly

---

## 🔧 **Solution Options:**

### **Option 1: Direct Database Fix (Recommended)**
Execute this SQL in your PostgreSQL database:

```sql
-- Fix the problematic cron job
UPDATE ir_cron 
SET interval_type = 'days', 
    interval_number = 1,
    active = false
WHERE cron_name = 'CRM: Lead Assignment' 
   OR interval_type IS NULL;

-- Verify the fix
SELECT id, cron_name, interval_type, interval_number, active 
FROM ir_cron 
WHERE interval_type IS NULL;
```

### **Option 2: Odoo Shell Fix**
1. Access your Odoo shell:
   ```bash
   python odoo-bin shell -d your_database_name
   ```

2. Run the fix script:
   ```python
   exec(open('fix_cron_in_odoo.py').read())
   ```

### **Option 3: Manual Fix via Odoo UI**
1. Go to **Settings > Technical > Automation > Scheduled Actions**
2. Find "CRM: Lead Assignment" 
3. Either:
   - Set **Interval Unit** to "Days" and **Interval Number** to 1
   - Or **Archive/Delete** the cron job if not needed

---

## 🛡️ **Prevention:**

### **Check for Other Issues:**
```sql
-- Find all cron jobs with potential issues
SELECT id, cron_name, interval_type, interval_number, active, nextcall
FROM ir_cron 
WHERE interval_type IS NULL 
   OR interval_type NOT IN ('minutes', 'hours', 'days', 'weeks', 'months');
```

### **Valid interval_type Values:**
- `'minutes'` - Run every X minutes
- `'hours'` - Run every X hours  
- `'days'` - Run every X days
- `'weeks'` - Run every X weeks
- `'months'` - Run every X months

---

## 📋 **Post-Fix Actions:**

1. **Restart Odoo server** to clear any cached cron states
2. **Monitor logs** for similar errors
3. **Review cron job configurations** in Settings > Technical > Scheduled Actions
4. **Re-enable cron jobs** that were deactivated, if needed

---

## ✅ **Verification:**

After applying the fix, verify with:

```sql
-- Should return no rows
SELECT * FROM ir_cron WHERE interval_type IS NULL;

-- Check that the fixed cron job is properly configured
SELECT id, cron_name, interval_type, interval_number, active 
FROM ir_cron 
WHERE cron_name = 'CRM: Lead Assignment';
```

---

**Files Created:**
- `find_cron_issues.py` - Script to identify problematic cron jobs
- `fix_cron_issues.sql` - SQL script to fix the database directly  
- `fix_cron_in_odoo.py` - Python script to run in Odoo shell
- `CRON_FIX_SUMMARY.md` - This documentation

**Issue Status:** ✅ **RESOLVED** - Solutions provided for immediate fix
