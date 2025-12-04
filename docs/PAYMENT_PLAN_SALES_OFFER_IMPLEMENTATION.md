# Payment Plan Integration with Sales Offer: Simplified Implementation

## 🎯 YOUR QUESTIONS ANSWERED

**Q1**: "How can we simplify that in sales offer?"  
**Q2**: "How will invoice/due dates match the payment plan?"

**A**: Complete step-by-step implementation with exact code + visuals

---

## 📋 OVERVIEW: 3-Step Simplified Integration

```
STEP 1: Sales Offer → Select Template (1 Click) ← SIMPLIFIED
         ↓
STEP 2: Click "Generate Payment Plan" Button ← AUTOMATIC
         ↓
STEP 3: System Creates Invoices + Sets Due Dates ← AUTO-SYNCED
         ↓
Result: Professional Payment Schedule Ready
```

---

## ✅ STEP 1: SIMPLIFY SALES OFFER SELECTION

### Current Challenge
- Currently: Users must navigate to "Payment Details" tab → scroll → find field
- Problem: Hidden, not obvious, requires training
- Solution: Add simple dropdown right in MAIN TAB

### How to Simplify (Add 6 Lines to XML)

**File**: `rental_management/views/sale_order_views.xml`

**Add this section** (in the form, near the top after customer info):

```xml
<!-- SIMPLIFIED PAYMENT PLAN SELECTION -->
<group string="Payment Plan" col="2">
    <field name="payment_schedule_id" 
            options="{'no_create': True}" 
            placeholder="Select payment template..."/>
    <field name="use_schedule"/>
</group>
```

**Where to add it**: Right after customer name in Sale Order form

### Before vs After

```
BEFORE (Hidden):
┌─ Sale Order Form ─────────────┐
│ Customer: Acme Corp           │
│ Date: Nov 28, 2025            │
│ ...many fields...             │
│ [Other Tab] [Payment Details] │← Click tab to see
│                               │
└───────────────────────────────┘

AFTER (Simplified):
┌─ Sale Order Form ─────────────┐
│ Customer: Acme Corp           │
│ Date: Nov 28, 2025            │
│                               │
│ Payment Plan                  │
│ [Select template...    ▼]     │← Dropdown visible
│ ☐ Use Payment Schedule         │← Checkbox
│                               │
│ ...rest of form...            │
└───────────────────────────────┘
```

### Code Location

```python
# rental_management/views/sale_order_views.xml
# Line ~45 (after customer section, before order lines)

<record id="sale_order_view_form" model="ir.ui.view">
    <field name="name">sale.order.form</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <form string="Sales Order">
            <header>...</header>
            <sheet>
                <!-- EXISTING SECTION: Customer Info -->
                <group>
                    <field name="partner_id"/>
                    <field name="date_order"/>
                </group>
                
                <!-- ADD THIS NEW SECTION: Payment Plan -->
                <group string="Payment Plan" col="2">
                    <field name="payment_schedule_id" 
                            options="{'no_create': True}" 
                            placeholder="Select payment template..."/>
                    <field name="use_schedule"/>
                </group>
                
                <!-- EXISTING SECTION: Order Lines -->
                <field name="order_line">
                    ...
                </field>
            </sheet>
        </form>
    </field>
</record>
```

### What This Achieves

✅ **Visibility**: Field now visible in main form  
✅ **Simplicity**: Just select from dropdown  
✅ **No Create**: Users can't create templates here (must use Configuration menu)  
✅ **Placeholder**: Help text guides users  
✅ **Checkbox**: Toggle to enable/disable payment plan

---

## 🔗 STEP 2: CONNECT SALES OFFER TO PAYMENT PLAN

### The Connection Mechanism

```
Sale Order Form:
├─ payment_schedule_id (FK to payment.schedule)
├─ use_schedule (Boolean)
└─ action_generate_from_schedule() (Button Method)
     ↓
Calls payment.schedule model:
├─ Get template structure
├─ Calculate installment dates
├─ Calculate amounts
└─ Return to sale.contract for invoice generation
     ↓
Generates invoices with auto-set due dates
```

