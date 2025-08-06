#!/bin/bash
"""
Enhanced REST API Installation Script
"""

echo "🚀 Enhanced REST API for Odoo 17 - Installation Script"
echo "====================================================="

# Check if we're in the right directory
if [ ! -f "enhanced_rest_api/__manifest__.py" ]; then
    echo "❌ Error: Please run this script from the odoo17_final directory"
    exit 1
fi

echo "✅ Found enhanced_rest_api module"

# Check if odoo.conf exists
ODOO_CONF="/var/odoo/testerp/odoo.conf"
if [ ! -f "$ODOO_CONF" ]; then
    echo "⚠️  Odoo config file not found at $ODOO_CONF"
    echo "Please update your odoo.conf manually to include:"
    echo "server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api"
else
    echo "📝 Updating odoo.conf..."
    
    # Backup original config
    cp "$ODOO_CONF" "$ODOO_CONF.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Created backup of odoo.conf"
    
    # Check if server_wide_modules line exists
    if grep -q "server_wide_modules" "$ODOO_CONF"; then
        # Update existing line
        sed -i 's/server_wide_modules = .*/server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api/' "$ODOO_CONF"
        echo "✅ Updated existing server_wide_modules line"
    else
        # Add new line after addons_path
        sed -i '/addons_path/a server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api' "$ODOO_CONF"
        echo "✅ Added server_wide_modules line"
    fi
fi

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."

python3 -c "import jwt" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ PyJWT is installed"
else
    echo "⚠️  PyJWT not found. Installing..."
    pip3 install PyJWT
fi

python3 -c "import requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ requests is installed"
else
    echo "⚠️  requests not found. Installing..."
    pip3 install requests
fi

# Set proper permissions
echo ""
echo "🔒 Setting file permissions..."
chmod -R 755 enhanced_rest_api/
echo "✅ File permissions set"

# Check if Odoo service exists
echo ""
echo "🔄 Checking Odoo service..."
if systemctl is-active --quiet odoo; then
    echo "⚠️  Odoo service is running. Restart required after installation."
    echo ""
    echo "To restart Odoo service:"
    echo "sudo systemctl restart odoo"
elif systemctl list-unit-files | grep -q odoo; then
    echo "ℹ️  Odoo service found but not running"
    echo ""
    echo "To start Odoo service:"
    echo "sudo systemctl start odoo"
else
    echo "ℹ️  No Odoo systemd service found"
fi

echo ""
echo "🎉 Enhanced REST API Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Restart your Odoo server"
echo "2. Go to Apps > Update Apps List"
echo "3. Search for 'Enhanced REST API'"
echo "4. Install the module"
echo "5. Configure API endpoints in Settings"
echo ""
echo "📚 Documentation:"
echo "- Module README: enhanced_rest_api/README.md"
echo "- API Documentation: Available after installation"
echo ""
echo "🔗 API Endpoints will be available at:"
echo "- Health Check: http://your-domain.com/api/v1/status"
echo "- Generate API Key: http://your-domain.com/api/v1/auth/generate-key"
echo "- CRM APIs: http://your-domain.com/api/v1/crm/*"
echo "- Sales APIs: http://your-domain.com/api/v1/sales/*"
echo "- Payment APIs: http://your-domain.com/api/v1/payments/*"
echo ""
echo "⚡ Enjoy your enhanced REST API experience!"
