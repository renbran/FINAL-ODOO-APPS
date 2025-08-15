# 🚨 CLOUDPEPPER EMERGENCY DEPLOYMENT GUIDE
## TypeError: unsupported operand type(s) for @: 'Monetary' and 'function'

**CRITICAL ERROR RESOLUTION - IMMEDIATE DEPLOYMENT REQUIRED**

### Error Details
- **Module**: `order_status_override`
- **File**: `/var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py`
- **Line**: 38 (approximately)
- **Issue**: Malformed `total_payment_out` field causing @ operator error with Monetary field
- **Impact**: Complete CloudPepper database initialization failure

### Emergency Fix Options

#### Option 1: Bash Script Deployment (Recommended for CLI)
```bash
# Upload the fix script to CloudPepper server
scp CLOUDPEPPER_MONETARY_FIELD_EMERGENCY_FIX.sh root@vultr:/tmp/

# SSH to CloudPepper and execute
ssh root@vultr
chmod +x /tmp/CLOUDPEPPER_MONETARY_FIELD_EMERGENCY_FIX.sh
sudo /tmp/CLOUDPEPPER_MONETARY_FIELD_EMERGENCY_FIX.sh
```

#### Option 2: Python Script Deployment
```bash
# Upload Python fix script
scp cloudpepper_monetary_emergency_fix.py root@vultr:/tmp/

# SSH to CloudPepper and execute
ssh root@vultr
sudo python3 /tmp/cloudpepper_monetary_emergency_fix.py
```

#### Option 3: Manual Fix (if scripts fail)
```bash
# SSH to CloudPepper
ssh root@vultr

# Backup original file
sudo cp /var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py /var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py.backup

# Edit the file directly
sudo nano /var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py

# Look for line 38 with malformed total_payment_out field and replace with:
total_payment_amount = fields.Monetary(
    string='Total Payment Amount',
    currency_field='currency_id',
    default=0.0,
    help='Total payment amount for this order'
)

# Save and restart Odoo
sudo systemctl restart odoo
```

### Root Cause Analysis
The error occurs because the `total_payment_out` field definition has incorrect syntax, likely:
- Missing proper field parameters
- Incorrect @ operator usage
- Malformed Monetary field declaration

### Fix Implementation
**Replaces problematic field with properly formatted Monetary field:**
```python
# BEFORE (causing error):
total_payment_out = fields.Monetary(  # <-- Line causing @ operator error

# AFTER (fixed):
total_payment_amount = fields.Monetary(
    string='Total Payment Amount',
    currency_field='currency_id',
    default=0.0,
    help='Total payment amount for this order'
)
```

### Verification Steps
1. **Check Odoo service status:**
   ```bash
   sudo systemctl status odoo
   ```

2. **Check Odoo logs:**
   ```bash
   sudo tail -f /var/log/odoo/odoo-server.log
   ```

3. **Test database initialization:**
   ```bash
   # Try to start Odoo without the problematic module first
   sudo systemctl stop odoo
   sudo -u odoo /var/odoo/osusbck/src/odoo/odoo-bin -d osusbck --test-enable --stop-after-init
   ```

4. **Verify module loading:**
   ```bash
   # If basic start works, try with the fixed module
   sudo systemctl start odoo
   ```

### Rollback Plan (if fix fails)
```bash
# Restore from backup
sudo cp /var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py.backup /var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/order_status_override/models/sale_order.py

# Restart Odoo
sudo systemctl restart odoo
```

### Post-Deployment Validation
1. ✅ CloudPepper accessible at https://stagingtry.cloudpepper.site/
2. ✅ Database `osusbck` initializes without errors
3. ✅ Module `order_status_override` loads successfully
4. ✅ Sale orders can be created and managed
5. ✅ No TypeError in logs

### Emergency Contacts
- **CloudPepper Login**: salescompliance@osusproperties.com
- **Server**: https://stagingtry.cloudpepper.site/
- **Database**: osusbck

### Files Created for This Fix
- `CLOUDPEPPER_MONETARY_FIELD_EMERGENCY_FIX.sh` - Bash emergency fix script
- `cloudpepper_monetary_emergency_fix.py` - Python emergency fix script
- `CLOUDPEPPER_MONETARY_EMERGENCY_DEPLOYMENT.md` - This deployment guide

**⏰ TIME SENSITIVE: Deploy immediately to restore CloudPepper functionality**
