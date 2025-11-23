# 🚨 CloudPepper Emergency Deployment Fix
## llm_lead_scoring - Security Groups Error Resolution

**Date**: November 23, 2025  
**Issue**: RPC_ERROR - Module installation failed due to deprecated security groups  
**Status**: ✅ **LOCAL FILES FIXED - CLOUDPEPPER NEEDS UPDATE**

---

## 🔍 Problem Analysis

### Error Message
```
Exception: Module loading llm_lead_scoring failed: file llm_lead_scoring/security/ir.model.access.csv could not be processed:
 No matching record found for external id 'crm.group_crm_user' in field 'Group'
 No matching record found for external id 'crm.group_crm_manager' in field 'Group'
```

### Root Cause
The **CloudPepper server** has an **old version** of the `ir.model.access.csv` file that uses **deprecated Odoo 17 security groups**:
- ❌ `crm.group_crm_user` (deprecated)
- ❌ `crm.group_crm_manager` (deprecated)

These groups were **removed in Odoo 17** and replaced with:
- ✅ `sales_team.group_sale_salesman` (correct)
- ✅ `sales_team.group_sale_manager` (correct)

### Current Status
- ✅ **Local repository**: Files already fixed with correct groups
- ❌ **CloudPepper server**: Still has old version with deprecated groups

---

## 🛠️ Solution: Update CloudPepper Server

### Option 1: Git Pull + Module Upgrade (RECOMMENDED)

This is the **cleanest and most reliable** method:

```bash
# SSH into CloudPepper server
ssh user@scholarixglobal.com

# Navigate to addons directory
cd /var/odoo/scholarixv2/addons

# Pull latest changes from repository
git pull origin main

# Verify the security file is updated
cat llm_lead_scoring/security/ir.model.access.csv

# Should see:
# access_llm_provider_user,llm.provider.user,model_llm_provider,sales_team.group_sale_salesman,1,0,0,0
# access_llm_provider_manager,llm.provider.manager,model_llm_provider,sales_team.group_sale_manager,1,1,1,1
# access_llm_service_user,llm.service.user,model_llm_service,sales_team.group_sale_salesman,1,0,0,0
# access_lead_enrichment_wizard_user,lead.enrichment.wizard.user,model_lead_enrichment_wizard,sales_team.group_sale_salesman,1,1,1,1

# Upgrade the module
./odoo-bin -d scholarixv2 -u llm_lead_scoring --stop-after-init

# Restart Odoo
sudo systemctl restart odoo

# Verify Odoo is running
sudo systemctl status odoo
```

### Option 2: Manual File Upload

If you can't use Git:

1. **Upload Fixed File**
   ```bash
   # From your local machine
   scp "d:\RUNNING APPS\ready production\odoo17_final.git-6880b7fcd4844\FINAL-ODOO-APPS\llm_lead_scoring\security\ir.model.access.csv" user@scholarixglobal.com:/var/odoo/scholarixv2/addons/llm_lead_scoring/security/
   ```

2. **SSH and Upgrade**
   ```bash
   ssh user@scholarixglobal.com
   cd /var/odoo/scholarixv2
   ./odoo-bin -d scholarixv2 -u llm_lead_scoring --stop-after-init
   sudo systemctl restart odoo
   ```

### Option 3: Direct Edit on Server

If you have shell access:

```bash
# SSH into server
ssh user@scholarixglobal.com

# Navigate to security directory
cd /var/odoo/scholarixv2/addons/llm_lead_scoring/security

# Backup original file
cp ir.model.access.csv ir.model.access.csv.backup

# Edit the file
nano ir.model.access.csv

# Replace all instances:
# crm.group_crm_user → sales_team.group_sale_salesman
# crm.group_crm_manager → sales_team.group_sale_manager

# Save and exit (Ctrl+X, Y, Enter)

# Verify changes
cat ir.model.access.csv

# Upgrade module
cd /var/odoo/scholarixv2
./odoo-bin -d scholarixv2 -u llm_lead_scoring --stop-after-init
sudo systemctl restart odoo
```

