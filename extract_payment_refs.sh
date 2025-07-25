#!/bin/bash
# Extract Payment References Script
echo "Starting payment reference extraction from journal entries..."
echo "=================================================="

# Run the extraction script in Odoo shell
docker-compose exec odoo odoo shell -d odoo --shell-interface ipython <<EOF
# Load the script and run it
exec(open('/mnt/extra-addons/extract_payment_refs.py').read())
EOF

echo "=================================================="
echo "Payment reference extraction completed!"
echo "Check the output above for results."
