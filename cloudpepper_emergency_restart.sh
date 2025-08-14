#!/bin/bash
# CloudPepper Emergency Restart Script

echo "=== CloudPepper Emergency Restart ==="
echo "Timestamp: $(date)"

# 1. Stop Odoo service
echo "Stopping Odoo service..."
sudo systemctl stop odoo

# 2. Clear all caches
echo "Clearing caches..."
rm -rf /tmp/odoo_*
rm -rf /var/odoo/osustst/sessions/*
rm -rf /var/odoo/osustst/filestore/osustst/assets/*

# 3. Clear Python cache
echo "Clearing Python cache..."
find /var/odoo -name "*.pyc" -delete
find /var/odoo -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 4. Apply database fixes
echo "Applying database fixes..."
sudo -u postgres psql osustst < cloudpepper_autovacuum_fix.sql
python3 cloudpepper_datetime_fix.py

# 5. Restart PostgreSQL
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql

# 6. Start Odoo with asset regeneration
echo "Starting Odoo with asset regeneration..."
sudo systemctl start odoo

# 7. Monitor startup
echo "Monitoring Odoo startup..."
sleep 10
sudo systemctl status odoo

echo "=== Emergency restart complete ==="
echo "Please check logs: sudo journalctl -u odoo -f"
