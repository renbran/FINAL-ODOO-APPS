# 🚀 PHASE 1 IMPLEMENTATION GUIDE - Template 1

## "40% Booking + 60% Milestones (Off-Plan)"

**Status**: Ready to Execute  
**Estimated Time**: 30 minutes  
**Complexity**: ⭐ Easy

---

## ✅ PRE-IMPLEMENTATION CHECKLIST

Before you start, verify these prerequisites:

```
☑ Odoo 17 running on CloudPepper (stagingtry.cloudpepper.site)
☑ rental_management module installed
☑ Logged in as admin or user with Configuration access
☑ Navigation bar visible (Sales, Configuration menus)
☑ No pending module upgrades
☑ Test database ready
```

---

## 📝 STEP-BY-STEP IMPLEMENTATION

### STEP 1: Navigate to Payment Schedules Configuration

```
Navigation Path:
1. Click: Configuration (top menu bar)
   ↓
2. Look for: "Payment Schedules" or "Rental Management" section
   ↓
3. Click: Payment Schedules
   ↓
4. Current Screen: List of existing payment schedules
```

**Expected Screen**:
- Title: "Payment Schedules"
- Button: "Create" (top-left)
- List: Any existing schedules (may be empty)

---

### STEP 2: Create New Payment Schedule

```
Action: Click "Create" button

New Form Opens with Fields:
├─ Schedule Name (text field) - EMPTY
├─ Description (text area) - EMPTY
├─ Schedule Type (dropdown) - "Sale Contract" or "Rental Contract"
├─ Sequence (number) - default 10
├─ Active (checkbox) - checked ✓
├─ Payment Lines (table) - EMPTY
└─ Total Percentage (read-only) - shows 0%
```

---

### STEP 3: Fill in Template Basic Info

**Copy-paste these exact values:**

```
Field: Schedule Name
Value: 40% Booking + 60% Milestones (Off-Plan)

Field: Description
Value: Standard off-plan payment structure for Dubai real estate. 
       40% collected at booking, 60% collected in 4 equal milestones 
       (15% each) tied to construction progress. Includes DLD fee (4%) 
       and admin charges. Complies with RERA guidelines.

Field: Schedule Type
Select: Sale Contract

Field: Sequence
Value: 10 (keep default)

Field: Active
Check: ✓ (keep checked)
```

**Expected Result**:
- Form shows your values
- Total Percentage still shows: 0% (because no lines added yet)

---

### STEP 4: Add Payment Line 1 (Booking)

**In the "Payment Lines" section, click "Add a line"**

```
New line appears. Fill these fields:

Line 1: Booking Payment
├─ Description: "Booking Payment"
├─ Sequence: 1
├─ Percentage (%): 40
├─ Days After Contract: 0
├─ Frequency: One Time Payment
├─ Number of Installments: 1
└─ Internal Notes: (leave empty)

After filling, press Tab or click outside to save the line
```

**Verification**:
- Line appears in table
- No red error markers

---

### STEP 5: Add Payment Line 2 (1st Milestone - Foundation)

**Click "Add a line" again**

```
Line 2: 1st Milestone - Foundation
├─ Description: "1st Milestone - Foundation"
├─ Sequence: 2
├─ Percentage (%): 15
├─ Days After Contract: 90
├─ Frequency: One Time Payment
├─ Number of Installments: 1
└─ Internal Notes: (leave empty)
```

---

### STEP 6: Add Payment Line 3 (2nd Milestone - Structure)

**Click "Add a line" again**

```
Line 3: 2nd Milestone - Structure
├─ Description: "2nd Milestone - Structure"
├─ Sequence: 3
├─ Percentage (%): 15
├─ Days After Contract: 180
├─ Frequency: One Time Payment
├─ Number of Installments: 1
└─ Internal Notes: (leave empty)
```

---

### STEP 7: Add Payment Line 4 (3rd Milestone - MEP)

**Click "Add a line" again**

```
Line 4: 3rd Milestone - MEP
├─ Description: "3rd Milestone - MEP"
├─ Sequence: 4
├─ Percentage (%): 15
├─ Days After Contract: 270
├─ Frequency: One Time Payment
├─ Number of Installments: 1
└─ Internal Notes: (leave empty)
```

---

### STEP 8: Add Payment Line 5 (4th Milestone - Handover)

**Click "Add a line" again**

```
Line 5: 4th Milestone - Handover
├─ Description: "4th Milestone - Handover"
├─ Sequence: 5
├─ Percentage (%): 15
├─ Days After Contract: 360
├─ Frequency: One Time Payment
├─ Number of Installments: 1
└─ Internal Notes: (leave empty)
```

---

### STEP 9: Verify Percentage Total

**After adding all 5 lines, check:**

```
"Total Percentage" field at top should show: 100%

Calculation:
40% + 15% + 15% + 15% + 15% = 100% ✓

If NOT 100%:
❌ Check each line's percentage
❌ Look for any calculation errors
❌ Scroll through all lines
```

**If you see 100%, proceed to save. If not, fix before saving.**

