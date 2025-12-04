# 📊 Booking Percentage Configuration Guide

## 🎯 Overview

The **Configurable Booking Percentage** feature allows different projects and properties to have different booking fee requirements. This is essential for real estate businesses that manage multiple projects with varying booking terms.

### **Key Benefits:**
- ✅ **Project-Level Configuration**: Set default booking percentage for entire projects
- ✅ **Property-Level Override**: Individual properties can override project settings
- ✅ **Automatic Inheritance**: Booking percentage flows: Project → Property → Sale Contract
- ✅ **Flexible Requirements**: Support 5%, 10%, 15%, 20%, or any custom percentage

---

## 🏗️ Configuration Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     CONFIGURATION HIERARCHY                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣ PROJECT LEVEL                                            │
│     ┌────────────────────────────────────────────────────┐  │
│     │ Property Project                                   │  │
│     │ • Booking Percentage: 15%                          │  │
│     │ • Booking Type: Percentage                         │  │
│     │ • Applies to all properties in project             │  │
│     └────────────────────────────────────────────────────┘  │
│                              ↓                               │
│  2️⃣ PROPERTY LEVEL                                           │
│     ┌────────────────────────────────────────────────────┐  │
│     │ Property A (inherits from project)                 │  │
│     │ • Use Project Booking %: ✓                         │  │
│     │ • Booking Percentage: 15% (from project)           │  │
│     └────────────────────────────────────────────────────┘  │
│                              ↓                               │
│     ┌────────────────────────────────────────────────────┐  │
│     │ Property B (custom override)                       │  │
│     │ • Use Project Booking %: ✗                         │  │
│     │ • Custom Booking %: 20%                            │  │
│     └────────────────────────────────────────────────────┘  │
│                              ↓                               │
│  3️⃣ SALE CONTRACT LEVEL                                      │
│     ┌────────────────────────────────────────────────────┐  │
│     │ When booking created, inherits from property       │  │
│     │ • Booking Percentage: 15% or 20%                   │  │
│     │ • Used to calculate booking invoice amount         │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📝 Step-by-Step Configuration

### **Step 1: Configure Project (Optional but Recommended)**

1. Navigate to **Property → Configuration → Property Project**
2. Open your project (e.g., "Downtown Towers")
3. Scroll to **"Booking Configuration (For Sale Projects)"** section
4. Set:
   - **Booking Type**: "Percentage of Sale Price"
   - **Booking Percentage**: Enter desired percentage (e.g., 15%)
5. Save the project

**Result**: All properties in this project will inherit 15% booking percentage

---

### **Step 2A: Configure Property (Inherit from Project)**

1. Navigate to **Property → Properties**
2. Open a property in the project
3. In **"Booking Configuration"** section:
   - **Use Project Booking %**: ✓ (Checked)
   - **Booking Percentage**: Shows inherited value (read-only)
4. See info alert: "Inheriting 15% from project"

**Result**: This property will use the project's booking percentage

---

### **Step 2B: Configure Property (Custom Override)**

1. Navigate to **Property → Properties**
2. Open a property in the project
3. In **"Booking Configuration"** section:
   - **Use Project Booking %**: ✗ (Unchecked)
   - **Custom Booking %**: Enter custom value (e.g., 20%)
   - **Booking Percentage**: Shows custom value (computed)
4. See info alert: "Using custom booking percentage"

**Result**: This property will use 20% instead of project's 15%

---

### **Step 3: Create Booking (Automatic Inheritance)**

1. Navigate to property
2. Click **"Create Booking"** button
3. Fill in customer details
4. Click **"Create Booking"**

**What Happens Automatically**:
- Sale Contract created with inherited booking percentage
- Booking amount calculated: `Sale Price × Booking Percentage`
- Example: 1,200,000 AED × 15% = 180,000 AED booking fee

---

## 💡 Use Case Examples

### **Example 1: Luxury Project (High Booking Requirement)**

```
Project: "Marina Heights Luxury"
├── Booking Percentage: 20%
├── Property A: Villa (inherits 20%)
│   └── Sale Price: 5,000,000 AED
│   └── Booking Fee: 1,000,000 AED (20%)
└── Property B: Penthouse (custom 25%)
    └── Sale Price: 8,000,000 AED
    └── Booking Fee: 2,000,000 AED (25%)
```

**Why**: Luxury projects often require higher booking fees to secure serious buyers.

---

### **Example 2: Affordable Housing Project (Low Booking)**

```
Project: "Green Valley Residences"
├── Booking Percentage: 5%
├── Property C: Studio (inherits 5%)
│   └── Sale Price: 400,000 AED
│   └── Booking Fee: 20,000 AED (5%)
└── Property D: 1BR (inherits 5%)
    └── Sale Price: 600,000 AED
    └── Booking Fee: 30,000 AED (5%)
```

**Why**: Lower booking fees make properties more accessible to first-time buyers.

---

### **Example 3: Mixed Project (Varied Requirements)**

```
Project: "Downtown Mixed-Use"
├── Booking Percentage: 10% (default)
├── Property E: Office (custom 15%)
│   └── Sale Price: 2,000,000 AED
│   └── Booking Fee: 300,000 AED (15%)
├── Property F: Retail (custom 20%)
│   └── Sale Price: 1,500,000 AED
│   └── Booking Fee: 300,000 AED (20%)
└── Property G: Apartment (inherits 10%)
    └── Sale Price: 800,000 AED
    └── Booking Fee: 80,000 AED (10%)
```

**Why**: Commercial units may require higher booking fees than residential.

---

## 🔍 Technical Implementation Details

### **Database Fields Added:**

