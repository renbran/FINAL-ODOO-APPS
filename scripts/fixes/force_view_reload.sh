#!/bin/bash
# Clear view cache and force reload
cd /var/odoo/scholarixv2
sudo -u postgres psql -d scholarixv2 << 'EOSQL'
-- Clear cached arch_db for the problematic view
UPDATE ir_ui_view SET arch_db = NULL WHERE id = 5106;
-- Also clear asset cache
DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';
EOSQL

# Now upgrade the module
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -u rental_management 2>&1 | tail -15