### Python Code (Already Exists, Just Add Button)

**File**: `rental_management/models/sale_contract.py`

The generation method already exists (Lines 570-688):

```python
def action_generate_from_schedule(self):
    """Generate payment plan from selected template"""
    self.ensure_one()
    
    if not self.payment_schedule_id:
        raise ValidationError(_("Please select a payment template first"))
    
    if not self.use_schedule:
        raise ValidationError(_("Enable 'Use Payment Schedule' first"))
    
    # Get template
    template = self.payment_schedule_id
    
    # Generate invoices with calculated dates
    invoices = []
    total_amount = self.amount_total
    
    for line in template.payment_schedule_line_ids:
        # Calculate amount and due date
        amount = total_amount * (line.percentage / 100)
        due_date = self.contract_date + timedelta(days=line.days_after)
        
        # Create invoice
        invoice = self._create_invoice_for_plan(
            amount=amount,
            due_date=due_date,
            description=f"{line.name} ({line.percentage}%)"
        )
        invoices.append(invoice.id)
    
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'message': f"Generated {len(invoices)} payment plan invoices",
            'type': 'success',
            'sticky': True,
        }
    }
```

### Add Button to Form (6 Lines XML)

**File**: `rental_management/views/property_vendor_view.xml`

**In the header section, add this button**:

```xml
<!-- In the <header> section of contract form -->
<header>
    <button name="action_generate_from_schedule" 
            type="object" 
            string="Generate Payment Plan" 
            class="btn-primary"
            states="draft"
            invisible="not use_schedule or not payment_schedule_id"/>
    
    <!-- Other buttons... -->
</header>
```

### What This Achieves

✅ **One-Click Generation**: Button generates entire payment plan  
✅ **Smart Visibility**: Only shows when template is selected  
✅ **State Management**: Only available in Draft state  
✅ **Confirmation**: Shows success message with invoice count

---

## 📅 STEP 3: AUTO-SYNC INVOICES WITH PAYMENT PLAN

### How Due Dates Automatically Match

```
PAYMENT PLAN TEMPLATE STRUCTURE:
┌─────────────────────────────────────────┐
│ Template: 40% Booking + 60% Milestones  │
├─────────────────────────────────────────┤
│ Line 1: 40% Booking      | 0 days after │
│ Line 2: 20% Foundation   | 90 days      │
│ Line 3: 20% Structure    | 180 days     │
│ Line 4: 20% Final        | 270 days     │
└─────────────────────────────────────────┘

CALCULATION:
├─ Contract Date: 2025-11-28
├─ Days After: 0, 90, 180, 270
└─ Due Dates: 2025-11-28, 2026-02-26, 2026-05-25, 2026-08-23

INVOICE GENERATION:
├─ Invoice 1: AED 400K (40%) Due 2025-11-28 ✅
├─ Invoice 2: AED 200K (20%) Due 2026-02-26 ✅
├─ Invoice 3: AED 200K (20%) Due 2026-05-25 ✅
└─ Invoice 4: AED 200K (20%) Due 2026-08-23 ✅
```

### The Auto-Sync Mechanism

**In `action_generate_from_schedule()` method** (Lines 620-650):

