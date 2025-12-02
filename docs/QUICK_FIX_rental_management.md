# 🚨 QUICK FIX SUMMARY: rental_management Dependency Error

**Date**: November 30, 2025  
**Error**: `Field "ai_enrichment_report" does not exist in model "crm.lead"`  
**Status**: ✅ **FIXED**

---

## The Problem

```
ParseError in rental_management/views/property_crm_lead_inherit_view.xml
Field "ai_enrichment_report" does not exist in model "crm.lead"
```

---

## The Solution

Added dependency on `crm_ai_field_compatibility` module in `rental_management/__manifest__.py`

### What Was Changed

**File**: `rental_management/__manifest__.py`

```python
"depends": [
    "mail",
    "contacts",
    "account",
    "hr",
    "maintenance",
    "crm",
    "crm_ai_field_compatibility",  # ← NEW: Provides ai_enrichment_report field
    "website",
    "base",
    "web",
],
```

---

## Deployment (Choose One)

### ⚡ Option 1: Automated (Recommended)

```powershell
# Run from repository root
.\deploy_rental_emergency_fix.ps1
```

**What it does**:
1. Installs `crm_ai_field_compatibility` module
2. Restarts Odoo
3. Uploads updated `rental_management` manifest
4. Upgrades `rental_management` module
5. Restarts Odoo again
6. Verifies deployment

---

### 🔧 Option 2: Manual Steps

```bash
# 1. SSH to CloudPepper
ssh user@scholarixglobal.com

# 2. Install compatibility module
odoo -d scholarixv2 -i crm_ai_field_compatibility --stop-after-init

# 3. Restart Odoo
sudo systemctl restart odoo

# 4. Upload updated manifest (from your local machine)
# scp rental_management/__manifest__.py user@server:/path/to/rental_management/

# 5. Upgrade rental_management
odoo -d scholarixv2 -u rental_management --stop-after-init

# 6. Restart Odoo again
sudo systemctl restart odoo

# 7. Check logs
tail -f /var/log/odoo/odoo.log | grep -i error
```

---

### 🌐 Option 3: Via Odoo UI

1. **Settings** → **Apps** → Remove "Apps" filter
2. Search: **crm_ai_field_compatibility**
3. Click **Install**
4. Wait for installation
5. Search: **rental_management**
6. Click **Upgrade**
7. Wait for upgrade
8. Test CRM lead form

---

## Verification Steps

After deployment, test these:

✅ **CRM Lead Form**
- Navigate to: CRM → Leads → Any lead
- Check "Property Details" tab loads
- No console errors

✅ **Property Sales**
- Create property sale contract
- Generate payment schedule
- Print SPA report
- All features work

✅ **No Errors in Logs**
```bash
tail -n 100 /var/log/odoo/odoo.log | grep -i "error\|rental"
```

---

## Why This Happened

The `rental_management` module inherits from CRM lead views. The parent CRM view includes a reference to `ai_enrichment_report` field (from `llm_lead_scoring` module). When the field doesn't exist, Odoo's XML parser throws a ParseError.

**The Fix**: Add `crm_ai_field_compatibility` module dependency, which provides the field as a compatibility layer.

---

## Documentation

📄 **Full Details**: `EMERGENCY_FIX_rental_management_dependency.md`  
📋 **Deployment Script**: `deploy_rental_emergency_fix.ps1`  
📖 **User Guide**: `rental_management/SALES_OFFER_PAYMENT_PLAN_QUICK_GUIDE.md`  
🔍 **Production Audit**: `rental_management/RENTAL_MANAGEMENT_PRODUCTION_AUDIT.md`

---

## Rollback (If Needed)

```bash
# Remove dependency from manifest
# Restore original __manifest__.py (without crm_ai_field_compatibility)
# Uninstall rental_management
odoo -d scholarixv2 --uninstall rental_management --stop-after-init

# Restore from backup if needed
sudo systemctl stop odoo
pg_restore -U odoo_user -d scholarixv2 /backup/scholarixv2.sql
sudo systemctl start odoo
```

---

## Impact Assessment

✅ **Low Risk Fix**
- Adds one lightweight dependency
- No data migration required
- No existing functionality affected
- Compatibility module already tested

⏱️ **Deployment Time**: 5-10 minutes  
🔄 **Downtime**: ~30 seconds (Odoo restarts)  
💾 **Database Changes**: Minimal (one computed field)

---

## Success Confirmation

You'll know the fix worked when:

1. ✅ No ParseError during upgrade
2. ✅ rental_management shows "Installed" status
3. ✅ CRM lead form loads without errors
4. ✅ Property details tab displays correctly
5. ✅ Payment schedule generation works
6. ✅ SPA report prints successfully

---

**Status**: ✅ **READY TO DEPLOY**  
**Priority**: **HIGH** (Production blocker)  
**Tested**: ✅ Code validated, deployment script ready

---

*For questions or issues, check EMERGENCY_FIX_rental_management_dependency.md*
