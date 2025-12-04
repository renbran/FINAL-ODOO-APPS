# Invoice Generation Flow - Visual Guide

## 🎯 Complete Payment Flow (Before vs After)

### ❌ **BEFORE FIX** (Incorrect Behavior)

```
Property (1,200,000 AED)
         ↓
    [Create Booking]
         ↓
Sale Contract
  - Payment Schedule: ❌ Empty (manual selection required)
  - Total Price: 1,200,000 AED ❌ (missing DLD + Admin)
         ↓
    [Generate Invoices]
         ↓
❌ WRONG: DLD and Admin split across installments
┌─────────────────────────────────────────────────┐
│ Invoice 1: Booking           120,000 AED        │
│ Invoice 2: Installment 1     320,000 AED  ❌     │
│            (includes part of DLD/Admin)         │
│ Invoice 3: Installment 2     320,000 AED  ❌     │
│ Invoice 4: Installment 3     320,000 AED  ❌     │
│ Invoice 5: Installment 4     320,000 AED  ❌     │
│                                                 │
│ Total: 1,400,000 AED  ❌ (Wrong calculation)     │
└─────────────────────────────────────────────────┘
```

---

### ✅ **AFTER FIX** (Correct Behavior)

```
Property (1,200,000 AED + Payment Plan)
  ✓ Payment Plan Available: YES
  ✓ Payment Schedule: UAE Standard 4 Installments
  ✓ DLD Fee (4%): 48,000 AED (auto-calculated)
  ✓ Admin Fee: 2,100 AED
  ✓ Total Customer Obligation: 1,250,100 AED
         ↓
    [Create Booking]
         ↓
Booking Wizard
  ✓ Base Sale Price: 1,200,000 AED
  ✓ DLD Fee: 48,000 AED
  ✓ Admin Fee: 2,100 AED
  ✓ Total Customer Price: 1,250,100 AED  ✅
         ↓
Sale Contract (Auto-Created)
  ✓ Payment Schedule: UAE Standard 4 Installments  ✅ (INHERITED!)
  ✓ Schedule from Property: TRUE
  ✓ Sale Price: 1,250,100 AED  ✅
  ✓ DLD Fee: 48,000 AED  ✅
  ✓ Admin Fee: 2,100 AED  ✅
  ✓ Include DLD in Plan: TRUE
  ✓ Include Admin in Plan: TRUE
         ↓
    [Generate from Schedule]  ⚡
         ↓
✅ CORRECT: Separate invoices for DLD and Admin
┌─────────────────────────────────────────────────┐
│ 📋 INVOICE STRUCTURE:                           │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: BOOKING                             │   │
│ │ Description: Booking/Reservation Payment  │   │
│ │ Amount: 120,000 AED (10%)                 │   │
│ │ Due: Day 0 (Today)                        │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: DLD_FEE  ✅                          │   │
│ │ Description: DLD Fee - Dubai Land Dept    │   │
│ │ Amount: 48,000 AED (4% of property)       │   │
│ │ Due: Day 30 (30 days after booking)       │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: ADMIN_FEE  ✅                        │   │
│ │ Description: Admin Fee - Processing       │   │
│ │ Amount: 2,100 AED (Fixed)                 │   │
│ │ Due: Day 30 (30 days after booking)       │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: INSTALLMENT                         │   │
│ │ Description: First Installment (1/4)      │   │
│ │ Amount: 270,000 AED (25% of property)     │   │
│ │ Due: Day 60                               │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: INSTALLMENT                         │   │
│ │ Description: Second Installment (2/4)     │   │
│ │ Amount: 270,000 AED                       │   │
│ │ Due: Day 150                              │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: INSTALLMENT                         │   │
│ │ Description: Third Installment (3/4)      │   │
│ │ Amount: 270,000 AED                       │   │
│ │ Due: Day 240                              │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ Type: INSTALLMENT                         │   │
│ │ Description: Fourth Installment (4/4)     │   │
│ │ Amount: 270,000 AED                       │   │
│ │ Due: Day 330 (Upon completion)            │   │
│ └───────────────────────────────────────────┘   │
│                                                 │
│ ═══════════════════════════════════════════════ │
│ TOTAL AMOUNT: 1,370,100 AED  ✅                 │
│                                                 │
│ Breakdown:                                      │
│   Booking:      120,000 AED                     │
│   DLD Fee:       48,000 AED  ✅ (Separate)      │
│   Admin Fee:      2,100 AED  ✅ (Separate)      │
│   Installments: 1,200,000 AED (4 x 270,000)     │
│   ─────────────────────────                     │
│   Total:      1,370,100 AED                     │
└─────────────────────────────────────────────────┘
```

---

## 💡 Key Differences Explained