### Option 4: Web UI Upgrade (After Files Updated)

Once files are updated on the server:

1. Login to https://scholarixglobal.com/
2. Go to **Apps** → **Update Apps List**
3. Search for **"LLM Lead Scoring"**
4. Click **"Upgrade"** button
5. Wait for upgrade to complete
6. Verify module is installed successfully

---

## 📄 Correct File Content

### security/ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_llm_provider_user,llm.provider.user,model_llm_provider,sales_team.group_sale_salesman,1,0,0,0
access_llm_provider_manager,llm.provider.manager,model_llm_provider,sales_team.group_sale_manager,1,1,1,1
access_llm_service_user,llm.service.user,model_llm_service,sales_team.group_sale_salesman,1,0,0,0
access_lead_enrichment_wizard_user,lead.enrichment.wizard.user,model_lead_enrichment_wizard,sales_team.group_sale_salesman,1,1,1,1
```

**Key Changes**:
- Row 2: `crm.group_crm_user` → `sales_team.group_sale_salesman`
- Row 3: `crm.group_crm_manager` → `sales_team.group_sale_manager`
- Row 4: `crm.group_crm_user` → `sales_team.group_sale_salesman`
- Row 5: `crm.group_crm_user` → `sales_team.group_sale_salesman`

---

## ✅ Verification Steps

After updating and upgrading the module:

### 1. Check Module Status
```bash
# SSH into server
ssh user@scholarixglobal.com

# Check module installation
cd /var/odoo/scholarixv2
./odoo-bin shell -d scholarixv2

>>> module = env['ir.module.module'].search([('name', '=', 'llm_lead_scoring')])
>>> print(f"State: {module.state}")
>>> print(f"Latest Version: {module.latest_version}")
>>> print(f"Installed Version: {module.installed_version}")
>>> exit()
```

Expected output:
```
State: installed
Latest Version: 17.0.1.0.0
Installed Version: 17.0.1.0.0
```

### 2. Check Access Rights
```bash
./odoo-bin shell -d scholarixv2

>>> access = env['ir.model.access'].search([('model_id.model', '=', 'llm.provider')])
>>> for a in access:
...     print(f"{a.name}: {a.group_id.full_name}")
...
>>> exit()
```

Expected output:
```
llm.provider.user: Sales / User: All Documents
llm.provider.manager: Sales / Administrator
```

### 3. Web UI Verification

1. Login to https://scholarixglobal.com/
2. Go to **Apps**
3. Search for **"LLM Lead Scoring"**
4. Status should show **"Installed"** ✅
5. Go to **CRM** → should see LLM features available
6. Try creating/editing a lead → no errors

### 4. Check Logs
```bash
# Check Odoo logs for errors
tail -f /var/log/odoo/odoo.log | grep -i "llm_lead_scoring\|error\|warning"

# Should see successful installation messages
```

---

## 🚨 Troubleshooting

### Issue 1: "Module not found" after upgrade

**Solution**:
```bash
# Update module list
./odoo-bin -d scholarixv2 --update-module-list
sudo systemctl restart odoo
```

### Issue 2: "Permission denied" errors

**Solution**:
```bash
# Fix file permissions
sudo chown -R odoo:odoo /var/odoo/scholarixv2/addons/llm_lead_scoring
sudo chmod -R 755 /var/odoo/scholarixv2/addons/llm_lead_scoring
```

### Issue 3: Module upgrade fails with different error

**Solution**:
```bash
# Uninstall and reinstall
./odoo-bin shell -d scholarixv2
>>> module = env['ir.module.module'].search([('name', '=', 'llm_lead_scoring')])
>>> module.button_immediate_uninstall()
>>> env.cr.commit()
>>> exit()

