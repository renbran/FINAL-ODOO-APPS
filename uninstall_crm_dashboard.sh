#!/bin/bash
# Uninstall crm_executive_dashboard module from scholarixv2

echo "=== Step 1: Mark module for removal in database ==="
psql -U odoo -d scholarixv2 -c "UPDATE ir_module_module SET state='to remove' WHERE name='crm_executive_dashboard';"

echo "=== Step 2: Run Odoo to process uninstallation ==="
cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init

echo "=== Step 3: Clean up residual data ==="
psql -U odoo -d scholarixv2 <<EOF
-- Remove menu items
DELETE FROM ir_ui_menu WHERE name LIKE '%Executive Dashboard%' OR name LIKE '%crm_executive%';

-- Remove views
DELETE FROM ir_ui_view WHERE name LIKE '%crm_executive%';

-- Remove actions
DELETE FROM ir_actions_act_window WHERE name LIKE '%Executive Dashboard%' OR res_model LIKE '%crm_executive%';
DELETE FROM ir_actions_server WHERE name LIKE '%crm_executive%';

-- Remove model access rights
DELETE FROM ir_model_access WHERE name LIKE '%crm_executive%';

-- Remove security groups if any
DELETE FROM res_groups WHERE name LIKE '%Executive Dashboard%';

-- Remove any scheduled actions
DELETE FROM ir_cron WHERE name LIKE '%crm_executive%';

-- Verify module is uninstalled
SELECT name, state FROM ir_module_module WHERE name='crm_executive_dashboard';
EOF

echo "=== Uninstallation complete ==="
