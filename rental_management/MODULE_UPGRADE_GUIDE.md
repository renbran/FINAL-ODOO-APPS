# 🚀 RENTAL MANAGEMENT MODULE UPGRADE GUIDE

## Issue: New Features Not Showing After Code Push

The invoice tracking features (smart buttons, payment dashboard) are in the code but not visible because **Odoo needs to reload the module**.

---

## ✅ SOLUTION: Upgrade the Module

### Method 1: Via Odoo UI (RECOMMENDED)

1. **Login to Odoo** as Administrator

2. **Enable Developer Mode**:
   - Go to Settings → Activate Developer Mode
   - OR add `?debug=1` to URL: `https://your-odoo-site.com/web?debug=1`

3. **Update Apps List**:
   - Go to **Apps** menu
   - Click **Update Apps List** button (top menu)
   - Confirm the action

4. **Upgrade rental_management**:
   - In Apps menu, remove "Apps" filter
   - Search for "rental_management"
   - Click on the module
   - Click **Upgrade** button
   - Wait for upgrade to complete (30-60 seconds)

5. **Clear Browser Cache**:
   - Press `Ctrl + Shift + R` (hard refresh)
   - Or clear browser cache completely

6. **Verify Changes**:
   - Open any Sales Contract (property.vendor)
   - You should now see:
     - ✅ Smart buttons at top right (Booking, Installments, All Invoices, etc.)
     - ✅ Payment Progress Dashboard below header
     - ✅ "Create Booking Invoices" button in header
     - ✅ Booking requirements monitoring alert

---

### Method 2: Via Command Line (ADVANCED)

```bash
# Stop Odoo service
sudo systemctl stop odoo

# Upgrade module
odoo -u rental_management --stop-after-init -d your_database_name

# Start Odoo service
sudo systemctl start odoo
```

---

### Method 3: Via Odoo Shell (DEVELOPER)

```bash
# Access Odoo shell
odoo shell -d your_database_name

# In Python shell:
>>> self.env['ir.module.module'].search([('name', '=', 'rental_management')]).button_immediate_upgrade()
>>> exit()
```

---

## 🔍 TROUBLESHOOTING

### Issue: "Upgrade button not visible"
**Solution**: 
- Make sure Developer Mode is enabled
- The module must be already installed (not in "To Install" state)

### Issue: "Smart buttons still not showing"
**Solution**:
1. Clear Odoo asset cache:
   ```bash
   rm -rf /path/to/odoo/filestore/your_db/assets/*
   ```
2. Clear browser cache (Ctrl + Shift + Delete)
3. Hard refresh (Ctrl + Shift + R)

### Issue: "Fields not found error"
**Solution**:
- The upgrade didn't complete properly
- Check Odoo logs: `tail -f /var/log/odoo/odoo.log`
- Look for errors related to rental_management
- Try upgrading again

### Issue: "Old view still showing"
**Solution**:
1. Go to Settings → Technical → User Interface → Views
2. Search for "property.vendor.form.view"
3. Delete the view
4. Upgrade module again
5. Odoo will recreate the view with new code

---

## 📋 WHAT WILL BE VISIBLE AFTER UPGRADE

### 1. Smart Buttons (Top Right):
```
┌─────────────┬──────────────┬─────────────┬──────────┬────────┬─────────────┐
│📋 Booking   │📅 Installments│📄 All      │📚 Created│✅ Paid │🔧 Maintenance│
│    (3)      │     (12)      │  (15)      │   (15)   │  (12)  │     (2)     │
└─────────────┴──────────────┴─────────────┴──────────┴────────┴─────────────┘
```

### 2. Header Buttons:
- **Draft Stage**:
  - `📋 Create Booking Invoices` - Create booking, DLD, admin invoices
  - `✓ Confirm Booking Complete` - Move to Booked stage (when 100% paid)

- **Booked Stage**:
  - `💰 Create Installment Plan` - Auto-generate installments
  - `📝 Manual Installments` - Custom installment creation
  - `⚡ Generate from Schedule` - Use payment schedule

### 3. Payment Progress Dashboard:
```
┌────────────────────────────────────────────────────────┐
│ 💰 Payment Progress Overview                           │
│                                                         │
│ Overall Progress:    [████████░░] 80%                 │
│ Paid: 400,000 / 500,000 AED                           │
│                                                         │
│ Installment Progress: [███████░░░] 70%                │
│ Outstanding: 100,000 AED                               │
│                                                         │
│ ┌──────┬──────┬──────┬──────┐                        │
│ │  15  │  15  │  12  │   3  │                        │
│ │Total │Creatd│ Paid │Pndng │                        │
│ └──────┴──────┴──────┴──────┘                        │
└────────────────────────────────────────────────────────┘
```

