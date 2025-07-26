# 🚀 Payment Account Enhanced - Production Deployment Guide

## 📁 Server Environment Configuration

**Production Server Paths:**
- **Base Directory**: `/var/odoo/osush/`
- **Odoo Source**: `/var/odoo/osush/src/odoo-bin`
- **Configuration**: `/var/odoo/osush/odoo.conf`
- **Logs Directory**: `/var/odoo/osush/logs/`
- **Extra Addons**: `/var/odoo/osush/extra-addons/`
- **Module Location**: `/var/odoo/osush/extra-addons/payment_account_enhanced/`

## 🎯 Quick Deployment Commands

### Option 1: Automated Deployment Script (Recommended)

```bash
# Make script executable
chmod +x /var/odoo/osush/extra-addons/payment_account_enhanced/deploy_database_fix.sh

# Run deployment script
cd /var/odoo/osush/extra-addons/payment_account_enhanced/
./deploy_database_fix.sh
```

### Option 2: Manual Odoo Shell Fix

```bash
# Navigate to Odoo base directory
cd /var/odoo/osush

# Start Odoo shell
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf

# In shell, execute:
exec(open('/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py').read())
fix_company_fields(env)
exit()
```

### Option 3: Module Update Method

```bash
# Update payment_account_enhanced module
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

# Or update all modules
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update all
```

## 🔧 Available Fix Scripts

### 1. Database Fix Scripts
- **Python Script**: `fix_company_fields.py` - Odoo shell compatible
- **SQL Script**: `fix_company_fields.sql` - Direct PostgreSQL execution
- **Migration Script**: `post-migration.py` - Auto-runs during module update
- **Deployment Script**: `deploy_database_fix.sh` - Automated deployment

### 2. Documentation
- **README**: `DATABASE_FIX_README.md` - Complete troubleshooting guide
- **This Guide**: `DEPLOYMENT_SUMMARY.md` - Quick reference

## ⚡ Emergency Quick Fix

If Odoo won't start due to missing columns:

```bash
# Direct SQL fix (fastest)
sudo -u postgres psql odoo -c "
ALTER TABLE res_company ADD COLUMN IF NOT EXISTS voucher_footer_message TEXT;
ALTER TABLE res_company ADD COLUMN IF NOT EXISTS voucher_terms TEXT;
ALTER TABLE res_company ADD COLUMN IF NOT EXISTS use_osus_branding BOOLEAN;

UPDATE res_company SET voucher_footer_message = 'Thank you for your business' WHERE voucher_footer_message IS NULL;
UPDATE res_company SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' WHERE voucher_terms IS NULL;
UPDATE res_company SET use_osus_branding = TRUE WHERE use_osus_branding IS NULL;
"
```

## 🔍 Verification Commands

### Check Database Columns

```bash
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
# In shell:
env.cr.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='res_company' AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding') ORDER BY column_name")
print(env.cr.fetchall())
```

### Monitor Logs

```bash
# Real-time log monitoring
tail -f /var/odoo/osush/logs/odoo.log | grep -E "(ERROR|payment_account_enhanced|res_company)"

# Check recent errors
tail -100 /var/odoo/osush/logs/odoo.log | grep ERROR
```

## 🛡️ Production Safety Steps

### 1. Pre-Deployment Checklist
- [ ] Create database backup
- [ ] Verify all fix scripts are in place
- [ ] Check Odoo service status
- [ ] Confirm user permissions

### 2. Backup Command

```bash
sudo -u postgres pg_dump odoo > /var/odoo/osush/logs/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Service Management

```bash
# Stop Odoo
sudo systemctl stop odoo

# Start Odoo
sudo systemctl start odoo

# Check status
sudo systemctl status odoo

# Restart if needed
sudo systemctl restart odoo
```

## ✅ Success Indicators

After deployment, you should see:

1. **In Logs**: No database column errors
2. **In Shell**: All three columns exist with correct data types
3. **In UI**: Company settings show voucher customization fields
4. **In Reports**: Payment vouchers display with OSUS branding

### Expected Output

```bash
✅ Added voucher_footer_message column
✅ Added voucher_terms column  
✅ Added use_osus_branding column
🎉 Payment account enhanced database fix completed successfully!

Verification - Found columns:
  - use_osus_branding: boolean
  - voucher_footer_message: text
  - voucher_terms: text
```

## 🚨 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Permission denied | Run with `sudo -u odoo` |
| File not found | Check paths match server environment |
| Columns already exist | Verification shows success, no action needed |
| Odoo won't start | Use emergency SQL fix first |
| Service errors | Check `systemctl status odoo` and logs |

### Emergency Contacts

If deployment fails:
1. Check `/var/odoo/osush/logs/odoo.log` for specific errors
2. Restore from backup if needed
3. Use emergency SQL fix for immediate resolution
4. Contact system administrator with error logs

## 📝 Post-Deployment Tasks

1. **Test Module Functionality**
   - Open Company settings
   - Verify voucher customization fields appear
   - Generate a test payment voucher
   - Confirm OSUS branding displays correctly

2. **Monitor System Performance**
   - Watch logs for any new errors
   - Test related modules (accounting, payments)
   - Verify no regression in existing features

3. **Update Documentation**
   - Mark deployment as completed
   - Note any environment-specific adjustments
   - Update team on new functionality

---

**Deployment Summary**: This fix resolves missing database columns for the payment_account_enhanced module by adding three required fields to the res_company table with proper default values and OSUS branding support.
