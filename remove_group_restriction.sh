#!/bin/bash
# Remove groups_id restriction from commission report

FILE="/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/enhanced_status/reports/commission_report_template.xml"

# Create backup
cp "$FILE" "${FILE}.backup"

# Remove the groups_id line
sed -i '/<field name="groups_id"/d' "$FILE"

echo "Removed groups_id restriction"
echo "Verifying:"
grep -n "groups_id" "$FILE" || echo "No groups_id found - SUCCESS"
