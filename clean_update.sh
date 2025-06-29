#!/bin/bash

# Define your Odoo instance path
ODOO_BASE="/var/odoo/osus-properties"
ODOO_CONF="$ODOO_BASE/odoo.conf"
ODOO_SRC="$ODOO_BASE/src"
ODOO_PY="$ODOO_BASE/venv/bin/python3"

echo "🔁 Deleting __pycache__ directories..."
find "$ODOO_SRC" -type d -name "__pycache__" -exec rm -rf {} +

echo "✅ __pycache__ cleaned."

echo "🔄 Updating all modules..."
cd "$ODOO_BASE" && sudo -u odoo $ODOO_PY src/odoo-bin -c "$ODOO_CONF" --no-http --stop-after-init --update all

echo "✅ Modules updated successfully."

# Optional: Restart Odoo service (uncomment if managed by systemd)
# echo "🔁 Restarting Odoo service..."
# sudo systemctl restart odoo

echo "🚀 All done!"
