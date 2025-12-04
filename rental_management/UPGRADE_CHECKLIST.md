# ✅ MODULE UPGRADE CHECKLIST

## 📋 Pre-Upgrade Checklist

- [ ] Code pushed to GitHub (commit 23912411) ✅ **DONE**
- [ ] All files validated (0 errors) ✅ **DONE**
- [ ] Module version 3.5.0 ✅ **DONE**
- [ ] Documentation complete ✅ **DONE**

---

## 🚀 UPGRADE STEPS (5 Minutes)

### Step 1: Login & Enable Developer Mode
- [ ] Login to Odoo as Administrator
- [ ] Go to **Settings**
- [ ] Click **"Activate Developer Mode"**
- [ ] OR add `?debug=1` to your URL

### Step 2: Update Apps List
- [ ] Go to **Apps** menu (main navigation)
- [ ] Click **"Update Apps List"** button (top menu bar)
- [ ] Click **"Update"** to confirm
- [ ] Wait for "Apps list updated" confirmation

### Step 3: Upgrade rental_management Module
- [ ] Still in Apps menu
- [ ] Click the **"Apps"** filter chip to remove it
- [ ] You should now see "All" or no filter
- [ ] In search box, type: **"rental_management"**
- [ ] Click on the **rental_management** module card
- [ ] Click the **"Upgrade"** button (top of card)
- [ ] Wait 30-60 seconds for upgrade to complete
- [ ] Look for success message

### Step 4: Clear Browser Cache
- [ ] Press **Ctrl + Shift + R** (hard refresh)
- [ ] OR: Press **Ctrl + Shift + Delete**
  - [ ] Select "Cached images and files"
  - [ ] Click "Clear data"
- [ ] Close any open sales contract tabs

### Step 5: Verify Changes
- [ ] Go to **Property → Sales → Sales Contracts**
- [ ] Open contract **PS/2025/12/0079** (from your screenshot)
- [ ] Look for **6 smart buttons** at top right:
  - [ ] 📋 Booking (count)
  - [ ] 💰 Installments (count)
  - [ ] 📄 All Invoices (count)
  - [ ] 📚 Created (count)
  - [ ] ✅ Paid (count)
  - [ ] 🔧 Maintenance (count)
- [ ] Look for **Payment Progress Dashboard** below header:
  - [ ] Overall Progress bar
  - [ ] Paid amount / Total amount
  - [ ] Installment Progress bar
  - [ ] Statistics grid
- [ ] Look for **Header Buttons** (stage-dependent):
  - [ ] If draft: "Create Booking Invoices" button
  - [ ] If booked: "Create Installment Plan" button

---

## ✅ SUCCESS INDICATORS

You'll know it worked when you see:

```
✓ Smart buttons visible at top right
✓ Numbers in parentheses (e.g., "Booking (3)")
✓ Payment dashboard with progress bars
✓ "Create Booking Invoices" button (if draft stage)
✓ No console errors in browser (F12 → Console)
```

---

## ❌ TROUBLESHOOTING (If Not Working)

### Issue: Smart Buttons Not Visible

**Try These (in order):**
1. [ ] Hard refresh again (Ctrl + Shift + R)
2. [ ] Clear ALL browser cache (Ctrl + Shift + Delete)
3. [ ] Close browser completely and reopen
4. [ ] Try different browser (Chrome, Firefox, Edge)
5. [ ] Logout and login again
6. [ ] Check if Developer Mode is still active
7. [ ] Verify module version in Apps (should be 3.5.0)

### Issue: "Field not found" Error

**Try These:**
1. [ ] Check Odoo logs for specific error
   ```bash
   tail -f /var/log/odoo/odoo.log | grep ERROR
   ```
2. [ ] Restart Odoo service:
   ```bash
   sudo systemctl restart odoo
   ```
3. [ ] Wait 60 seconds for Odoo to fully start
4. [ ] Try upgrading module again

### Issue: Old View Still Showing

**Delete Cached View:**
1. [ ] Settings → Technical → User Interface → Views
2. [ ] Search: "property.vendor.form.view"
3. [ ] Select the view
4. [ ] Click "Action → Delete"
5. [ ] Go back to Apps
6. [ ] Upgrade rental_management again
7. [ ] Odoo will recreate the view with new code

### Issue: Module Won't Upgrade