### **1. Payment Schedule Inheritance**

| Before | After |
|--------|-------|
| ❌ Empty field - manual selection | ✅ Auto-inherited from property |
| ⏱️ Extra 2-3 minutes per booking | ⏱️ Instant (0 seconds) |
| ⚠️ Risk of wrong schedule selected | ✅ Always correct schedule |

### **2. Total Customer Price**

| Before | After |
|--------|-------|
| ❌ 1,200,000 AED (property only) | ✅ 1,250,100 AED (includes all fees) |
| 😕 Customer surprised by extra fees | 😊 Customer sees full cost upfront |
| 📉 Payment disputes | 📈 Transparent pricing |

### **3. Invoice Structure**

| Before | After |
|--------|-------|
| ❌ DLD/Admin split across installments | ✅ Separate dedicated invoices |
| ❌ Hard to track statutory fees | ✅ Clear fee categorization |
| ❌ Accounting confusion | ✅ Proper reporting by type |

---

## 🧮 Calculation Examples

### **Example 1: Standard Sale (1,200,000 AED)**

```
Property Details:
─────────────────────────────────────────
Sale Price:                  1,200,000 AED
Payment Plan:                UAE Standard 4 Installments
Booking:                     10% of sale price

Automatic Calculations:
─────────────────────────────────────────
DLD Fee (4%):                   48,000 AED  ✅
Admin Fee (Fixed):               2,100 AED  ✅
Total Customer Obligation:   1,250,100 AED  ✅

Booking (10%):                 120,000 AED
Remaining Property Price:    1,080,000 AED

Invoice Breakdown:
─────────────────────────────────────────
1. Booking:          120,000 AED (Day 0)
2. DLD Fee:           48,000 AED (Day 30)    ✅ Separate
3. Admin Fee:          2,100 AED (Day 30)    ✅ Separate
4. Installment 1:    270,000 AED (Day 60)    25% of remaining
5. Installment 2:    270,000 AED (Day 150)   25% of remaining
6. Installment 3:    270,000 AED (Day 240)   25% of remaining
7. Installment 4:    270,000 AED (Day 330)   25% of remaining
─────────────────────────────────────────
TOTAL:             1,370,100 AED  ✅

Verification:
  120,000 (booking) + 
   48,000 (DLD) + 
    2,100 (admin) + 
1,200,000 (property installments) = 1,370,100  ✅
```

### **Example 2: Luxury Property (5,000,000 AED)**

```
Property Details:
─────────────────────────────────────────
Sale Price:                  5,000,000 AED
Payment Plan:                UAE Premium 6 Installments
Booking:                     20% of sale price

Automatic Calculations:
─────────────────────────────────────────
DLD Fee (4%):                  200,000 AED  ✅
Admin Fee (Fixed):               5,000 AED  ✅
Total Customer Obligation:   5,205,000 AED  ✅

Booking (20%):               1,000,000 AED
Remaining Property Price:    4,000,000 AED

Invoice Structure:
─────────────────────────────────────────
1. Booking:        1,000,000 AED (Day 0)
2. DLD Fee:          200,000 AED (Day 30)    ✅ Separate
3. Admin Fee:          5,000 AED (Day 30)    ✅ Separate
4-9. Six Installments of 666,666 AED each    Split property only
─────────────────────────────────────────
TOTAL:             6,205,000 AED  ✅
```

---

## 📊 Invoice Type Categories