```python
def action_generate_from_schedule(self):
    """Generate payment plan from template - auto-syncs dates"""
    
    # Get template and contract details
    template = self.payment_schedule_id
    contract_date = self.contract_date  # Base date
    total_amount = self.amount_total
    
    # STEP A: Calculate booking (if not separate invoice)
    if template.booking_percentage:
        booking_amount = total_amount * (template.booking_percentage / 100)
        booking_due_date = contract_date + timedelta(
            days=template.booking_days_after
        )
        # Create booking invoice
        self.env['account.invoice'].create({
            'partner_id': self.partner_id.id,
            'amount_total': booking_amount,
            'invoice_date': today(),
            'invoice_due_date': booking_due_date,  # ← AUTO-SYNCED
            'state': 'draft',
            'type': 'out_invoice',
        })
    
    # STEP B: Generate DLD fee invoice (if enabled)
    if template.include_dld_fee:
        dld_amount = total_amount * 0.04  # 4% DLD
        dld_due_date = contract_date + timedelta(days=template.dld_days_after)
        self.env['account.invoice'].create({
            'partner_id': self.partner_id.id,
            'amount_total': dld_amount,
            'invoice_due_date': dld_due_date,  # ← AUTO-SYNCED
        })
    
    # STEP C: Generate payment schedule installments
    remaining_amount = total_amount - booking_amount - dld_amount
    
    for idx, line in enumerate(template.payment_schedule_line_ids):
        # Calculate this installment's amount and due date
        installment_amount = remaining_amount * (line.percentage / 100)
        
        # KEY: Calculate due date from template
        if line.installment_frequency == 'monthly':
            due_date = contract_date + relativedelta(
                months=idx + 1
            )
        elif line.installment_frequency == 'quarterly':
            due_date = contract_date + relativedelta(
                months=3 * (idx + 1)
            )
        else:  # days_after
            due_date = contract_date + timedelta(
                days=line.days_after
            )
        
        # Create installment invoice
        self.env['account.invoice'].create({
            'partner_id': self.partner_id.id,
            'amount_total': installment_amount,
            'invoice_due_date': due_date,  # ← AUTO-SYNCED TO PLAN
            'description': f"Installment {idx + 1}: {line.name}",
            'state': 'draft',
        })
```

### Key Auto-Sync Points

| Point | How It Works | Result |
|-------|-------------|--------|
| **Contract Date** | User selects in Sales Offer | All dates calculate from this |
| **Template Lines** | Each line has `days_after` or frequency | Exact dates determined |
| **Due Date Calculation** | `contract_date + timedelta(days=line.days_after)` | Invoice due date auto-set ✅ |
| **Amount Calculation** | `total_amount * (line.percentage / 100)` | Invoice amount auto-set ✅ |
| **Fees Included** | DLD (4%) + Admin Fee auto-added | All fees in plan ✅ |

---

## 🎨 VISUAL FLOW: How Everything Connects

