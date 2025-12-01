#!/bin/bash
# Clear ALL caches
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
-- Clear asset bundles
DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';
-- Clear QWeb templates cache  
DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view';
-- Clear the model data cache
DELETE FROM ir_model_data WHERE model = 'ir.model.fields' AND name LIKE '%total_customer_obligation%';
EOSQL

# Restart Odoo to rebuild caches
systemctl restart odoo
echo "Caches cleared. Please wait 10 seconds for Odoo to start..."
sleep 10
systemctl status odoo --no-pager | head -5
