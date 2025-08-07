#!/bin/bash
# Quick Docker restart script for Odoo module upgrades

echo "🔄 Restarting Odoo Docker containers..."

# Stop the containers
echo "⏹️  Stopping containers..."
docker-compose down

# Start them again
echo "▶️  Starting containers..."
docker-compose up -d

# Wait for Odoo to be ready
echo "⏳ Waiting for Odoo to start..."
sleep 10

# Show logs
echo "📋 Showing recent logs..."
docker-compose logs -f --tail=50 odoo

echo ""
echo "🎉 Restart complete!"
echo "💡 Now you can:"
echo "   1. Go to http://localhost:8069"
echo "   2. Navigate to Apps → Update Apps List"
echo "   3. Search for 'OSUS Payment Voucher Enhanced'"
echo "   4. Click 'Upgrade' button"
