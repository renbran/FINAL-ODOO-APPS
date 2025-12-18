#!/bin/bash
# Clear the groups restriction from the commission report in database

# The groups are stored in a many2many table, not directly on the report
# We need to delete from the relation table

sudo -u postgres psql osusproperties << 'EOF'
-- Check current groups
SELECT r.id, r.name, g.name as group_name 
FROM ir_act_report_xml r 
LEFT JOIN res_groups_report_rel rel ON r.id = rel.uid 
LEFT JOIN res_groups g ON rel.gid = g.id
WHERE r.id = 2206;

-- Delete the group relation
DELETE FROM res_groups_report_rel WHERE uid = 2206;

-- Verify
SELECT r.id, r.name, g.name as group_name 
FROM ir_act_report_xml r 
LEFT JOIN res_groups_report_rel rel ON r.id = rel.uid 
LEFT JOIN res_groups g ON rel.gid = g.id
WHERE r.id = 2206;
EOF

echo "Done! Restart Odoo to apply changes."