---

### STEP 10: Save Template

```
Action: Click "Save" button (top-left)

Expected Result:
✓ Form saves
✓ No validation errors
✓ You see success notification
✓ Template appears in list
✓ Template ID assigned
```

**If you see error**: 
- "Total percentage must equal 100%" → Check line percentages
- "Percentage must be between 0 and 100" → Check for invalid values
- "Days after contract cannot be negative" → Check for negative days

---

## 🧪 TEST: TEMPLATE CREATION VERIFICATION

### Test 1A: Verify Template Saved

```
Action: Go to Configuration → Payment Schedules

Expected Result:
✓ Your template "40% Booking + 60% Milestones" appears in list
✓ Description visible
✓ Active status = Yes
✓ Can click to open and view

Verification Checklist:
☑ Template name appears
☑ No duplicate templates created
☑ Template is active (not archived)
☑ All 5 lines visible when opened
☑ Total Percentage = 100%
```

---

## 📊 TEST: CREATE TEST PROPERTY & GENERATE PLAN

### Test 1B: Create Test Sales Order

```
Navigation: Sales → Sales Orders → Create New

Fill These Fields:

1. Customer
   ├─ Create new or select existing
   ├─ Name: "Test Customer - Off-Plan"
   └─ Email: test@example.com

2. Order Lines (Click "Add")
   ├─ Product: Select "Sample Property" or create:
   │   └─ Name: "Test Villa - AED 1M"
   │   └─ Type: "Service"
   │   └─ Price: 1,000,000
   │
   ├─ Quantity: 1
   ├─ Unit Price: 1,000,000
   └─ Taxes: 0% (no tax for clean testing)

3. Payment Configuration
   ├─ Payment Schedule: Select "40% Booking + 60% Milestones"
   ├─ Use Schedule: Check ✓
   ├─ DLD Fee: 4% (default)
   └─ Admin Fee: 50,000

Click: Save
```

**Expected Result**:
- Sales order created
- Status: Draft
- Payment Schedule field shows your template
- No validation errors

---

### Test 1C: Generate Payment Plan

**On the Sales Order form:**

```
Action: Click "Generate Payment Plan" button

Location: Look in the top button bar (green buttons area)

Expected Result:
✓ Success notification appears
✓ Message: "7 invoices created successfully"
✓ Form refreshes
✓ No error messages
```

**If no "Generate Payment Plan" button visible:**
- Check if payment_schedule_id field is populated
- Check UI changes were deployed (may need module refresh)
- Clear browser cache (Ctrl+Shift+R)

---

### Test 1D: Verify Invoices Created

**After plan generated:**

```
Action: Go to Accounting → Invoices (or similar menu path)

Or: Look for "Related Invoices" section on Sales Order

Expected Invoices: 7 Total

Invoice 1: BOOKING PAYMENT
├─ Amount: 400,000 AED (40% of 1M)
├─ Description: "Booking Payment"
├─ Due Date: TODAY (0 days after)
├─ Status: Draft
└─ Product: Test Villa line item

Invoice 2: DLD FEE
├─ Amount: 40,000 AED (4% of 1M)
├─ Description: "DLD Fee"
├─ Due Date: TODAY
├─ Status: Draft
└─ Note: Dubai Land Department fee

Invoice 3: ADMIN FEE
├─ Amount: 50,000 AED (fixed)
├─ Description: "Admin Fee"
├─ Due Date: TODAY
├─ Status: Draft
└─ Note: Fixed admin charge

Invoice 4: 1ST MILESTONE - FOUNDATION
├─ Amount: 150,000 AED (15% of 1M)
├─ Description: "1st Milestone - Foundation"
├─ Due Date: TODAY + 90 days = [28 January 2026]
├─ Status: Draft
└─ Milestone: Construction foundation complete

Invoice 5: 2ND MILESTONE - STRUCTURE
├─ Amount: 150,000 AED (15% of 1M)
├─ Description: "2nd Milestone - Structure"
├─ Due Date: TODAY + 180 days = [27 May 2026]
├─ Status: Draft
└─ Milestone: Structural work complete

Invoice 6: 3RD MILESTONE - MEP
├─ Amount: 150,000 AED (15% of 1M)
├─ Description: "3rd Milestone - MEP"
├─ Due Date: TODAY + 270 days = [24 August 2026]
├─ Status: Draft
└─ Milestone: Mechanical/Electrical/Plumbing complete

Invoice 7: 4TH MILESTONE - HANDOVER
├─ Amount: 150,000 AED (15% of 1M)
├─ Description: "4th Milestone - Handover"
├─ Due Date: TODAY + 360 days = [23 November 2026]
├─ Status: Draft
└─ Milestone: Property handover to customer
```

**Total Amount Check**:
```
400,000 (Booking)
+ 40,000 (DLD)
+ 50,000 (Admin)
+ 150,000 (Milestone 1)
+ 150,000 (Milestone 2)
+ 150,000 (Milestone 3)
+ 150,000 (Milestone 4)
─────────────
= 1,090,000 AED ✓
```

