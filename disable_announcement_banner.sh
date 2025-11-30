#!/bin/bash
# Check and fix announcement_banner entries that keep reappearing

echo "=== Current state ==="
sudo -u odoo psql -d scholarixv2 -c "SELECT id, module, name, res_id FROM ir_model_data WHERE name='module_announcement_banner' ORDER BY id;"

echo ""
echo "=== Deleting ALL entries ==="
sudo -u odoo psql -d scholarixv2 -c "DELETE FROM ir_model_data WHERE name='module_announcement_banner';"

echo ""
echo "=== Checking filesystem for announcement_banner ==="
find /var/odoo/scholarixv2 -type d -name "announcement_banner" 2>/dev/null

echo ""
echo "=== Renaming announcement_banner directory to prevent re-detection ==="
for dir in $(find /var/odoo/scholarixv2 -type d -name "announcement_banner" 2>/dev/null); do
    if [ -d "$dir" ]; then
        mv "$dir" "${dir}_disabled"
        echo "Renamed: $dir -> ${dir}_disabled"
    fi
done

echo ""
echo "✅ Done!"
