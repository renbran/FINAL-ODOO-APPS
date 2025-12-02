# 🚀 CloudPepper Deployment Guide - Complete Payment Plan

## ✅ **CODE READY FOR DEPLOYMENT**

**Commits**:
- `4b4ef513` - Complete payment plan auto-generation
- `4b1046d5` - Documentation

**Files Changed**:
- `rental_management/models/sale_contract.py` (+240 lines)
- `rental_management/COMPLETE_PAYMENT_PLAN_IMPLEMENTATION.md` (new)

---

## 📦 **DEPLOYMENT STEPS**

### **Option 1: Quick Deploy Script** (RECOMMENDED)

```powershell
# From repository root
.\quick_deploy.ps1 deploy
```

### **Option 2: Manual Deployment**

```powershell
# 1. Connect to server
ssh cloudpepper

# 2. Navigate to module
cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management

# 3. Backup current version
cp models/sale_contract.py models/sale_contract.py.backup_$(date +%Y%m%d_%H%M%S)

# 4. Upload new file (from local machine)
# Open new terminal on local machine:
scp "d:\RUNNING APPS\FINAL-ODOO-APPS\rental_management\models\sale_contract.py" cloudpepper:/var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/models/

# 5. Set correct permissions (back on server)
chown odoo:odoo models/sale_contract.py
chmod 644 models/sale_contract.py

# 6. Upgrade module
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv2 -u rental_management

# 7. Restart Odoo
systemctl restart odoo

# 8. Check logs
tail -f /var/odoo/scholarixv2/logs/odoo-server.log
```

---

## 🧪 **POST-DEPLOYMENT TESTING**

### **Test 1: Create New Contract with Payment Plan**

1. Login to scholarixglobal.com
2. Go to: Sales → Properties → Create
3. Fill in:
   - **Property**: Manta Bay Ras Al Kaimah-404
   - **Customer**: Any customer
   - **Payment Schedule**: "24 Months Installment Plan"
4. **Save** contract
5. **Expected Result**:
   - Contract sequence assigned (PS/2025/12/00XXX)
   - Success notification appears
   - 27 payment lines auto-created
   - Lines visible in "Payment Schedule" tab

### **Test 2: Verify Calculation**

1. Open created contract
2. Go to "Payment Schedule" tab
3. **Check**:
   - Line 1: Booking (120,000 AED)
   - Line 2: DLD (48,000 AED)
   - Line 3: Admin (24,000 AED)
   - Lines 4-27: Installments (45,000 AED each)
   - Total sum: 1,272,000 AED
4. **Verify Math**:
   ```
   Property: 1,200,000 AED
   DLD (4%): 48,000 AED
   Admin (2%): 24,000 AED
   Total: 1,272,000 AED ✓
   
   Installment Balance: 1,200,000 - 120,000 = 1,080,000
   Per Month: 1,080,000 ÷ 24 = 45,000 AED ✓
   ```

### **Test 3: Check Due Dates**

1. In Payment Schedule tab, check "Due Date" column
2. **Expected**:
   - Line 1 (Booking): Contract date (e.g., 2025-12-03)
   - Line 2 (DLD): +1 month (e.g., 2026-01-03)
   - Line 3 (Admin): +2 months (e.g., 2026-02-03)
   - Line 4: +3 months (e.g., 2026-03-03)
   - Line 5: +4 months (e.g., 2026-04-03)
   - etc.

### **Test 4: Smart Buttons**

1. Check top right of form
2. **Expected**:
   - Booking (3) - Shows booking, DLD, admin
   - Installments (24) - Shows 24 installment lines
   - All Invoices (27) - Shows total count

---

## ⚠️ **ROLLBACK PLAN**

If issues occur:

```bash
# 1. Connect to server
ssh cloudpepper

# 2. Navigate to module
cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management

# 3. Find backup
ls -lht models/sale_contract.py.backup_*

# 4. Restore backup (use most recent timestamp)
cp models/sale_contract.py.backup_YYYYMMDD_HHMMSS models/sale_contract.py

# 5. Upgrade module
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -d scholarixv2 -u rental_management

# 6. Restart Odoo
systemctl restart odoo
```

---

## 📊 **MONITORING**

### **Check for Errors**:
```bash
# Real-time log monitoring
ssh cloudpepper "tail -f /var/odoo/scholarixv2/logs/odoo-server.log | grep -i 'rental_management\|payment\|ERROR'"

# Check for Python errors
ssh cloudpepper "grep -i 'traceback\|error' /var/odoo/scholarixv2/logs/odoo-server.log | grep -i rental_management | tail -20"
```

### **Verify Module Upgraded**:
```bash
# Check module version
ssh cloudpepper "grep 'version' /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/rental_management/__manifest__.py"

# Expected: '3.5.0' or higher
```

---

## ✅ **SUCCESS CRITERIA**

Deployment is successful when:
- [ ] No Python errors in logs
- [ ] Module upgrade completes without errors
- [ ] Odoo service starts successfully
- [ ] New contracts auto-generate payment lines
- [ ] 27 lines created for 24-month plan property
- [ ] Calculations are correct (see Test 2)
- [ ] Due dates follow payment schedule
- [ ] Smart buttons show correct counts
- [ ] No user-reported issues

---

## 🆘 **SUPPORT**

If issues occur:

1. **Check logs first**:
   ```bash
   ssh cloudpepper "tail -100 /var/odoo/scholarixv2/logs/odoo-server.log"
   ```

2. **Common Issues**:
   - **Syntax Error**: Restore backup and check file encoding
   - **Import Error**: Ensure all dependencies installed
   - **No lines generated**: Check payment schedule configuration
   - **Wrong calculations**: Verify property fees configuration

3. **Contact**: Development team with:
   - Error message from logs
   - Contract sequence number
   - Property name
   - Payment schedule name
   - Screenshot of issue

---

## 📅 **DEPLOYMENT SCHEDULE**

**Recommended Timeline**:
1. **Stage 1**: Deploy to staging environment (Day 1)
2. **Stage 2**: Test with real data (Days 2-3)
3. **Stage 3**: User acceptance testing (Days 4-5)
4. **Stage 4**: Production deployment (Day 6)
5. **Stage 5**: Monitor for 48 hours (Days 6-8)

**Recommended Time**: Off-peak hours (e.g., 2 AM - 6 AM UAE time)

---

## 📞 **DEPLOYMENT CHECKLIST**

Before deploying:
- [ ] Code reviewed and tested locally
- [ ] Backup current production file
- [ ] Database backup taken
- [ ] Users notified of deployment
- [ ] Rollback plan ready
- [ ] Test environment validated

During deployment:
- [ ] Upload files successfully
- [ ] Module upgrade completed
- [ ] Odoo restarted
- [ ] Logs checked for errors
- [ ] Basic smoke test passed

After deployment:
- [ ] Create test contract
- [ ] Verify payment lines generated
- [ ] Check calculations correct
- [ ] Test with different payment schedules
- [ ] Monitor for 24 hours
- [ ] Collect user feedback

---

**Prepared By**: AI Development Assistant  
**Date**: December 3, 2025  
**Version**: 3.6.0  
**Status**: ✅ Ready for Deployment
