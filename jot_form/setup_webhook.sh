#!/bin/bash

# JotForm Webhook Setup Script
# This script sets up the Python environment and installs dependencies for the JotForm webhook

echo "🚀 Setting up JotForm Webhook Environment..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"

# Check if we're in a Docker container or have access to apt
if command -v apt &> /dev/null; then
    echo "🔍 Detected apt package manager (Debian/Ubuntu system)"
    
    # Update package list
    echo "📦 Updating package list..."
    apt update
    
    # Install system packages for Python dependencies
    echo "🔧 Installing system packages..."
    apt install -y python3-flask python3-requests python3-gunicorn python3-dotenv
    
    echo "✅ System packages installed successfully!"
    
elif command -v pip3 &> /dev/null; then
    echo "🔍 Using pip3 with --break-system-packages flag..."
    
    # Try installing with --break-system-packages flag
    pip3 install --break-system-packages -r requirements.txt
    
    echo "✅ Python packages installed successfully!"
    
else
    echo "❌ Neither apt nor pip3 found. Manual installation required."
    echo "📋 Required packages:"
    cat requirements.txt
    exit 1
fi

echo ""
echo "🎉 JotForm Webhook Environment Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure your .env file with proper settings"
echo "2. Run the webhook server: python3 jotform_odoo_webhook.py"
echo "3. Or use enhanced version: python3 enhanced_webhook.py"
echo ""

# Make the Python files executable
chmod +x *.py

# Show current environment status
echo "🔍 Environment Status:"
python3 -c "import flask, requests, gunicorn; print('✅ All required packages are available')" 2>/dev/null || echo "❌ Some packages may be missing"