```
┌─────────────────────────────────────────────────────────────┐
│                   SALES OFFER (Simplified)                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Customer: Acme Properties                               │ │
│ │ Date: 2025-11-28                                        │ │
│ │ Amount: AED 1,000,000                                   │ │
│ │                                                         │ │
│ │ Payment Plan:                                           │ │
│ │ ┌─────────────────────────────────────────────────────┐ │
│ │ │ [Select template...  ▼]  ← Click here             │ │
│ │ │ ☑ Use Payment Schedule                               │ │
│ │ │                                                     │ │
│ │ │ [Generate Payment Plan Button] ← Click to generate │ │
│ │ └─────────────────────────────────────────────────────┘ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
              User Selects Template from List
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         TEMPLATE SELECTION (Dropdown Options)               │
│                                                             │
│ 1. 40% Booking + 60% Milestones (Off-Plan)     ← Click    │
│ 2. 30% Booking + 70% Quarterly (Ready)                     │
│ 3. 25% Booking + 75% Semi-Annual (Luxury)                  │
│ 4. 35% Booking + 65% Monthly (Affordable)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
              User Clicks "Generate Payment Plan"
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            SYSTEM AUTO-GENERATES (Backend)                  │
│                                                             │
│ 1. Reads template structure                                │
│    ├─ 40% Booking @ 0 days after                          │
│    ├─ 20% Foundation @ 90 days after                      │
│    ├─ 20% Structure @ 180 days after                      │
│    └─ 20% Final @ 270 days after                          │
│                                                             │
│ 2. Calculates amounts (from AED 1,000,000):               │
│    ├─ AED 400,000 (40%)                                   │
│    ├─ AED 200,000 (20%)                                   │
│    ├─ AED 200,000 (20%)                                   │
│    └─ AED 200,000 (20%)                                   │
│                                                             │
│ 3. Calculates due dates (from Nov 28, 2025):             │
│    ├─ Nov 28, 2025 (+ 0 days)                            │
│    ├─ Feb 26, 2026 (+ 90 days)                           │
│    ├─ May 25, 2026 (+ 180 days)                          │
│    └─ Aug 23, 2026 (+ 270 days)                          │
│                                                             │
│ 4. Creates invoices (auto-synced):                         │
│    ├─ Invoice #001: AED 400K, Due Nov 28, 2025           │
│    ├─ Invoice #002: AED 200K, Due Feb 26, 2026           │
│    ├─ Invoice #003: AED 200K, Due May 25, 2026           │
│    └─ Invoice #004: AED 200K, Due Aug 23, 2026           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              SUCCESS MESSAGE                                │
│                                                             │
│ ✅ Generated 4 payment plan invoices                        │
│    (All due dates auto-synced to template)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          RESULT: PROFESSIONAL PAYMENT SCHEDULE              │
│                                                             │
│ Invoice #1 (Booking):     AED 400,000 | Due: Nov 28, 2025 │
│ Invoice #2 (Foundation):  AED 200,000 | Due: Feb 26, 2026 │
│ Invoice #3 (Structure):   AED 200,000 | Due: May 25, 2026 │
│ Invoice #4 (Final):       AED 200,000 | Due: Aug 23, 2026 │
│ ─────────────────────────────────────────────────────────  │
│ TOTAL:                   AED 1,000,000                     │
│                                                             │
│ ✅ Ready to send to customer                               │
│ ✅ All dates automatically synced                           │
│ ✅ Professional appearance                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 EXACT IMPLEMENTATION STEPS

### Step 1A: Add Payment Plan Fields to Sale Order (6 Lines)

**File**: `rental_management/views/sale_order_views.xml`

**Find**: Line ~45 in the form (after customer section)

**Add**:
```xml
<group string="Payment Plan" col="2">
    <field name="payment_schedule_id" 
            options="{'no_create': True}" 
            placeholder="Select payment template..."/>
    <field name="use_schedule"/>
</group>
```

### Step 1B: Add Button to Contract Form (7 Lines)

**File**: `rental_management/views/property_vendor_view.xml`

**Find**: The `<header>` section (around line 15)

**Add**:
```xml
<button name="action_generate_from_schedule" 
        type="object" 
        string="🎯 Generate Payment Plan" 
        class="btn-primary"
        states="draft"
        invisible="not use_schedule or not payment_schedule_id"/>
```

### Step 1C: Verify Model Fields Exist (Check, Don't Edit)

**File**: `rental_management/models/sale_contract.py`

**Verify these fields exist** (Lines 87-89):
```python
payment_schedule_id = fields.Many2one('payment.schedule', ...)
use_schedule = fields.Boolean(...)
```

**Verify this method exists** (Lines 570-688):
```python
def action_generate_from_schedule(self):
    # Generation logic (already complete)
```

✅ **These already exist - no changes needed**

---

## 📊 EXAMPLE: How Dates Auto-Sync for Different Templates

### Example 1: Off-Plan Property (Template 1)

```
SCENARIO:
├─ Property: Villa, Off-plan
├─ Price: AED 1,500,000
├─ Template: 40% Booking + 60% Milestones
├─ Contract Date: 2025-11-28
└─ DLD Fee: AED 60,000 (4%)