### 4. Booking Requirements Alert (Draft Stage):
```
┌────────────────────────────────────────┐
│ ⏳ Awaiting Booking Payments           │
│ Progress: [████░░░░░░] 33%            │
│                                        │
│ • Booking Payment: Pending             │
│ • DLD Fee: Pending                     │
│ • Admin Fee: Pending                   │
└────────────────────────────────────────┘
```

---

## 🎯 STEP-BY-STEP VERIFICATION

After upgrading, follow these steps to verify:

### Step 1: Open Sales Contract
1. Go to Property → Sales → Sales Contracts
2. Open the contract from your screenshot (PS/2025/12/0079)

### Step 2: Check Smart Buttons
- Look at **top right** of the form
- You should see 6 smart buttons
- Numbers in parentheses show counts

### Step 3: Check Header Buttons
- Look at the **top of the form** (header area)
- Based on stage, you'll see different buttons
- If stage = "draft", you should see "Create Booking Invoices"

### Step 4: Create Booking Invoices
1. Click "📋 Create Booking Invoices" button
2. System will create 3 invoices:
   - Booking Payment (based on booking percentage)
   - DLD Fee
   - Admin Fee
3. Smart buttons will update to show counts

### Step 5: Monitor Payment Progress
- Dashboard will appear showing:
  - Overall payment percentage
  - Amount paid vs total
  - Invoice counts
- Alert box will show which fees are paid/pending

### Step 6: Complete Booking
1. Create accounting invoices for the 3 booking fees
2. Register payments
3. When all 3 are paid (100%), button "Confirm Booking Complete" appears
4. Click it to move to "Booked" stage

### Step 7: Create Installment Plan
1. In "Booked" stage, click "💰 Create Installment Plan"
2. System generates remaining installment invoices
3. Smart buttons update with new counts
4. Payment dashboard shows full progress

---

## 🔧 MANUAL FIELD CHECK (IF NEEDED)

If upgrade doesn't work, manually check if fields exist:

```bash
# Access Odoo shell
odoo shell -d your_database_name

# Check if fields exist
>>> model = self.env['property.vendor']
>>> model._fields.keys()
# Should include: booking_invoice_count, installment_invoice_count, 
#                 total_invoice_count, overall_payment_percentage, etc.

# Check if action methods exist
>>> hasattr(model, 'action_create_booking_invoices_button')
# Should return: True

>>> hasattr(model, 'action_view_booking_invoices')
# Should return: True
```

---

## 📞 STILL NOT WORKING?

If after upgrade and cache clearing the features still don't appear:

1. **Check Odoo Logs**:
   ```bash
   tail -f /var/log/odoo/odoo.log | grep -i error
   ```

2. **Check Database**:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'property_vendor' 
   AND column_name LIKE '%invoice_count%';
   ```
   Should return: booking_invoice_count, installment_invoice_count, etc.

3. **Reinstall Module** (LAST RESORT):
   ```bash
   # Backup first!
   pg_dump your_db > backup.sql
   
   # Uninstall
   odoo -d your_db --uninstall rental_management
   
   # Install fresh
   odoo -d your_db -i rental_management
   ```

---

## 🎓 UNDERSTANDING THE WORKFLOW

After upgrade, the new workflow is:

```
1. CREATE BOOKING (Wizard)
   ↓
2. DRAFT STAGE
   - Click "Create Booking Invoices"
   - Creates 3 invoices (Booking, DLD, Admin)
   - Monitor via smart buttons & dashboard
   ↓
3. PAY BOOKING FEES (in Accounting)
   - Create account.move invoices
   - Register payments
   - Progress bar updates in real-time
   ↓
4. CONFIRM BOOKING COMPLETE
   - When 100% paid, button appears
   - Click to move to "Booked" stage
   ↓
5. BOOKED STAGE
   - Click "Create Installment Plan"
   - System generates remaining invoices
   - Continue monitoring payments
   ↓
6. COMPLETE SALE
   - When all invoices paid
   - Click "Confirm Sale"
   - Move to "Sold" stage
```

---

## 📚 RELATED DOCUMENTATION

- [📘 Invoice Tracking Quick Start](INVOICE_TRACKING_QUICK_START.md)
- [🚀 Quick Reference](QUICK_REFERENCE.md)
- [📋 Deployment Checklist](PRODUCTION_DEPLOYMENT_CHECKLIST.md)
- [📖 README](README.md)

---

**TL;DR**: 
1. Enable Developer Mode
2. Apps → Update Apps List
3. Search "rental_management" → Upgrade
4. Clear browser cache (Ctrl + Shift + R)
5. Open sales contract → Features should now be visible

---

**Last Updated**: December 3, 2025
