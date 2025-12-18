# UAE Payment Plan Templates - Quick Setup Guide

## 🎯 CREATE THESE 4 TEMPLATES IN ODOO

**Location**: Configuration → Payment Schedules  
**Time**: 45 minutes total  
**Result**: Reusable payment plans for all projects

---

## TEMPLATE 1️⃣: Off-Plan Milestones

### Create New Record
```
Name: 40% Booking + 60% Milestones (Dubai Standard)
Description: Off-plan development with construction milestones
Schedule Type: Sale
Active: Yes
```

### Payment Lines
```
Line 1: Booking Payment
├─ Percentage: 40%
├─ Days After: 0
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Initial booking deposit

Line 2: Foundation/Structural Work
├─ Percentage: 15%
├─ Days After: 180
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Completion of structural foundation

Line 3: MEP Installation Complete
├─ Percentage: 15%
├─ Days After: 360
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Mechanical, Electrical, Plumbing systems installed

Line 4: Interior Finishes
├─ Percentage: 20%
├─ Days After: 540
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Interior painting, fixtures, flooring complete

Line 5: Handover Ready
├─ Percentage: 10%
├─ Days After: 720
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Final payment upon handover

✅ Total: 40+15+15+20+10 = 100% ✓
```

---

## TEMPLATE 2️⃣: Ready Quarterly

### Create New Record
```
Name: 30% Booking + 70% Quarterly (Ready Property)
Description: Ready/completed property with quarterly payments
Schedule Type: Sale
Active: Yes
```

### Payment Lines
```
Line 1: Booking Payment
├─ Percentage: 30%
├─ Days After: 0
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Initial booking for ready property

Line 2: Quarterly Installments
├─ Percentage: 70%
├─ Days After: 30
├─ Frequency: Quarterly (90 days)
├─ Installments: 4
└─ Notes: 4 quarterly payments (30, 120, 210, 300 days)

✅ Total: 30+70 = 100% ✓
```

**Result**: 5 invoices (1 booking + 4 quarterly)

---

## TEMPLATE 3️⃣: Luxury Semi-Annual

### Create New Record
```
Name: 25% Booking + 75% Semi-Annual (Luxury Segment)
Description: Luxury properties with flexible payment timeline
Schedule Type: Sale
Active: Yes
```

### Payment Lines
```
Line 1: Booking Payment
├─ Percentage: 25%
├─ Days After: 0
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Booking payment for luxury property

Line 2: Semi-Annual Installments
├─ Percentage: 75%
├─ Days After: 180
├─ Frequency: Semi-Annual (180 days)
├─ Installments: 2
└─ Notes: 2 payments at 6-month intervals

✅ Total: 25+75 = 100% ✓
```

**Result**: 3 invoices (1 booking + 2 semi-annual)

---

## TEMPLATE 4️⃣: Affordable Monthly

### Create New Record
```
Name: 35% Booking + 65% Monthly (Affordable Housing)
Description: Affordable housing with monthly payment plan
Schedule Type: Sale
Active: Yes
```

### Payment Lines
```
Line 1: Booking Payment
├─ Percentage: 35%
├─ Days After: 0
├─ Frequency: One Time
├─ Installments: 1
└─ Notes: Initial booking deposit

Line 2: Monthly Installments
├─ Percentage: 65%
├─ Days After: 0
├─ Frequency: Monthly (30 days)
├─ Installments: 12
└─ Notes: 12 monthly payments (Days 0, 30, 60... 330)

✅ Total: 35+65 = 100% ✓
```

**Result**: 13 invoices (1 booking + 12 monthly)

---

## 📋 VERIFICATION CHECKLIST

### After Creating All 4 Templates

- [ ] Template 1 shows in dropdown
- [ ] Template 2 shows in dropdown
- [ ] Template 3 shows in dropdown
- [ ] Template 4 shows in dropdown
- [ ] Each has "Total Percentage = 100%"
- [ ] No errors when saving
- [ ] All templates marked "Active"

### Test Generation (Quick Validation)

**Test Each Template**:
```
For Each Template:
1. Create test Property Vendor
2. Sale Price: AED 1,000,000
3. Select template
4. Click "⚡ Generate from Schedule"
5. Verify invoice count:
   ├─ Template 1: 7 invoices (5 + DLD + Admin)
   ├─ Template 2: 7 invoices (5 + DLD + Admin)
   ├─ Template 3: 5 invoices (3 + DLD + Admin)
   └─ Template 4: 15 invoices (13 + DLD + Admin)
6. Verify amounts: Booking % of 1M, etc.
```