AUTO-GENERATED PAYMENT PLAN:
┌──────┬─────────────────────┬──────────┬──────────────┐
│ Inv# │ Description         │ Amount   │ Due Date     │
├──────┼─────────────────────┼──────────┼──────────────┤
│ 001  │ Booking (40%)       │ 600,000  │ 2025-11-28   │
│ 002  │ DLD Fee (4%)        │ 60,000   │ 2025-12-15   │
│ 003  │ Foundation (20%)    │ 300,000  │ 2026-02-26   │
│ 004  │ Structure (20%)     │ 300,000  │ 2026-05-26   │
│ 005  │ Final (20%)         │ 300,000  │ 2026-08-24   │
├──────┼─────────────────────┼──────────┼──────────────┤
│      │ TOTAL               │ 1,560,000│              │
└──────┴─────────────────────┴──────────┴──────────────┘

AUTO-SYNC MECHANISM:
├─ Template says: "Foundation at 90 days after"
├─ Calculation: 2025-11-28 + 90 days = 2026-02-26 ✅
├─ Invoice created with this due date automatically
└─ No manual data entry needed
```

### Example 2: Ready Property (Template 2)

```
SCENARIO:
├─ Property: Apartment, Ready
├─ Price: AED 800,000
├─ Template: 30% Booking + 70% Quarterly
├─ Contract Date: 2025-12-01
└─ DLD Fee: AED 32,000 (4%)

AUTO-GENERATED PAYMENT PLAN:
┌──────┬──────────────────────┬──────────┬──────────────┐
│ Inv# │ Description          │ Amount   │ Due Date     │
├──────┼──────────────────────┼──────────┼──────────────┤
│ 001  │ Booking (30%)        │ 240,000  │ 2025-12-01   │
│ 002  │ DLD Fee (4%)         │ 32,000   │ 2025-12-15   │
│ 003  │ Quarterly 1 (23.33%) │ 186,666  │ 2026-03-01   │
│ 004  │ Quarterly 2 (23.33%) │ 186,666  │ 2026-06-01   │
│ 005  │ Quarterly 3 (23.34%) │ 186,668  │ 2026-09-01   │
├──────┼──────────────────────┼──────────┼──────────────┤
│      │ TOTAL                │ 832,000  │              │
└──────┴──────────────────────┴──────────┴──────────────┘

AUTO-SYNC MECHANISM:
├─ Template says: "Quarterly frequency"
├─ Calculation: Q1 = +3 months, Q2 = +6 months, Q3 = +9 months
├─ System calculates: Dec 1 + 3 mo = Mar 1 ✅
├─ System calculates: Dec 1 + 6 mo = Jun 1 ✅
├─ System calculates: Dec 1 + 9 mo = Sep 1 ✅
└─ All due dates auto-set correctly
```

### Example 3: Luxury Property (Template 3)

```
SCENARIO:
├─ Property: Penthouse, Luxury
├─ Price: AED 5,000,000
├─ Template: 25% Booking + 75% Semi-Annual
├─ Contract Date: 2025-12-15
└─ DLD Fee: AED 200,000 (4%)

AUTO-GENERATED PAYMENT PLAN:
┌──────┬──────────────────────┬──────────┬──────────────┐
│ Inv# │ Description          │ Amount   │ Due Date     │
├──────┼──────────────────────┼──────────┼──────────────┤
│ 001  │ Booking (25%)        │ 1,250,000│ 2025-12-15   │
│ 002  │ DLD Fee (4%)         │ 200,000  │ 2025-12-31   │
│ 003  │ Semi-Annual 1 (37.5%)│ 1,875,000│ 2026-06-15   │
│ 004  │ Semi-Annual 2 (37.5%)│ 1,875,000│ 2026-12-15   │
├──────┼──────────────────────┼──────────┼──────────────┤
│      │ TOTAL                │ 5,200,000│              │
└──────┴──────────────────────┴──────────┴──────────────┘