# Clear cache
rm -rf ~/.local/share/Odoo/sessions/*
rm -rf ~/.local/share/Odoo/filestore/scholarixv2/*

# Reinstall
./odoo-bin -d scholarixv2 -i llm_lead_scoring --stop-after-init
sudo systemctl restart odoo
```

### Issue 4: Still seeing old security groups

**Solution**:
```bash
# Force update security rules
./odoo-bin shell -d scholarixv2
>>> env['ir.model.access'].search([('model_id.model', '=', 'llm.provider')]).unlink()
>>> env.cr.commit()
>>> exit()

# Reload security data
./odoo-bin -d scholarixv2 -u llm_lead_scoring --stop-after-init
sudo systemctl restart odoo
```

---

## 📊 Deployment Checklist

Before deployment:
- [x] Local files verified with correct security groups
- [x] Emergency fix script created and tested
- [x] Deployment instructions documented
- [x] Rollback procedure prepared

During deployment:
- [ ] SSH access to CloudPepper server confirmed
- [ ] Backup created of current files
- [ ] Files updated via Git pull or manual upload
- [ ] Module upgraded via command line
- [ ] Odoo service restarted
- [ ] No errors in logs

After deployment:
- [ ] Module status verified (installed)
- [ ] Access rights verified (correct groups)
- [ ] Web UI tested (no errors)
- [ ] CRM features accessible
- [ ] Lead enrichment tested
- [ ] User permissions confirmed

---

## 🔄 Rollback Procedure

If something goes wrong:

```bash
# SSH into server
ssh user@scholarixglobal.com

# Restore backup
cd /var/odoo/scholarixv2/addons/llm_lead_scoring/security
cp ir.model.access.csv.backup ir.model.access.csv

# Uninstall module
cd /var/odoo/scholarixv2
./odoo-bin shell -d scholarixv2
>>> module = env['ir.module.module'].search([('name', '=', 'llm_lead_scoring')])
>>> module.button_immediate_uninstall()
>>> env.cr.commit()
>>> exit()

# Restart Odoo
sudo systemctl restart odoo

# Note: This will uninstall the module but preserve data
```

---

## 📞 Support

If you need assistance:

1. **Check Logs**: `tail -f /var/log/odoo/odoo.log`
2. **Odoo Shell**: `./odoo-bin shell -d scholarixv2`
3. **Service Status**: `sudo systemctl status odoo`
4. **Module Status**: Check in Apps menu

**Common Commands**:
```bash
# Restart Odoo
sudo systemctl restart odoo

# Check Odoo status
sudo systemctl status odoo

# View logs
tail -100 /var/log/odoo/odoo.log

# Check Python errors
journalctl -u odoo -n 100
```

---

## ✅ Success Criteria

Deployment is successful when:

1. ✅ Module installs without errors
2. ✅ No "group_crm_user" or "group_crm_manager" errors
3. ✅ Access rights use "sales_team.group_sale_*" groups
4. ✅ CRM features accessible in web UI
5. ✅ Lead enrichment wizard works
6. ✅ LLM provider configuration accessible
7. ✅ No errors in Odoo logs

---

## 🎯 Next Steps After Fix

Once the module is successfully installed:

1. **Configure LLM Providers**
   - Go to Settings → Technical → LLM Providers
   - Add OpenAI, Groq, or HuggingFace provider
   - Set API keys

2. **Enable Auto-Enrichment**
   - Settings → CRM → LLM Lead Scoring
   - Enable auto-enrichment features
   - Configure scoring weights

3. **Test with Sample Lead**
   - Create a test lead in CRM
   - Click "Enrich with AI" button
   - Verify AI scoring works

4. **Train Users**
   - Show sales team the AI features
   - Demonstrate lead probability scoring
   - Explain enrichment data

---

## 📚 Related Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [README_PRODUCTION_READY.md](./README_PRODUCTION_READY.md) - Feature documentation
- [PRODUCTION_READY_SUMMARY.md](./PRODUCTION_READY_SUMMARY.md) - Validation results

---

*Emergency Fix Guide Version: 1.0*  
*Last Updated: November 23, 2025*  
*Status: Ready for CloudPepper Deployment*  
*Priority: CRITICAL - Module Installation Blocked*