---

### Test 1E: Verify Date Calculations

**Check each invoice's due date:**

```
TODAY = November 28, 2025 (example)

Invoice 1 (Booking): Nov 28, 2025 ✓
Invoice 2 (DLD): Nov 28, 2025 ✓
Invoice 3 (Admin): Nov 28, 2025 ✓
Invoice 4 (Milestone 1): Jan 28, 2026 (+90 days) ✓
Invoice 5 (Milestone 2): May 27, 2026 (+180 days) ✓
Invoice 6 (Milestone 3): Aug 24, 2026 (+270 days) ✓
Invoice 7 (Milestone 4): Nov 23, 2026 (+360 days) ✓

VERIFICATION:
☑ Booking invoices: Due today
☑ Milestone invoices: Due on correct milestone date
☑ Dates are future dates (logical for construction)
☑ Dates follow construction progression (90→180→270→360)
```

---

## ✅ FINAL VALIDATION CHECKLIST

**Use this checklist to confirm Phase 1 success:**

```
TEMPLATE CREATION:
☑ Template name: "40% Booking + 60% Milestones (Off-Plan)"
☑ Description: Comprehensive and clear
☑ Schedule Type: "Sale Contract"
☑ Active: Yes (checked)
☑ Total Percentage: 100%
☑ Lines count: 5
☑ Saved without errors

TEST PROPERTY:
☑ Sales order created
☑ Customer assigned
☑ Property line item: AED 1,000,000
☑ Payment Schedule: Template assigned
☑ Use Schedule: Checked
☑ DLD Fee: 4%
☑ Admin Fee: 50,000

PAYMENT PLAN GENERATION:
☑ "Generate Payment Plan" button clicked
☑ Success notification: "7 invoices created"
☑ No error messages

INVOICES CREATED:
☑ Total invoices: 7
☑ Booking invoice: 400,000 AED (40%)
☑ DLD fee: 40,000 AED (4%)
☑ Admin fee: 50,000 AED
☑ Milestone 1: 150,000 AED (90 days)
☑ Milestone 2: 150,000 AED (180 days)
☑ Milestone 3: 150,000 AED (270 days)
☑ Milestone 4: 150,000 AED (360 days)
☑ Total: 1,090,000 AED

DATE ACCURACY:
☑ Booking due: Today
☑ DLD due: Today
☑ Admin due: Today
☑ Milestone 1: +90 days
☑ Milestone 2: +180 days
☑ Milestone 3: +270 days
☑ Milestone 4: +360 days

BUSINESS LOGIC:
☑ Invoices are in Draft status
☑ Can be confirmed to accounting
☑ Descriptions are professional
☑ Amounts make sense to customer
☑ Payment schedule is logical

PROFESSIONAL APPEARANCE:
☑ Template name: Professional ✓
☑ Description: Clear and complete ✓
☑ Invoice layout: Professional ✓
☑ No typos or errors ✓
☑ Milestone names: Clear and descriptive ✓
```

---

## 🎯 SUCCESS CRITERIA

**Phase 1 is COMPLETE when:**

```
✅ All checkboxes above are checked
✅ 7 invoices correctly created
✅ Amounts match calculations exactly
✅ Dates are correct
✅ No validation errors
✅ Template appears in dropdown for future use
```

---

## ⚠️ TROUBLESHOOTING

### Problem: "Total percentage must equal 100%"

**Solution**:
1. Open template
2. Check each line's percentage
3. Sum: 40 + 15 + 15 + 15 + 15 = 100
4. If not 100%, adjust percentages
5. Save again

---

### Problem: "Generate Payment Plan" button not visible

**Solution**:
1. Check if module was deployed
2. Clear browser cache (Ctrl+Shift+R)
3. Refresh page
4. Check if payment_schedule_id field is visible
5. If not visible, may need XML deployment

---

### Problem: Only 5-6 invoices created instead of 7

**Solution**:
1. Check if DLD fee is enabled (4%)
2. Check if Admin fee is set (50,000)
3. Check template has exactly 5 lines
4. Verify amounts on created invoices

---

### Problem: Due dates are incorrect

**Solution**:
1. Check each line's "Days After Contract" value
2. Verify:
   - Line 1: 0 days
   - Line 2: 90 days
   - Line 3: 180 days
   - Line 4: 270 days
   - Line 5: 360 days
3. Recalculate manually (Today + days = due date)

---

## 📋 NEXT STEPS

**After Phase 1 validation is COMPLETE:**

1. ✅ Phase 1 complete (this guide)
2. → Phase 2: Template 2 (30% + 70% Quarterly)
3. → Phase 3: Template 3 (25% + 75% Semi-Annual)
4. → Phase 4: Template 4 (35% + 65% Monthly)

**Timeline**: Each phase takes ~25-30 minutes  
**Total**: ~2 hours for all 4 templates

---

**Phase 1 Status**: ✅ Ready to Execute  
**Last Updated**: November 28, 2025  
**Documentation**: Complete