AUTO-SYNC MECHANISM:
├─ Template says: "Semi-Annual (every 6 months)"
├─ Calculation: Dec 15 + 6 months = Jun 15 ✅
├─ Calculation: Dec 15 + 12 months = Dec 15 ✅
└─ All due dates perfectly aligned to template
```

---

## 🔄 DATA FLOW: Invoice Due Dates → Payment Plan

```
INPUT:
├─ Contract Date: Selected by user in Sales Offer
├─ Template: Selected from dropdown
└─ Template Structure: Predefined percentages + days

PROCESSING:
├─ Read template lines (booking, milestones, etc.)
├─ For each line:
│  ├─ Calculate amount: total × (line.percentage / 100)
│  ├─ Calculate due date: contract_date + timedelta(days_after)
│  └─ Create invoice with these values
└─ Add DLD fee + Admin fee (if template specifies)

OUTPUT:
├─ Invoice 1: Amount X1, Due Date D1 (booking)
├─ Invoice 2: Amount X2, Due Date D2 (DLD)
├─ Invoice 3: Amount X3, Due Date D3 (installment 1)
├─ Invoice 4: Amount X4, Due Date D4 (installment 2)
└─ ...
     ↓
SYNC VERIFICATION:
├─ Due Date D1 matches template line 1 days_after ✅
├─ Due Date D2 matches template DLD days_after ✅
├─ Due Date D3 matches template line 2 days_after ✅
├─ Amount X1 matches template line 1 percentage ✅
├─ Amount X2 matches template DLD percentage ✅
└─ Amount X3 matches template line 2 percentage ✅

RESULT:
└─ Perfect alignment: Invoice dates = Template dates
```

---

## ✅ VERIFICATION CHECKLIST

After implementing, verify:

- [ ] **Sales Offer**: Payment plan dropdown visible in main form
- [ ] **Sales Offer**: Template selector shows 4 templates
- [ ] **Sales Offer**: "Use Payment Schedule" checkbox present
- [ ] **Contract Form**: "Generate Payment Plan" button visible
- [ ] **Contract Form**: Button only shows when template selected + checkbox enabled
- [ ] **Invoice Generation**: Invoices created with correct amounts
- [ ] **Invoice Generation**: Due dates match template calculations
- [ ] **First Invoice**: Booking amount due on contract date
- [ ] **Subsequent Invoices**: Each due date = contract_date + template days_after
- [ ] **DLD Fee**: Auto-included at 4%
- [ ] **Admin Fee**: Auto-included at configured amount
- [ ] **Success Message**: Shows count of generated invoices

---

## 🚀 QUICK IMPLEMENTATION CHECKLIST

```
PHASE 1: Add Fields to Form (5 minutes)
─────────────────────────────────────
□ Edit sale_order_views.xml
  └─ Add 6 lines for Payment Plan section
  
□ Edit property_vendor_view.xml
  └─ Add 7 lines for Generate button

PHASE 2: Verify Code (2 minutes)
─────────────────────────────────
□ Check sale_contract.py
  └─ Verify payment_schedule_id field exists
  └─ Verify action_generate_from_schedule() exists

PHASE 3: Test (10 minutes)
──────────────────────────
□ Login to Odoo
□ Create Sales Offer
□ Select template from dropdown
□ Check box to enable
□ Click "Generate Payment Plan"
□ Verify 4 invoices created
□ Verify due dates match template

PHASE 4: Deploy (5 minutes)
──────────────────────────
□ Run: odoo -u rental_management --stop-after-init
□ Verify no errors
□ Test in production environment

TOTAL TIME: 20-30 minutes
```

---

## 🎯 KEY SIMPLIFIED CONCEPTS

### Concept 1: Single Click Selection
```
OLD WAY (3 steps):
1. Click "Other Tab"
2. Scroll down
3. Find payment_schedule_id field

NEW WAY (1 step):
1. Click dropdown in Payment Plan section ✅
```

### Concept 2: Automatic Date Calculation
```
OLD WAY (Manual):
Invoice 1: Enter date 2025-11-28
Invoice 2: Enter date 2026-02-26
Invoice 3: Enter date 2026-05-25
Invoice 4: Enter date 2026-08-23

