#!/bin/bash

# OSUS Odoo 17 Docker Setup Script
# This script helps you set up and manage your Odoo 17 environment with custom modules

set -e

echo "🚀 OSUS Odoo 17 Docker Setup"
echo "=================================="

# Function to display menu
show_menu() {
    echo ""
    echo "Choose an option:"
    echo "1. Build and start Odoo (first time setup)"
    echo "2. Start existing containers"
    echo "3. Stop containers"
    echo "4. View logs"
    echo "5. Reset database (WARNING: This will delete all data)"
    echo "6. Update modules"
    echo "7. Backup database"
    echo "8. Restore database"
    echo "9. Exit"
    echo ""
}

# Function to build and start Odoo
build_and_start() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    
    echo "🚀 Starting services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    echo "✅ Services started successfully!"
    echo "🌐 Odoo is available at: http://localhost:8069"
    echo "🗄️  Database: PostgreSQL on localhost:5432"
    echo ""
    echo "📋 Default credentials:"
    echo "   Database: odoo"
    echo "   Username: admin"
    echo "   Password: admin"
}

# Function to start existing containers
start_containers() {
    echo "▶️  Starting existing containers..."
    docker-compose up -d
    echo "✅ Containers started!"
    echo "🌐 Odoo is available at: http://localhost:8069"
}

# Function to stop containers
stop_containers() {
    echo "⏹️  Stopping containers..."
    docker-compose down
    echo "✅ Containers stopped!"
}

# Function to view logs
view_logs() {
    echo "📋 Viewing Odoo logs (Press Ctrl+C to exit)..."
    docker-compose logs -f odoo
}

# Function to reset database
reset_database() {
    echo "⚠️  WARNING: This will delete ALL data!"
    read -p "Are you sure you want to reset the database? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        echo "🗑️  Stopping containers..."
        docker-compose down
        
        echo "🗑️  Removing database volume..."
        docker volume rm odoo17_final_odoo-db-data 2>/dev/null || echo "Volume already removed"
        
        echo "🚀 Starting fresh containers..."
        docker-compose up -d
        
        echo "✅ Database reset complete!"
    else
        echo "❌ Database reset cancelled."
    fi
}

# Function to update modules
update_modules() {
    echo "🔄 Updating Odoo modules..."
    docker-compose exec odoo odoo --update=all --stop-after-init
    docker-compose restart odoo
    echo "✅ Modules updated!"
}

# Function to backup database
backup_database() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_${timestamp}.sql"
    
    echo "💾 Creating database backup..."
    docker-compose exec db pg_dump -U odoo odoo > "$backup_file"
    echo "✅ Database backed up to: $backup_file"
}

# Function to restore database
restore_database() {
    echo "📋 Available backup files:"
    ls -la backup_*.sql 2>/dev/null || echo "No backup files found"
    echo ""
    read -p "Enter backup file name: " backup_file
    
    if [ -f "$backup_file" ]; then
        echo "📥 Restoring database from: $backup_file"
        docker-compose exec -T db psql -U odoo -d odoo < "$backup_file"
        docker-compose restart odoo
        echo "✅ Database restored successfully!"
    else
        echo "❌ Backup file not found: $backup_file"
    fi
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-9): " choice
    
    case $choice in
        1)
            build_and_start
            ;;
        2)
            start_containers
            ;;
        3)
            stop_containers
            ;;
        4)
            view_logs
            ;;
        5)
            reset_database
            ;;
        6)
            update_modules
            ;;
        7)
            backup_database
            ;;
        8)
            restore_database
            ;;
        9)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-9."
            ;;
    esac
done
