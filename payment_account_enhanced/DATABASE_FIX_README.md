# Payment Account Enhanced - Database Fix Guide

## Server Environment
- **Base Path**: `/var/odoo/osush/`
- **Source Path**: `/var/odoo/osush/src/`
- **Config File**: `/var/odoo/osush/odoo.conf`
- **Logs Path**: `/var/odoo/osush/logs/`
- **Extra Addons**: `/var/odoo/osush/extra-addons/`

## Problem Description
The `payment_account_enhanced` module defines three new fields in `res.company` model, but the database columns don't exist:
- `voucher_footer_message` (Text)
- `voucher_terms` (Text) 
- `use_osus_branding` (Boolean)

This causes PostgreSQL errors when starting Odoo.

## Solution Methods (Choose One)

### Method 1: Odoo Shell Fix (Recommended)
```bash
# 1. Navigate to Odoo directory
cd /var/odoo/osush

# 2. Start Odoo shell
sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf

# 3. In the shell, load and execute the fix script:
exec(open('/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py').read())
fix_company_fields(env)

# 4. Exit shell
exit()
```

### Method 2: Module Update
```bash
# Update the specific module (will run migration scripts)
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update payment_account_enhanced

# Or update all modules
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update all
```

### Method 3: Direct SQL Fix (Advanced)
```bash
# Connect to PostgreSQL directly
sudo -u postgres psql odoo

# Execute SQL commands:

ALTER TABLE res_company ADD COLUMN voucher_footer_message TEXT;
ALTER TABLE res_company ADD COLUMN voucher_terms TEXT;
ALTER TABLE res_company ADD COLUMN use_osus_branding BOOLEAN;

UPDATE res_company SET voucher_footer_message = 'Thank you for your business' WHERE voucher_footer_message IS NULL;
UPDATE res_company SET voucher_terms = 'This is a computer-generated document. No physical signature or stamp required for system verification.' WHERE voucher_terms IS NULL;
UPDATE res_company SET use_osus_branding = TRUE WHERE use_osus_branding IS NULL;

# Exit PostgreSQL
\q
```

## Verification Commands

### Check Database Columns

```bash
# Connect to Odoo shell
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf

# In shell, check if columns exist:
env.cr.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='res_company' AND column_name IN ('voucher_footer_message', 'voucher_terms', 'use_osus_branding') ORDER BY column_name")
print(env.cr.fetchall())
```

### Test Module Functionality

```bash
# Start Odoo normally and check logs
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf

# Check logs for errors
tail -f /var/odoo/osush/logs/odoo.log
```

## File Locations on Server

- **Fix Script**: `/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py`
- **Migration Script**: `/var/odoo/osush/extra-addons/payment_account_enhanced/post-migration.py`
- **SQL Script**: `/var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.sql`
- **This README**: `/var/odoo/osush/extra-addons/payment_account_enhanced/DATABASE_FIX_README.md`

## Expected Output

When the fix is successful, you should see:

```
✅ Added voucher_footer_message column
✅ Added voucher_terms column  
✅ Added use_osus_branding column
🎉 Payment account enhanced database fix completed successfully!

Verification - Found columns:
  - use_osus_branding: boolean
  - voucher_footer_message: text
  - voucher_terms: text
```

## Troubleshooting

### If Odoo Won't Start

```bash
# Check detailed error logs
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --log-level=debug

# Or check log file
tail -100 /var/odoo/osush/logs/odoo.log
```

### If Columns Already Exist

```bash
# Verify current state
cd /var/odoo/osush && sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf
env.cr.execute("DESCRIBE res_company")  # MySQL
# or
env.cr.execute("\\d res_company")  # PostgreSQL
```

### Permission Issues

```bash
# Ensure odoo user owns the files
sudo chown -R odoo:odoo /var/odoo/osush/extra-addons/payment_account_enhanced/
sudo chmod +x /var/odoo/osush/extra-addons/payment_account_enhanced/fix_company_fields.py
```

## Production Deployment Steps

1. **Backup Database**: Always backup before applying fixes

   ```bash
   sudo -u postgres pg_dump odoo > /var/odoo/osush/logs/backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Stop Odoo Service**:

   ```bash
   sudo systemctl stop odoo
   ```

3. **Apply Fix**: Use Method 1 (Odoo Shell) or Method 2 (Module Update)

4. **Verify Fix**: Check columns exist and no errors in logs

5. **Start Odoo Service**:

   ```bash
   sudo systemctl start odoo
   sudo systemctl status odoo
   ```

6. **Monitor Logs**:

   ```bash
   tail -f /var/odoo/osush/logs/odoo.log
   ```

## Success Criteria

- ✅ No database column errors in logs
- ✅ `payment_account_enhanced` module loads without errors  
- ✅ Company settings show new voucher fields
- ✅ Payment vouchers generate with OSUS branding
- ✅ No impact on existing functionality
