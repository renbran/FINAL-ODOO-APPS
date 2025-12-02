# 🚀 Quick Start Guide - Invoice Tracking & Payment Management

## For Property Sales Team

### Step-by-Step: Creating a Sales Contract with Proper Invoice Tracking

---

## 📋 Step 1: Create Sales Contract (Draft Stage)

1. **Create Property Sale Contract**
   - Go to: Property → Sales Contracts → Create
   - Select property (must be in 'sale' stage)
   - Fill customer details
   - Configure pricing

2. **Configure Booking & Fees**
   - Set **Booking Amount** (percentage or fixed)
   - Set **DLD Fee** (4% of sale price - auto-calculated or manual)
   - Set **Admin Fee** (fixed amount)
   - Configure due dates for DLD and Admin fees

3. **Save the Contract**
   - Stage: Draft - Awaiting Booking Payment
   - Status bar shows workflow progress

---

## 💳 Step 2: Create Booking Invoices

### Click Button: `📋 Create Booking Invoices`

**What happens:**
- System creates 3 invoices automatically:
  1. **Booking Payment** - Due immediately
  2. **DLD Fee** - Due after X days (configurable)
  3. **Admin Fee** - Due after Y days (configurable)

**You will see:**
- Success notification with invoice details
- Alert box showing payment monitoring
- Progress bar at 0%

**What to do next:**
- Review generated invoices in "Invoices & Payments" tab
- Share invoice details with customer
- Create accounting invoices for each payment

---

## 📊 Step 3: Monitor Booking Payments

### Use the Smart Buttons:
- **📋 Booking (3)** - View booking-related invoices
- Shows real-time count of booking invoices

### Watch the Progress:
```
⏳ Awaiting Booking Payments
Progress: [████░░░░░░] 33%

• Booking Payment: ✓ Paid (50,000 AED)
• DLD Fee: ✗ Pending (80,000 AED)
• Admin Fee: ✗ Pending (20,000 AED)
```

### How to Mark as Paid:
1. Click on an invoice in the list
2. Click `📋 Create Invoice` button
3. System creates accounting invoice (account.move)
4. Register payment in Accounting module
5. Status auto-updates to "Paid" ✅

**Tip:** Use the **Payment Dashboard** at the top to see overall progress!

---

## ✅ Step 4: Confirm Booking Complete

### When all 3 payments are received:

**You will see:**
```
💳 Booking Requirements Status
┌─────────────────────────────────────┐
│ ✓ Booking Payment: Paid ✅         │
│ ✓ DLD Fee: Paid ✅                 │
│ ✓ Admin Fee: Paid ✅               │
│                                     │
│ Progress: [██████████] 100%        │
│ ✓ Ready to create installment plan │
└─────────────────────────────────────┘
```

**Click Button:** `✓ Confirm Booking Complete`

**What happens:**
- Contract moves from "Draft" to "Booked" stage
- System validates all payments are received
- Ready for installment creation

---

## 💰 Step 5: Create Installment Plan

### Three Options:

#### **Option A: Automatic (Recommended)**
**Click:** `💰 Create Installment Plan`
- Uses configured payment schedule
- Auto-generates invoices based on template
- Calculates due dates automatically

#### **Option B: Payment Schedule**
**Click:** `⚡ Generate from Schedule`
- Requires payment schedule selection
- Follows UAE payment plan structure
- Professional SPA-compliant invoicing

#### **Option C: Manual**
**Click:** `📝 Manual Installments`
- Opens wizard for manual input
- Full control over amounts and dates
- Flexible for custom arrangements

**What you get:**
- Complete installment invoice list
- Scheduled due dates
- Ready to share with customer

---

## 📈 Step 6: Monitor Overall Progress

### Payment Progress Dashboard:
```
💰 Payment Progress Overview
┌────────────────────────────────────────────┐
│ Overall Progress:    [████████░░] 80%     │
│ Paid: 400,000 / 500,000 AED               │
│                                            │
│ Installment Progress: [███████░░░] 70%    │
│ Outstanding: 100,000 AED                   │
└────────────────────────────────────────────┘

Statistics:
Total Invoices: 15 | Created: 15 | Paid: 12 | Pending: 3
```

