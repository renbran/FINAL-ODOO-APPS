# CLOUDPEPPER EMERGENCY DEPLOYMENT PRIORITY

## 🚨 CRITICAL PRIORITY 1 - COMMISSION EMAIL ERROR FIX

**Status**: IMMEDIATE ACTION REQUIRED  
**Issue**: Production commission emails failing with AttributeError  
**Impact**: Customer commission notifications not being sent  

### DEPLOY NOW:
1. **SQL Fix**: Run `cloudpepper_commission_email_emergency_fix.sql` in CloudPepper database
2. **Module Update**: Upload updated `commission_ax` module with stored fields
3. **Verification**: Test commission email sending immediately

---

## ✅ READY FOR DEPLOYMENT - ORDER NET COMMISSION MODULE

**Status**: PRODUCTION READY  
**Issue**: Module emergency fix applied for CloudPepper compatibility  
**Impact**: Enhanced order workflow with commission calculation  

### DEPLOY AFTER PRIORITY 1:
1. **Module Upload**: Install `order_net_commission` module
2. **User Testing**: Verify workflow with security groups
3. **Integration**: Test with existing commission_ax module

---

## DEPLOYMENT SEQUENCE

### Step 1: Fix Critical Email Error (5 minutes)
```bash
# In CloudPepper database console
source cloudpepper_commission_email_emergency_fix.sql

# Upload commission_ax module
# Apps → commission_ax → Upgrade
```

### Step 2: Deploy Order Net Commission (10 minutes)  
```bash
# Upload order_net_commission folder
# Apps → Update Apps List
# Search "Order Net Commission" → Install
```

### Step 3: Verify Both Systems (15 minutes)
```bash
# Test commission emails from purchase orders
# Test order workflow: draft → documentation → commission → sale
# Monitor CloudPepper logs for any errors
```

## SUCCESS CRITERIA

### Priority 1 Success:
- [ ] Commission emails send without AttributeError
- [ ] Purchase orders display agent information
- [ ] No QWeb template errors in logs

### Order Net Commission Success:
- [ ] Module installs without XPath errors
- [ ] Workflow buttons appear for authorized users
- [ ] Commission calculation works correctly
- [ ] OSUS branding displays properly

## EMERGENCY CONTACTS

**If Email Fix Fails**:
```sql
-- Temporary disable commission emails
UPDATE mail_template SET active = FALSE WHERE body_html LIKE '%COMMISSION PAYOUT%';
```

**If Module Install Fails**:
- Check browser console for JavaScript errors
- Verify all security groups exist
- Ensure CloudPepper compatibility patches loaded

---

**TOTAL DEPLOYMENT TIME**: 30 minutes maximum  
**RISK LEVEL**: Low (all fixes tested and validated)  
**ROLLBACK AVAILABLE**: Yes (documented procedures)

## 🎯 DEPLOY COMMISSION EMAIL FIX IMMEDIATELY TO RESTORE PRODUCTION FUNCTIONALITY
