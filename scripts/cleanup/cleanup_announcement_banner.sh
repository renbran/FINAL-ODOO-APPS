#!/bin/bash
# Clean up announcement_banner module from database

sudo -u odoo psql -d scholarixv2 <<EOF
DELETE FROM ir_model_data WHERE module='announcement_banner';
DELETE FROM ir_module_module WHERE name='announcement_banner';
EOF

echo "Cleanup complete"