### Smart Button Tracking:
- **📅 Installments (12)** - View installment invoices
- **📄 All Invoices (15)** - Complete invoice list
- **📚 Created (15)** - Accounting invoices
- **✅ Paid (12)** - Fully paid invoices

---

## 🎯 Step 7: Create Accounting Invoices

### For Each Installment Due:

1. **Go to "Invoices & Payments" tab**
2. **Find unpaid invoice in list**
3. **Click:** `📋 Create Invoice` button
4. **System generates** account.move invoice
5. **Share invoice** with customer
6. **Register payment** when received

**Invoice List Color Coding:**
- 🟢 **Green Row** = Paid
- 🟠 **Orange Row** = Partially Paid
- ⚪ **Gray Row** = Not Created Yet

---

## 🏆 Step 8: Complete Sale

### When All Payments Received:

**You will see:**
```
Overall Progress: [██████████] 100%
Paid: 500,000 / 500,000 AED
Outstanding: 0 AED ✅
```

**Click Button:** `Confirm Sale`

**What happens:**
- Contract moves to "Sold" stage
- Property ownership transferred
- Generate final reports (SPA, Sales Offer)

---

## 🔍 Quick Reference: Smart Buttons

| Button | What It Shows | When to Use |
|--------|---------------|-------------|
| 📋 **Booking** | Booking, DLD, Admin invoices | Check booking payment status |
| 📅 **Installments** | Property installment invoices | Monitor installment payments |
| 📄 **All Invoices** | Complete invoice list | Full overview of all payments |
| 📚 **Created** | Accounting invoices | Check what's in accounting system |
| ✅ **Paid** | Fully paid invoices | See successful payments |

---

## 💡 Tips & Best Practices

### ✅ DO:
- Create booking invoices immediately after contract creation
- Monitor payment progress regularly using dashboard
- Use payment schedules for consistent invoicing
- Update payment status promptly in accounting
- Generate invoices before due dates

### ❌ DON'T:
- Skip booking payment confirmation
- Create installments before booking completion
- Delete invoices without resetting (use Reset button)
- Manually edit generated invoice amounts
- Change property details after booking confirmed

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Cannot create installments yet"
**Reason:** Booking requirements not fully paid
**Solution:** 
1. Check booking payment progress (should be 100%)
2. Verify all 3 invoices are paid (Booking + DLD + Admin)
3. Click "Confirm Booking Complete" when ready

### Issue 2: "Booking invoices already exist"
**Reason:** Trying to recreate existing invoices
**Solution:** 
1. View existing invoices via smart button
2. Delete manually if regeneration needed
3. Or use "Reset Installments" for clean slate

### Issue 3: Progress bar not updating
**Reason:** Payments not registered in accounting
**Solution:**
1. Create accounting invoice (account.move)
2. Register payment in Accounting module
3. Status will auto-update

### Issue 4: Can't see smart buttons
**Reason:** No invoices created yet
**Solution:**
1. First create booking invoices
2. Smart buttons appear automatically
3. Counts update in real-time

---

## 📞 Need Help?

### Quick Actions:
- **View Documentation:** `INVOICE_TRACKING_ENHANCEMENT.md`
- **Payment Plan Guide:** `PAYMENT_PLAN_SOLUTION_PACKAGE.md`
- **Production Audit:** `RENTAL_MANAGEMENT_PRODUCTION_AUDIT.md`

### Support Contacts:
- Technical Issues: Development Team
- Process Questions: Sales Manager
- Accounting Issues: Finance Department

---

## 🎓 Training Checklist

Before using the system, ensure you can:
- [ ] Create a sales contract
- [ ] Generate booking invoices
- [ ] Monitor payment progress
- [ ] Confirm booking completion
- [ ] Create installment plans
- [ ] Use smart buttons for tracking
- [ ] Create accounting invoices
- [ ] Register payments
- [ ] Read payment dashboard
- [ ] Handle common issues

---

**Version:** 3.5.0
**Last Updated:** December 3, 2025
**Module:** rental_management

---

## 🌟 Remember:

> **The system is designed to guide you step-by-step. Follow the workflow, use the visual indicators, and let the smart buttons help you track everything!**

**Workflow Summary:**
```
Draft → Create Booking Invoices → Monitor Payments → 
Confirm Booking → Create Installments → Monitor Progress → 
Confirm Sale ✅
```

Happy Selling! 🏡💰
