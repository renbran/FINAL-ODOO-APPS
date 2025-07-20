#!/bin/bash

echo "🔧 Starting Odoo with module upgrade for hide_menu_user..."

# Start only the database first
docker-compose up -d db

echo "⏳ Waiting for database to be ready..."
sleep 10

# Run Odoo with upgrade for the problematic module
docker-compose run --rm odoo odoo -d osusre -u hide_menu_user --stop-after-init

if [ $? -eq 0 ]; then
    echo "✅ Module upgrade completed successfully"
    echo "🚀 Starting Odoo normally..."
    docker-compose up -d
else
    echo "❌ Module upgrade failed, trying to start normally..."
    docker-compose up -d
fi

echo "🌐 Odoo should be available at http://localhost:8069/web?db=osusre"