---

## 🎯 HOW TO USE IN PRODUCTION

### For Off-Plan Projects
```
Step 1: Identify property as "off-plan"
Step 2: Open Property Vendor form
Step 3: Select: "40% Booking + 60% Milestones"
Step 4: Click "Generate from Schedule"
Step 5: Done! 7 invoices created automatically
```

### For Ready Properties
```
Step 1: Identify property as "ready/completed"
Step 2: Open Property Vendor form
Step 3: Select: "30% Booking + 70% Quarterly"
Step 4: Click "Generate from Schedule"
Step 5: Done! 7 invoices created automatically
```

### For Luxury Properties
```
Step 1: Identify property as "luxury" (>AED 2M)
Step 2: Open Property Vendor form
Step 3: Select: "25% Booking + 75% Semi-Annual"
Step 4: Click "Generate from Schedule"
Step 5: Done! 5 invoices created automatically
```

### For Affordable Housing
```
Step 1: Identify property as "affordable" (<AED 800K)
Step 2: Open Property Vendor form
Step 3: Select: "35% Booking + 65% Monthly"
Step 4: Click "Generate from Schedule"
Step 5: Done! 15 invoices created automatically
```

---

## 💡 PRO TIPS

**Tip 1**: Use consistent naming across all templates  
→ All start with percentage (40%, 30%, 25%, 35%)  
→ All include segment type (Dubai Standard, Ready, Luxury, Affordable)

**Tip 2**: Add descriptions explaining when to use  
→ Sales team knows exactly when to use which

**Tip 3**: Test thoroughly before rollout  
→ Create 5-10 test properties  
→ Verify calculations match expectations

**Tip 4**: Document for your team  
→ Create internal guide: "When to use Template #1, 2, 3, 4"  
→ Share with sales, accounting, operations teams

**Tip 5**: Version your templates  
→ If you need to change percentages later, create v2  
→ Keep v1 for reference (existing contracts)

---

## ⚠️ COMMON MISTAKES TO AVOID

| Mistake | Impact | How to Avoid |
|---------|--------|------------|
| Fixed amounts instead of percentages | Can't reuse across price ranges | Always use percentages |
| Forgetting DLD fee | Invoice mismatch | Enable in sale contract settings |
| Different terminology per template | Customer confusion | Standardize names |
| Not testing before rollout | Errors in production | Test 5-10 properties first |
| Creating too many templates | Confusion, hard to maintain | Stick to 4 master templates |

---

## ✅ SUCCESS CRITERIA

**You're done when**:
- [ ] 4 templates created and active
- [ ] Each template tested with 1-2 properties
- [ ] Invoices generated with correct amounts
- [ ] Invoices show correct payment dates
- [ ] DLD and Admin fees included
- [ ] Sales team trained on which to use
- [ ] First real property successfully processed

**Time Investment**: 2-4 hours (one-time setup)  
**Time Saved Per Property**: 25 minutes (5 minutes instead of 30)  
**Break-even**: 6 properties (~3 hours saved)

---

## 📞 QUESTIONS?

**Q: Can I change the percentages later?**  
A: Yes, create a new version (v2). Keep old version for historical reference.

**Q: What if my company needs different percentages?**  
A: Create your own template based on these 4 as starting points.

**Q: Can I use different templates for the same project?**  
A: Yes! Use Template #1 for phase 1 (off-plan), Template #2 for phase 2 (ready).

**Q: How many templates should I create?**  
A: Start with these 4. Add more only if you have specific market segments that don't fit.

**Q: Can I copy a template?**  
A: Yes, create new record, manually enter lines (or ask admin to copy via database).

---

## 🚀 NEXT STEPS

1. **Today** (30 min):
   - Identify which template matches your primary business
   - Get manager approval to proceed

2. **Tomorrow** (45 min):
   - Create 4 master templates in Odoo
   - Take screenshots for documentation

3. **This Week** (2 hours):
   - Test each template with real properties
   - Verify all calculations correct
   - Train sales team (15 min presentation)

4. **Next Week**:
   - Start using for all new properties
   - Monitor for 2 weeks
   - Collect feedback

---

**Ready to implement?**  
Start with Template #1 (Off-Plan Milestones) - it's the most commonly used! 🎯

**Setup Time**: ~45 minutes  
**Usage Time Per Property**: ~2 minutes  
**Professional Result**: ✅ Excellent
