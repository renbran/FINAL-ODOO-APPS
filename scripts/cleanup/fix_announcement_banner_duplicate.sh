#!/bin/bash
# Fix announcement_banner duplicate key constraint

echo "=== Checking announcement_banner entries ==="
sudo -u odoo psql -d scholarixv2 <<EOF
SELECT id, module, name, model, res_id 
FROM ir_model_data 
WHERE name LIKE '%announcement_banner%' 
ORDER BY id;
EOF

echo ""
echo "=== Deleting duplicate entries ==="
sudo -u odoo psql -d scholarixv2 <<EOF
-- Keep only the first entry, delete duplicates
DELETE FROM ir_model_data 
WHERE id IN (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY module, name ORDER BY id) as rn
        FROM ir_model_data
        WHERE name = 'module_announcement_banner'
    ) t WHERE rn > 1
);

-- Also delete all announcement_banner module entries
DELETE FROM ir_model_data WHERE module='announcement_banner';
DELETE FROM ir_module_module WHERE name='announcement_banner';
EOF

echo ""
echo "=== Verification - remaining entries ==="
sudo -u odoo psql -d scholarixv2 <<EOF
SELECT id, module, name, model, res_id 
FROM ir_model_data 
WHERE name LIKE '%announcement_banner%';
EOF

echo ""
echo "✅ Cleanup complete!"
