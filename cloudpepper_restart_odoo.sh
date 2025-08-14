#!/bin/bash
# CloudPepper Odoo Restart with Asset Regeneration

echo "=== CloudPepper Odoo Restart ==="
echo "Timestamp: $(date)"

# Stop Odoo
echo "Stopping Odoo..."
if command -v docker-compose &> /dev/null; then
    docker-compose stop odoo
elif systemctl is-active --quiet odoo; then
    sudo systemctl stop odoo
else
    echo "Odoo service not found - manual stop required"
fi

# Clear asset caches
echo "Clearing asset caches..."
rm -rf /tmp/odoo_assets_* 2>/dev/null || true
rm -rf /var/odoo/*/filestore/*/assets/* 2>/dev/null || true

# Clear Python cache
echo "Clearing Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Start Odoo with asset regeneration
echo "Starting Odoo..."
if command -v docker-compose &> /dev/null; then
    docker-compose start odoo
    echo "Waiting for Odoo to start..."
    sleep 30
    echo "Forcing asset regeneration..."
    docker-compose exec odoo odoo-bin --dev=reload --stop-after-init -d $(docker-compose exec db psql -U odoo -l | grep odoo | head -1 | awk '{print $1}')
    docker-compose restart odoo
elif systemctl is-active --quiet odoo; then
    sudo systemctl start odoo
else
    echo "Please start Odoo manually"
fi

echo "=== Restart complete ==="
echo "Check logs: docker-compose logs -f odoo OR journalctl -u odoo -f"