```
┌────────────────────────────────────────────────────────┐
│                  INVOICE CATEGORIES                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  🏦 UPFRONT PAYMENTS                                   │
│  ├── Booking/Reservation  (invoice_type='booking')     │
│  │   • First payment                                  │
│  │   • Secures property                               │
│  │   • Typically 10-20% of property price             │
│  │                                                    │
│  ├── DLD Fee  (invoice_type='dld_fee')  ✅ NEW        │
│  │   • Dubai Land Department fee                      │
│  │   • Always 4% of property price                    │
│  │   • Separate invoice (not split)                   │
│  │   • Due 30 days after booking                      │
│  │                                                    │
│  └── Admin Fee  (invoice_type='admin_fee')  ✅ NEW    │
│      • Administrative processing fee                  │
│      • Fixed amount or percentage                     │
│      • Separate invoice (not split)                   │
│      • Due 30 days after booking                      │
│                                                        │
│  💰 INSTALLMENT PAYMENTS                               │
│  └── Installments  (invoice_type='installment')       │
│      • Based on payment schedule template             │
│      • Split PROPERTY PRICE only (excludes DLD/Admin) │
│      • Number and timing per schedule                 │
│      • Example: 4 quarterly payments of 25% each      │
│                                                        │
│  🎁 COMPLETION PAYMENTS                                │
│  ├── Handover Payment  (invoice_type='handover')      │
│  │   • Payment upon key handover                      │
│  │   • If specified in payment plan                   │
│  │                                                    │
│  └── Completion Payment  (invoice_type='completion')  │
│      • Final payment upon project completion          │
│      • For off-plan properties                        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🎯 Payment Timeline Visualization

```
Day 0                Day 30              Day 60              Day 150             Day 240             Day 330
  │                    │                   │                   │                   │                   │
  │  📋 BOOKING        │  🏛️ DLD FEE       │  💰 INST 1        │  💰 INST 2        │  💰 INST 3        │  💰 INST 4
  │  120,000 AED       │  48,000 AED       │  270,000 AED      │  270,000 AED      │  270,000 AED      │  270,000 AED
  │                    │  📄 ADMIN FEE     │                   │                   │                   │
  │                    │   2,100 AED       │                   │                   │                   │
  │                    │                   │                   │                   │                   │
  ▼                    ▼                   ▼                   ▼                   ▼                   ▼
  
  Property            Statutory           First               Second              Third               Fourth
  Secured             Fees Due            Installment         Installment         Installment         Installment
  
  Running Total:      Running Total:      Running Total:      Running Total:      Running Total:      Running Total:
  120,000 AED         170,100 AED         440,100 AED         710,100 AED         980,100 AED         1,250,100 AED
                                                                                                      (+ 120k booking)
                                                                                                      = 1,370,100 AED ✅
```

---

## 🔄 Code Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CREATES BOOKING                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              booking_wizard.py: default_get()                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Load property data                                    │  │
│  │  2. Check if property.sale_lease == 'for_sale'            │  │
│  │  3. Calculate ask_price:                                  │  │
│  │     ask_price = property.total_customer_obligation        │  │
│  │                                                           │  │
│  │  4. Display in wizard:                                    │  │
│  │     Base Sale Price: 1,200,000 AED                        │  │
│  │     DLD Fee:            48,000 AED  ✅                     │  │
│  │     Admin Fee:           2,100 AED  ✅                     │  │
│  │     Total Customer Price: 1,250,100 AED  ✅               │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│           booking_wizard.py: create_booking_action()            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Prepare contract data:                                │  │
│  │     sale_price = ask_price  ✅                             │  │
│  │                                                           │  │
│  │  2. Check property payment plan:                          │  │
│  │     if property.is_payment_plan:                          │  │
│  │       payment_schedule_id = property.payment_schedule_id  │  │
│  │       use_schedule = True  ✅                              │  │
│  │       schedule_from_property = True  ✅                    │  │
│  │                                                           │  │
│  │  3. Pass DLD & Admin fees:                                │  │
│  │     dld_fee = property.dld_fee  ✅                         │  │
│  │     admin_fee = property.admin_fee  ✅                     │  │
│  │     include_dld_in_plan = True                            │  │
│  │     include_admin_in_plan = True                          │  │
│  │                                                           │  │
│  │  4. Create property.vendor record                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         sale_contract.py: Sale Contract Created                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Fields Set:                                              │  │
│  │  • customer_id: [Customer]                                │  │
│  │  • property_id: [Property]                                │  │
│  │  • sale_price: 1,250,100 AED  ✅                           │  │
│  │  • payment_schedule_id: [Inherited]  ✅                    │  │
│  │  • use_schedule: True                                     │  │
│  │  • schedule_from_property: True  ✅                        │  │
│  │  • dld_fee: 48,000 AED  ✅                                 │  │
│  │  • admin_fee: 2,100 AED  ✅                                │  │
│  │  • include_dld_in_plan: True                              │  │
│  │  • include_admin_in_plan: True                            │  │
│  │  • stage: 'booked'                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│      USER CLICKS "⚡ Generate from Schedule"                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│     sale_contract.py: action_generate_from_schedule()           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  STEP 1: Clear existing invoices                          │  │
│  │  self.sale_invoice_ids.unlink()                           │  │
│  │                                                           │  │
│  │  STEP 2: Generate Booking Invoice                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ name: "Booking/Reservation Payment"                 │  │  │
│  │  │ amount: 120,000 AED (10% of property)               │  │  │
│  │  │ invoice_type: 'booking'                             │  │  │
│  │  │ invoice_date: today                                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  STEP 3: Generate DLD Fee Invoice  ✅ NEW                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ name: "DLD Fee - Dubai Land Department"            │  │  │
│  │  │ amount: 48,000 AED (4% of property)                │  │  │
│  │  │ invoice_type: 'dld_fee'  ✅                          │  │  │
│  │  │ invoice_date: today + 30 days                       │  │  │
│  │  │ tax_ids: False (DLD fees not taxed)                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  STEP 4: Generate Admin Fee Invoice  ✅ NEW               │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ name: "Admin Fee - Administrative Processing"      │  │  │
│  │  │ amount: 2,100 AED (Fixed)                          │  │  │
│  │  │ invoice_type: 'admin_fee'  ✅                        │  │  │
│  │  │ invoice_date: today + 30 days                       │  │  │
│  │  │ tax_ids: False (admin fees typically not taxed)     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  STEP 5: Calculate Remaining Amount  ✅ CRITICAL FIX      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ property_base_price = property.price                │  │  │
│  │  │                     = 1,200,000 AED                 │  │  │
│  │  │                                                     │  │  │
│  │  │ remaining_amount = property_base_price - booking    │  │  │
│  │  │                  = 1,200,000 - 120,000              │  │  │
│  │  │                  = 1,080,000 AED                    │  │  │
│  │  │                                                     │  │  │
│  │  │ ⚠️ NOTE: DLD and Admin fees are NOT included        │  │  │
│  │  │         in remaining_amount calculation!            │  │  │
│  │  │         They are separate invoices!  ✅             │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  STEP 6: Generate Installment Invoices                   │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ For each line in payment_schedule:                  │  │  │
│  │  │   line_amount = remaining_amount * line.percentage  │  │  │
│  │  │               = 1,080,000 * 25% = 270,000 AED       │  │  │
│  │  │                                                     │  │  │
│  │  │   amount_per_invoice = line_amount / num_install    │  │  │
│  │  │                      = 270,000 / 1 = 270,000        │  │  │
│  │  │                                                     │  │  │
│  │  │   Create invoice:                                   │  │  │
│  │  │     name: "First Installment (1/4)"                │  │  │
│  │  │     amount: 270,000 AED  ✅                          │  │  │
│  │  │     invoice_type: 'installment'                     │  │  │
│  │  │     invoice_date: start_date + days_offset          │  │  │
│  │  │                                                     │  │  │
│  │  │   Repeat for all installments...                    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  STEP 7: Return Success Message                          │  │
│  │  "Payment schedule generated successfully with X invoices"│  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESULT: 7 INVOICES CREATED                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ✅ Invoice 1: Booking             120,000 AED            │  │
│  │  ✅ Invoice 2: DLD Fee              48,000 AED  (Separate)│  │
│  │  ✅ Invoice 3: Admin Fee             2,100 AED  (Separate)│  │
│  │  ✅ Invoice 4: Installment 1       270,000 AED            │  │
│  │  ✅ Invoice 5: Installment 2       270,000 AED            │  │
│  │  ✅ Invoice 6: Installment 3       270,000 AED            │  │
│  │  ✅ Invoice 7: Installment 4       270,000 AED            │  │
│  │  ═════════════════════════════════════════════            │  │
│  │  Total:                          1,370,100 AED  ✅         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Verification Checklist

After deployment, verify these key points:

```
PROPERTY LEVEL:
  □ Payment plan available checkbox works
  □ Payment schedule selection saves correctly
  □ DLD fee auto-calculates (4% of price)
  □ Admin fee displays correctly
  □ Total customer obligation = Price + DLD + Admin

