#!/bin/bash
# CloudPepper Asset Cleanup Script

echo "Cleaning asset bundles..."

# Remove compiled assets
rm -rf /var/odoo/osustst/filestore/osustst/assets/*
rm -rf /tmp/odoo_assets_*

# Clear browser cache headers
echo "Clearing asset cache..."

# Restart Odoo to regenerate assets
echo "Restarting Odoo service..."
sudo systemctl restart odoo

echo "Asset cleanup complete"
