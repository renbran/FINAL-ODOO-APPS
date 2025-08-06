#!/bin/bash
"""
Quick Module Installation Script
Installs the Enhanced REST API module via Odoo command line
"""

echo "🚀 Installing Enhanced REST API Module..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "enhanced_rest_api" ]; then
    echo "❌ Error: enhanced_rest_api module not found in current directory"
    echo "Please run this script from the directory containing the enhanced_rest_api folder"
    exit 1
fi

echo "✅ Found enhanced_rest_api module"

# Method 1: Docker installation
if command -v docker-compose &> /dev/null; then
    echo "🐳 Attempting Docker Compose installation..."
    docker-compose exec odoo odoo --update=enhanced_rest_api --stop-after-init
    
    if [ $? -eq 0 ]; then
        echo "✅ Module installed successfully via Docker"
        exit 0
    else
        echo "⚠️  Docker installation failed, trying alternative methods..."
    fi
fi

# Method 2: Direct Odoo installation
if command -v odoo &> /dev/null; then
    echo "🔧 Attempting direct Odoo installation..."
    odoo --update=enhanced_rest_api --stop-after-init
    
    if [ $? -eq 0 ]; then
        echo "✅ Module installed successfully"
        exit 0
    fi
fi

echo "📋 Manual Installation Required:"
echo "1. Access your Odoo interface"
echo "2. Go to Apps > Update Apps List"
echo "3. Search for 'Enhanced REST API'"
echo "4. Click Install"
echo ""
echo "🔗 Odoo URL: https://testerp.cloudpepper.site"
echo "👤 Login with: salescompliance@osusproperties.com"
