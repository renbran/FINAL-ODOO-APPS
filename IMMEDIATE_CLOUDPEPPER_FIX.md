# 🚨 IMMEDIATE ACTION REQUIRED - CloudPepper Emergency Fix

## Your Current Error
```
ValueError: External ID not found in the system: web.assets_backend
```

This is a **CRITICAL ERROR** - your Odoo's core web assets template is missing, which is why you can't install any modules.

## OPTION 1: Quick Manual Fix (Recommended)

### Step 1: SSH into your CloudPepper server
```bash
ssh your-username@your-cloudpepper-server
```

### Step 2: Stop Odoo service
```bash
sudo systemctl stop odoo
```

### Step 3: Connect to PostgreSQL and run emergency SQL cleanup
```bash
sudo -u postgres psql YOUR_DATABASE_NAME
```

Then run these SQL commands:
```sql
-- Clean up payment_account_enhanced completely
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';
DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_ui_view WHERE arch_db LIKE '%inherit_id="web.assets_backend"%' AND key LIKE '%payment_account_enhanced%';
DELETE FROM ir_attachment WHERE name LIKE '%payment_account_enhanced%';

-- Recreate missing web.assets_backend if it doesn't exist
INSERT INTO ir_ui_view (name, key, type, arch, active, mode)
SELECT 'assets_backend', 'web.assets_backend', 'qweb', 
'<t t-name="web.assets_backend">
    <t t-call="web.assets_common"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient.scss"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient_layout.scss"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/abstract_web_client.js"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/web_client.js"/>
</t>', true, 'primary'
WHERE NOT EXISTS (
    SELECT 1 FROM ir_model_data 
    WHERE module = 'web' AND name = 'assets_backend' AND model = 'ir.ui.view'
);

-- Create ir.model.data record for web.assets_backend
INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
SELECT 'assets_backend', 'web', 'ir.ui.view', v.id, false
FROM ir_ui_view v
WHERE v.key = 'web.assets_backend' 
AND NOT EXISTS (
    SELECT 1 FROM ir_model_data 
    WHERE module = 'web' AND name = 'assets_backend' AND model = 'ir.ui.view'
);

-- Exit PostgreSQL
\q
```

### Step 4: Update web module and restart
```bash
# Update web module specifically
sudo -u odoo python3 /opt/odoo/odoo-bin -d YOUR_DATABASE_NAME --update=web --stop-after-init

# Start Odoo service
sudo systemctl start odoo

# Check status
sudo systemctl status odoo
```

## OPTION 2: Automated Script

1. Upload the `cloudpepper_auto_fix.sh` script to your server
2. Make it executable: `chmod +x cloudpepper_auto_fix.sh`
3. Run it: `./cloudpepper_auto_fix.sh`

## OPTION 3: Manual Python Shell Method

If the SQL approach doesn't work:

```bash
# Enter Odoo shell
sudo -u odoo python3 /opt/odoo/odoo-bin shell -d YOUR_DATABASE_NAME
```

Copy and paste this Python code:
```python
# Copy the entire content from cloudpepper_fix_clean.py
```

## Verification Steps

After running any fix:

1. **Check Odoo logs**: `sudo journalctl -u odoo -f`
2. **Access Odoo web interface**: Should load without errors
3. **Go to Apps**: Should be able to access Apps menu
4. **Update Apps List**: Click "Update Apps List"
5. **Install payment_account_enhanced**: Should work without the assets_backend error

## If Still Having Issues

1. **Check database integrity**:
   ```bash
   sudo -u postgres psql YOUR_DATABASE_NAME -c "SELECT * FROM ir_model_data WHERE module = 'web' AND name = 'assets_backend';"
   ```

2. **Verify web.assets_backend exists**:
   ```bash
   sudo -u postgres psql YOUR_DATABASE_NAME -c "SELECT id, key, name FROM ir_ui_view WHERE key = 'web.assets_backend';"
   ```

3. **Complete Odoo restart**:
   ```bash
   sudo systemctl restart odoo
   sudo systemctl status odoo
   ```

## Root Cause Analysis

This error occurred because:
1. The nuclear cleanup scripts deleted core Odoo assets
2. `web.assets_backend` is a fundamental template required for all web functionality
3. Without it, no modules can inherit from web assets, causing installation failures

## Prevention

- Always backup database before running cleanup scripts
- Test in staging environment first
- Avoid nuclear cleanup of core Odoo components

---

**Choose OPTION 1 for immediate results. Let me know which option you'll use and if you need help with any specific step!**
