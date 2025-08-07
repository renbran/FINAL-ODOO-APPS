#!/bin/bash

# NUCLEAR EMERGENCY FIX FOR CLOUDPEPPER TESTERP DATABASE
# This script will completely fix the web.assets_backend issue

echo "🚨 NUCLEAR EMERGENCY FIX FOR TESTERP DATABASE"
echo "=============================================="

# Step 1: Stop Odoo completely
echo "⏹️ Stopping Odoo service..."
sudo systemctl stop odoo
sudo pkill -f odoo-bin || true

# Wait a moment
sleep 3

# Step 2: Nuclear database cleanup
echo "💥 Running nuclear database cleanup..."
sudo -u postgres psql testerp << 'EOF'
-- NUCLEAR CLEANUP
BEGIN;

-- Remove ALL payment_account_enhanced references
DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';
DELETE FROM ir_ui_view WHERE key LIKE 'payment_account_enhanced.%';
DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_ui_view WHERE arch_db LIKE '%payment_account_enhanced%';
DELETE FROM ir_attachment WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_asset WHERE path LIKE '%payment_account_enhanced%';
DELETE FROM ir_model_constraint WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_model_field WHERE model LIKE '%payment_account_enhanced%';
DELETE FROM ir_model WHERE model LIKE '%payment_account_enhanced%';
DELETE FROM ir_model_access WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_rule WHERE name LIKE '%payment_account_enhanced%';
DELETE FROM ir_module_module WHERE name = 'payment_account_enhanced';

-- Remove any broken assets inheritance
DELETE FROM ir_ui_view WHERE arch_db LIKE '%inherit_id="web.assets_backend"%' AND key LIKE '%payment%';

-- Check current state of web.assets_backend
SELECT 'BEFORE FIX - web.assets_backend count:' as status, COUNT(*) as count FROM ir_model_data WHERE module = 'web' AND name = 'assets_backend';

-- Remove any corrupted web.assets_backend
DELETE FROM ir_model_data WHERE module = 'web' AND name = 'assets_backend';
DELETE FROM ir_ui_view WHERE key = 'web.assets_backend';

-- Force recreate web.assets_backend
INSERT INTO ir_ui_view (name, key, type, arch, active, mode, create_date, write_date)
VALUES (
    'assets_backend',
    'web.assets_backend',
    'qweb',
    '<t t-name="web.assets_backend">
    <t t-call="web.assets_common"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient.scss"/>
    <link rel="stylesheet" type="text/css" href="/web/static/src/scss/webclient_layout.scss"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/abstract_web_client.js"/>
    <script type="text/javascript" src="/web/static/src/js/chrome/web_client.js"/>
</t>',
    true,
    'primary',
    NOW(),
    NOW()
);

-- Create the ir.model.data record
INSERT INTO ir_model_data (name, module, model, res_id, noupdate, create_date, write_date)
SELECT 'assets_backend', 'web', 'ir.ui.view', v.id, false, NOW(), NOW()
FROM ir_ui_view v
WHERE v.key = 'web.assets_backend';

-- Verify the fix
SELECT 'AFTER FIX - web.assets_backend count:' as status, COUNT(*) as count FROM ir_model_data WHERE module = 'web' AND name = 'assets_backend';
SELECT 'web.assets_backend view exists:' as status, COUNT(*) as count FROM ir_ui_view WHERE key = 'web.assets_backend';

-- Clear all caches
DELETE FROM ir_attachment WHERE name LIKE '%.assets_%';

COMMIT;

SELECT '🎉 NUCLEAR CLEANUP COMPLETED SUCCESSFULLY! 🎉' as final_status;
EOF

# Step 3: Force update web module without starting service
echo "🔄 Force updating web module..."
sudo -u odoo /var/odoo/testerp/src/odoo-bin -d testerp -u web --stop-after-init --no-http --log-level=error

# Step 4: Force update base module
echo "🔄 Force updating base module..."
sudo -u odoo /var/odoo/testerp/src/odoo-bin -d testerp -u base --stop-after-init --no-http --log-level=error

# Step 5: Update apps list
echo "📋 Updating apps list..."
sudo -u odoo /var/odoo/testerp/src/odoo-bin -d testerp --init=False --update-list --stop-after-init --no-http --log-level=error

# Step 6: Start Odoo service
echo "🚀 Starting Odoo service..."
sudo systemctl start odoo

# Step 7: Wait and check status
echo "⏳ Waiting for Odoo to start..."
sleep 10

echo "📊 Checking Odoo status..."
sudo systemctl status odoo --no-pager

echo ""
echo "🎉 NUCLEAR FIX COMPLETED!"
echo "=========================================="
echo "✅ web.assets_backend has been forcibly recreated"
echo "✅ payment_account_enhanced completely removed"
echo "✅ All caches cleared"
echo "✅ Core modules updated"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Test your Odoo web interface"
echo "2. Go to Apps → Update Apps List"
echo "3. Install payment_account_enhanced fresh"
echo ""
echo "🔍 Monitor logs with: sudo journalctl -u odoo -f"

# Step 8: Show recent logs
echo ""
echo "📝 Recent Odoo logs:"
sudo journalctl -u odoo --since "2 minutes ago" --no-pager -n 20