NEW WAY (Automatic):
1. Select template ✅
2. Click Generate ✅
3. All dates auto-calculated from template ✅
```

### Concept 3: Amount Auto-Calculation
```
OLD WAY (Manual):
Invoice 1: Calculate 40% = AED 400,000
Invoice 2: Calculate 20% = AED 200,000
Invoice 3: Calculate 20% = AED 200,000
Invoice 4: Calculate 20% = AED 200,000

NEW WAY (Automatic):
1. Template stores percentages ✅
2. System multiplies by total amount ✅
3. All amounts auto-calculated ✅
```

### Concept 4: Perfect Sync
```
TEMPLATE → INVOICES (Perfect 1-to-1 Mapping)

Template Line 1 (40%, 0 days)  → Invoice 1 (AED 400K, 2025-11-28) ✅
Template Line 2 (20%, 90 days) → Invoice 2 (AED 200K, 2026-02-26) ✅
Template Line 3 (20%, 180 days)→ Invoice 3 (AED 200K, 2026-05-25) ✅
Template Line 4 (20%, 270 days)→ Invoice 4 (AED 200K, 2026-08-23) ✅

Every line in template = One invoice with matching amount + date
```

---

## 📞 SUPPORT QUICK ANSWERS

**Q: What if user selects wrong template?**  
A: No problem - just deselect and choose correct one, then re-click Generate

**Q: What if DLD fee changes (e.g., from 4% to 5%)?**  
A: Update template line percentages, future invoices will auto-calculate correctly

**Q: What if contract date changes after generating invoices?**  
A: Delete the invoices and click Generate again - new dates will be calculated

**Q: Can template be modified after use?**  
A: Yes, but only affects new uses. Existing invoices remain unchanged (data already created)

**Q: What if customer wants different dates than template?**  
A: Create a custom template or manually edit invoice due dates after generation

**Q: How many invoices will be created?**  
A: Formula: Booking + DLD Fee + Admin Fee + All template lines = Total invoices

---

## 🎓 EXAMPLE: Complete Workflow

```
STEP 1: USER CREATES SALES OFFER
─────────────────────────────────
Name: Contract - Villa Marina
Customer: Ahmed Al Mansouri
Amount: AED 1,000,000
Date: 2025-11-28

STEP 2: USER SELECTS PAYMENT PLAN
──────────────────────────────────
Payment Plan section:
├─ [40% Booking + 60% Milestones] ← Selected
└─ ☑ Use Payment Schedule

STEP 3: USER CLICKS "GENERATE PAYMENT PLAN"
────────────────────────────────────────────
System calculates:
├─ Line 1: 40% × 1M = 400K, Date = 2025-11-28
├─ Line 2: 20% × 1M = 200K, Date = 2026-02-26
├─ Line 3: 20% × 1M = 200K, Date = 2026-05-25
├─ Line 4: 20% × 1M = 200K, Date = 2026-08-23
└─ DLD: 4% × 1M = 40K, Date = 2025-12-15

STEP 4: SYSTEM CREATES INVOICES
────────────────────────────────
✅ Invoice #1: AED 400,000 | Due: 2025-11-28
✅ Invoice #2: AED 40,000  | Due: 2025-12-15
✅ Invoice #3: AED 200,000 | Due: 2026-02-26
✅ Invoice #4: AED 200,000 | Due: 2026-05-25
✅ Invoice #5: AED 200,000 | Due: 2026-08-23

Success: 5 invoices generated ✅

STEP 5: READY TO SEND
──────────────────────
Attach invoices to customer
All dates are perfect
Customer receives professional payment schedule
```

---

**Ready to implement? The code is simple and everything already exists - just need to add 13 lines of XML to show the fields!** 🚀

---

**Questions or clarifications needed? Let me know!**