**Check These:**
1. [ ] Is module in "Installed" state? (not "To Install")
2. [ ] Do you have Administrator rights?
3. [ ] Is Developer Mode enabled?
4. [ ] Are there errors in Odoo logs?
5. [ ] Is Odoo service running?
   ```bash
   sudo systemctl status odoo
   ```

---

## 🔍 VERIFICATION TESTS

After upgrade, test these functions:

### Test 1: Smart Button Click
- [ ] Click **"Booking"** smart button
- [ ] Should open list of booking invoices
- [ ] Back to form

### Test 2: Dashboard Visibility
- [ ] Dashboard shows at top of form (below header)
- [ ] Progress bars are visible
- [ ] Numbers are displayed (not blank)

### Test 3: Button Actions (Draft Stage)
- [ ] "Create Booking Invoices" button exists
- [ ] Click it (or hover to see tooltip)
- [ ] Should show confirmation or create invoices

### Test 4: Computed Fields
- [ ] Open browser console (F12 → Console)
- [ ] Look for any JavaScript errors
- [ ] No errors = ✓

### Test 5: Different Sales Contract
- [ ] Open a different sales contract
- [ ] Smart buttons should still be visible
- [ ] Dashboard should show for all contracts

---

## 📊 EXPECTED RESULTS

### Before Upgrade:
```
[ Empty space where buttons should be ]

Property Sale Contract
Title: [value]
Reference: PS/2025/12/0079

[Regular fields...]
```

### After Upgrade:
```
[📋 3] [💰 12] [📄 15] [📚 15] [✅ 10] [🔧 2]
      Smart Buttons →

Property Sale Contract
Title: [value]
Reference: PS/2025/12/0079

╔══════════════════════════════════════╗
║ 💰 Payment Progress Overview         ║
║ Overall: [████████░░] 65%           ║
║ Paid: 325,000 / 500,000 AED         ║
╚══════════════════════════════════════╝

[Regular fields...]
```

---

## 🎯 QUICK COMMANDS

### Check Module Version (Odoo Shell)
```python
odoo shell -d your_database
>>> module = self.env['ir.module.module'].search([('name', '=', 'rental_management')])
>>> print(f'Version: {module.installed_version}')
# Should show: 3.5.0
```

### Check Fields Exist (Odoo Shell)
```python
>>> contract = self.env['property.vendor']
>>> print('booking_invoice_count' in contract._fields)
# Should show: True
```

### Check View Updated (Odoo Shell)
```python
>>> view = self.env['ir.ui.view'].search([('name', '=', 'property.vendor.form.view')], limit=1)
>>> print('booking_invoice_count' in view.arch)
# Should show: True
```

### Restart Odoo (Terminal)
```bash
sudo systemctl restart odoo
```

### Clear Asset Cache (Terminal)
```bash
rm -rf /path/to/odoo/filestore/your_db/assets/*
```

---

## 📞 STILL STUCK?

### Run Diagnostic Script:
```bash
cd d:\RUNNING APPS\FINAL-ODOO-APPS\rental_management
python check_module_status.py
```

### Read Full Documentation:
- **MODULE_UPGRADE_GUIDE.md** - Complete upgrade guide
- **QUICK_FIX_GUIDE.md** - Detailed troubleshooting
- **INVOICE_TRACKING_QUICK_START.md** - Feature walkthrough

### Check These Files:
- `models/sale_contract.py` - Lines 309+ (new fields)
- `views/property_vendor_view.xml` - Lines 51-123 (smart buttons + dashboard)

---

## ✅ COMPLETION CHECKLIST

Mark complete when:
- [x] Module upgraded successfully
- [ ] Smart buttons visible
- [ ] Payment dashboard visible
- [ ] Buttons clickable and functional
- [ ] No console errors
- [ ] All sales contracts show new features
- [ ] Tested on multiple contracts
- [ ] Tested booking invoice creation
- [ ] Documentation reviewed

---

## 📝 NOTES

**Important:**
- Code is already correct and in GitHub ✅
- Issue is just Odoo not loading new view
- Upgrade = Reload the module in Odoo
- Should take 5 minutes maximum

**Remember:**
- Always enable Developer Mode first
- Always update apps list before upgrading
- Always clear browser cache after upgrading
- Always hard refresh (Ctrl + Shift + R)

---

**Last Updated**: December 3, 2025  
**Module Version**: 3.5.0  
**Status**: Ready to Upgrade
