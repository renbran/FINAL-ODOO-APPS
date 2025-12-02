#!/bin/bash
# Complete fix for rental_management module

echo "=== Step 1: Clear view cache ==="
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
-- Remove cached arch for property.details views
UPDATE ir_ui_view SET arch_db = NULL WHERE model = 'property.details';
-- Clear any asset caches
DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';
EOSQL

echo ""
echo "=== Step 2: Update module ==="
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -u rental_management 2>&1 | grep -E "ERROR|error|loaded|Stopping" | tail -10

echo ""
echo "=== Step 3: Restart Odoo ==="
systemctl restart odoo
sleep 8

echo ""
echo "=== Step 4: Verify Odoo status ==="
systemctl status odoo --no-pager | head -8

echo ""
echo "=== DONE ==="