#### **property.project Model:**
```python
booking_percentage = fields.Float(
    string='Booking Percentage',
    default=10.0,
    help='Default booking percentage for properties in this project'
)
booking_type = fields.Selection([
    ('fixed', 'Fixed Amount'),
    ('percentage', 'Percentage of Sale Price')
], default='percentage')
```

#### **property.details Model:**
```python
use_project_booking = fields.Boolean(
    string='Use Project Booking %',
    default=True,
    help='Inherit booking percentage from project'
)
booking_percentage = fields.Float(
    string='Booking Percentage',
    compute='_compute_booking_percentage',
    store=True
)
custom_booking_percentage = fields.Float(
    string='Custom Booking %',
    help='Custom booking percentage for this property'
)
```

#### **property.vendor Model (Sale Contract):**
```python
booking_percentage = fields.Float(
    string='Booking %',
    help='Inherited from property or set manually'
)
```

---

## 📊 Booking Amount Calculation

### **Formula:**
```
Booking Amount = Sale Price × (Booking Percentage ÷ 100)
```

### **Examples:**

| Sale Price    | Booking % | Booking Amount |
|---------------|-----------|----------------|
| 1,200,000 AED | 5%        | 60,000 AED     |
| 1,200,000 AED | 10%       | 120,000 AED    |
| 1,200,000 AED | 15%       | 180,000 AED    |
| 1,200,000 AED | 20%       | 240,000 AED    |
| 5,000,000 AED | 20%       | 1,000,000 AED  |

---

## ✅ Verification Checklist

After configuration, verify:

```
PROJECT LEVEL:
  ☐ Open project form
  ☐ "Booking Configuration" section visible (for sale projects only)
  ☐ Can set booking percentage (e.g., 15%)
  ☐ Info message shows: "This will be inherited by all properties"
  ☐ Save project without errors

PROPERTY LEVEL (INHERIT):
  ☐ Open property in project
  ☐ "Booking Configuration" section visible
  ☐ "Use Project Booking %" checkbox checked by default
  ☐ "Booking Percentage" shows project's percentage (read-only)
  ☐ Info alert shows: "Inheriting X% from project"

PROPERTY LEVEL (CUSTOM):
  ☐ Uncheck "Use Project Booking %"
  ☐ "Custom Booking %" field becomes visible
  ☐ Enter custom percentage (e.g., 20%)
  ☐ "Booking Percentage" updates to custom value
  ☐ Info alert shows: "Using custom booking percentage"
  ☐ Save property

BOOKING CREATION:
  ☐ Click "Create Booking" on property
  ☐ Fill customer details
  ☐ Create booking
  ☐ Open created sale contract
  ☐ Verify "Booking %" field shows correct percentage
  ☐ Generate booking invoices
  ☐ Verify booking invoice amount = Sale Price × Booking %
```

---

## 🚨 Common Questions & Answers

### **Q1: What happens if I change the project's booking percentage?**
**A**: Existing properties with "Use Project Booking %" checked will automatically update to the new percentage. Properties with custom percentages are not affected.

### **Q2: Can I change booking percentage after creating a booking?**
**A**: Yes, you can manually edit the "Booking %" field in the sale contract before generating invoices. After invoices are generated, you should regenerate them to reflect the new percentage.

### **Q3: What's the default booking percentage if no project is assigned?**
**A**: The system defaults to 10% if:
- Property has no project
- Property's custom percentage is 0 or not set
- Project has no booking percentage configured

### **Q4: Can I use fixed booking amounts instead of percentages?**
**A**: Yes! Set "Booking Type" to "Fixed Amount" at project level. However, the current implementation focuses on percentage-based booking. Fixed amount support can be added in future versions.

### **Q5: Does booking percentage affect installment calculations?**
**A**: Yes! The booking amount is deducted from the property price before calculating installments:
```
Remaining Amount = Property Price - Booking Amount
Installments = Split Remaining Amount (not total price)
```

---

## 🎯 Best Practices

### **1. Project-Level Configuration**
✅ **DO**: Set reasonable defaults at project level (e.g., 10-15%)
❌ **DON'T**: Leave project booking percentage at 0%

### **2. Property-Level Overrides**
✅ **DO**: Use custom percentages for special properties (premium units, promotions)
❌ **DON'T**: Override every property (defeats purpose of project defaults)

### **3. Booking Amount Validation**
✅ **DO**: Ensure booking percentage is reasonable (5-30% typical)
❌ **DON'T**: Set extremely high (>50%) or low (<2%) percentages

### **4. Documentation**
✅ **DO**: Document why custom percentages are used for specific properties
❌ **DON'T**: Change percentages frequently without tracking

---

## 🔄 Migration Notes

### **Existing Data Behavior:**
- Existing sale contracts retain their current booking amounts
- Existing properties without projects will use 10% default
- No data loss or recalculation of existing bookings

### **Recommended Actions:**
1. Review all active projects and set appropriate booking percentages
2. Review properties and verify they inherit correct percentages
3. Update any properties needing custom percentages
4. Test booking creation flow on development/staging environment first

---

## 📞 Support & Troubleshooting

### **Issue: Booking percentage not showing**
**Solution**: Ensure property's "Property For" is set to "Sale" (not "Rent")

### **Issue: Cannot change booking percentage**
**Solution**: Check property stage - must be in 'Draft' or 'Available' stage

### **Issue: Booking amount incorrect**
**Solution**: Regenerate invoices after changing booking percentage

### **Issue: Custom percentage not saving**
**Solution**: Uncheck "Use Project Booking %" first, then enter custom value

---

**Module**: rental_management v3.4.1  
**Feature**: Configurable Booking Percentage  
**Date**: December 2, 2025  
**Status**: ✅ Implemented and ready for deployment
