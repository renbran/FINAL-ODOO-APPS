## Commission AX Module Upgrade Instructions

**Status**: Files deployed, database columns added, module marked for upgrade

### Current Situation:
1. ✅ Updated `sale_order.py` file deployed to CloudPepper
2. ✅ `commission_id` column added to `account_move` table (both databases)
3. ✅ `commission_lines_count` field defined in Python code
4. ⚠️ **Module needs to complete upgrade to register the new field**

### The Error You're Seeing:
```
Error: "sale.order"."commission_lines_count" field is undefined.
```

**Why**: The Python code has been updated, but Odoo hasn't reloaded it yet. The module is marked "to upgrade" and will complete when you access it through the web interface.

---

## SOLUTION: Manual Module Upgrade via Odoo UI

### Step-by-Step Instructions:

#### Option 1: Web Interface Upgrade (RECOMMENDED)

1. **Login to Odoo**:
   - Go to: https://erposus.com
   - Login with your admin credentials

2. **Enable Developer Mode**:
   - Click on **Settings** (top menu)
   - Scroll to bottom → Click **Activate the developer mode**
   - (Or add `?debug=1` to URL)

3. **Navigate to Apps**:
   - Click **Apps** in the top menu
   - Click **Update Apps List** (it may prompt you to update)

4. **Find and Upgrade commission_ax**:
   - In search box, remove the "Apps" filter to show all modules
   - Search for: **"Enhanced Commission"** or **"commission_ax"**
   - You should see the module with an **"Upgrade"** button
   - Click **Upgrade**
   - Wait for the upgrade to complete (may take 30-60 seconds)

5. **Clear Browser Cache**:
   - Press `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
   - Or close and reopen browser

6. **Test the Fix**:
   - Navigate to **Sales → Orders**
   - Open any sale order
   - Should load without RPC errors!

---

#### Option 2: Direct Database Upgrade (If UI doesn't work)

If you can't access the UI due to errors, use this SQL approach:

```bash
# SSH to CloudPepper
ssh -p 22 root@139.84.163.11

# Option A: Force upgrade via SQL (erposus database)
sudo -u postgres psql -d erposus -c "UPDATE ir_module_module SET state='to upgrade' WHERE name='commission_ax';"

# Option B: If module is stuck, try re-installing
sudo -u postgres psql -d erposus -c "UPDATE ir_module_module SET state='to install' WHERE name='commission_ax';"

# Restart Odoo to process the upgrade
sudo systemctl restart odoo

# Monitor the upgrade process
tail -f /var/log/odoo/odoo.log | grep -i commission
```

---

#### Option 3: Command Line Upgrade (Technical)

This requires proper Odoo CLI access:

```bash
# SSH to server
ssh -p 22 root@139.84.163.11

# Navigate to Odoo directory
cd /var/odoo/osusproperties

# Run upgrade (replace 'erposus' with your database name)
sudo -u odoo ./odoo-bin -c odoo.conf -d erposus -u commission_ax --stop-after-init

# If above doesn't work, try with python3 directly
sudo -u odoo python3 odoo-bin -c odoo.conf -d erposus -u commission_ax --stop-after-init

# Restart Odoo
sudo systemctl restart odoo
```

---

## Troubleshooting

### If you still see errors after upgrade:

1. **Clear Odoo's cache**:
   ```bash
   ssh -p 22 root@139.84.163.11
   rm -rf /var/odoo/.local/share/Odoo/sessions/*
   sudo systemctl restart odoo
   ```

2. **Verify field exists in database**:
   ```bash
   sudo -u postgres psql -d erposus -c "\d sale_order" | grep commission
   ```

3. **Check module state**:
   ```bash
   sudo -u postgres psql -d erposus -c "SELECT name, state, latest_version FROM ir_module_module WHERE name='commission_ax';"
   ```
   Should show: `state = 'installed'`

4. **Force field rebuild**:
   ```sql
   DELETE FROM ir_model_fields WHERE name='commission_lines_count' AND model='sale.order';
   ```
   Then upgrade module again.

---

## Expected Results After Upgrade:

✅ No more `commission_lines_count field is undefined` errors  
✅ Sale orders load correctly  
✅ Vendor bills load correctly  
✅ Commission data displays properly  

---

## Quick Verification Commands:

```bash
# Check module status
ssh -p 22 root@139.84.163.11 "sudo -u postgres psql -d erposus -c \"SELECT name, state FROM ir_module_module WHERE name='commission_ax';\""

# Check if field is registered
ssh -p 22 root@139.84.163.11 "sudo -u postgres psql -d erposus -c \"SELECT name, model FROM ir_model_fields WHERE name='commission_lines_count';\""

# Monitor Odoo logs
ssh -p 22 root@139.84.163.11 "tail -f /var/log/odoo/odoo.log"
```

---

## Summary of All Fixes Applied:

1. ✅ **Added `commission_lines_count` field** to `sale_order.py`
2. ✅ **Added `commission_id` column** to `account_move` table  
3. ✅ **Uploaded files** to CloudPepper production server
4. ✅ **Updated database schema** (both erposus and osusproperties)
5. ⏳ **Module upgrade pending** - requires UI/CLI action

**Next Action**: Follow Option 1 above to complete the module upgrade!
