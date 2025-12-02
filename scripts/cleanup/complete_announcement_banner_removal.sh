#!/bin/bash
# Complete removal of announcement_banner module

echo "=== Checking module and data entries ==="
sudo -u odoo psql -d scholarixv2 <<EOF
SELECT id, name, state FROM ir_module_module WHERE id=1413;
SELECT id, module, name, res_id FROM ir_model_data WHERE name='module_announcement_banner';
EOF

echo ""
echo "=== Removing announcement_banner completely ==="
sudo -u odoo psql -d scholarixv2 <<EOF
-- First delete the module record
DELETE FROM ir_module_module WHERE id=1413 OR name='announcement_banner';

-- Then delete all related ir_model_data entries
DELETE FROM ir_model_data WHERE name='module_announcement_banner';
DELETE FROM ir_model_data WHERE module='announcement_banner';
DELETE FROM ir_model_data WHERE res_id=1413 AND model='ir.module.module';

-- Clean up any module dependencies
DELETE FROM ir_module_module_dependency WHERE name='announcement_banner';
EOF

echo ""
echo "=== Verification ==="
sudo -u odoo psql -d scholarixv2 <<EOF
SELECT COUNT(*) as remaining_entries 
FROM ir_model_data 
WHERE name LIKE '%announcement_banner%' OR module='announcement_banner';

SELECT COUNT(*) as remaining_modules
FROM ir_module_module 
WHERE name='announcement_banner';
EOF

echo ""
echo "✅ Complete cleanup done!"
