#!/bin/bash
# Enhanced REST API Installation Script - Fixed for Odoo 17
# Fixes compatibility issues and installs required dependencies

echo "🚀 Enhanced REST API for Odoo 17 - Installation Script (Fixed)"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -d "enhanced_rest_api" ]; then
    echo "❌ Error: enhanced_rest_api module not found in current directory"
    echo "Please run this script from the directory containing the enhanced_rest_api folder"
    exit 1
fi

echo "✅ Found enhanced_rest_api module"

# Update odoo.conf
echo "📝 Updating odoo.conf..."
if [ -f "odoo.conf" ]; then
    # Create backup
    cp odoo.conf odoo.conf.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Created backup of odoo.conf"
    
    # Check if server_wide_modules already exists
    if grep -q "server_wide_modules" odoo.conf; then
        # Update existing line
        sed -i 's/^server_wide_modules.*/server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api/' odoo.conf
        echo "✅ Updated existing server_wide_modules line"
    else
        # Add new line
        echo "server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api" >> odoo.conf
        echo "✅ Added server_wide_modules line"
    fi
else
    echo "⚠️  odoo.conf not found in current directory"
    echo "Please manually add this line to your odoo.conf:"
    echo "server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."

# Function to install pip package
install_pip_package() {
    local package=$1
    echo "   Installing $package..."
    
    # Try different pip commands
    if command -v pip3 &> /dev/null; then
        pip3 install "$package" --quiet
    elif command -v pip &> /dev/null; then
        pip install "$package" --quiet
    else
        echo "   ⚠️  pip not found, please install manually: pip install $package"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "   ✅ $package installed successfully"
    else
        echo "   ⚠️  Failed to install $package, please install manually"
    fi
}

# Install required packages
install_pip_package "PyJWT"
install_pip_package "requests"
install_pip_package "qrcode[pil]"
install_pip_package "Pillow"

# Set file permissions
echo "🔒 Setting file permissions..."
chmod -R 644 enhanced_rest_api/
find enhanced_rest_api/ -type d -exec chmod 755 {} \;
echo "✅ File permissions set"

# Check for Odoo service
echo "🔄 Checking Odoo service..."
if systemctl is-active --quiet odoo; then
    echo "ℹ️  Odoo service is running"
    echo "📋 Next step: Restart Odoo service with: sudo systemctl restart odoo"
elif command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "ℹ️  Docker Compose found"
    echo "📋 Next step: Restart Odoo with: docker-compose restart odoo"
else
    echo "ℹ️  No Odoo service found"
    echo "📋 Next step: Restart your Odoo server manually"
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
echo "- Payment Voucher API: enhanced_rest_api/PAYMENT_VOUCHER_API.md"
echo "- API Documentation: Available after installation"
echo ""
echo "🔗 API Endpoints will be available at:"
echo "- Health Check: http://your-domain.com/api/v1/status"
echo "- Generate API Key: http://your-domain.com/api/v1/auth/generate-key"
echo "- CRM APIs: http://your-domain.com/api/v1/crm/*"
echo "- Sales APIs: http://your-domain.com/api/v1/sales/*"
echo "- Payment APIs: http://your-domain.com/api/v1/payments/*"
echo "- Payment Vouchers: http://your-domain.com/api/v1/payments/voucher/*"
echo ""
echo "⚡ Enjoy your enhanced REST API experience!"