BOOKING WIZARD:
  □ Opens with correct property data
  □ Shows base sale price
  □ Shows DLD fee (4%)
  □ Shows admin fee
  □ Total customer price = all three combined
  □ Ask price field shows total

SALE CONTRACT:
  □ Payment schedule field populated ✅
  □ Blue alert shows "inherited from property" ✅
  □ Use schedule checkbox checked
  □ Schedule from property = True
  □ Sale price = ask price from wizard
  □ DLD fee transferred correctly
  □ Admin fee transferred correctly
  □ Include DLD/Admin checkboxes checked

INVOICE GENERATION:
  □ "Generate from Schedule" button visible
  □ Confirmation dialog appears
  □ 7 invoices created (1 booking + 1 DLD + 1 admin + 4 installments)
  □ DLD invoice type = 'dld_fee' ✅
  □ Admin invoice type = 'admin_fee' ✅
  □ DLD amount = 48,000 AED (not split) ✅
  □ Admin amount = 2,100 AED (not split) ✅
  □ Each installment = 270,000 AED (property price / 4)
  □ Total of all invoices = 1,370,100 AED
  □ Invoice dates progress correctly

CALCULATIONS:
  □ Booking = 10% of property price (120,000)
  □ DLD = 4% of property price (48,000)
  □ Admin = fixed amount (2,100)
  □ Installments sum = property price - booking (1,080,000)
  □ Grand total = property + booking + DLD + admin (1,370,100)
```

---

**Status**: ✅ Deployed and operational  
**Module**: rental_management v3.4.0  
**Date**: December 2, 2025
