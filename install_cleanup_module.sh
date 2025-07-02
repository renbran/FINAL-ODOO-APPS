#!/bin/bash
# Installation Script for Custom Fields Cleanup

echo "======================================"
echo "Custom Fields Cleanup Installation"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "custom_fields_cleanup_module/__manifest__.py" ]; then
    echo "❌ Error: Please run this script from the odoo17_final directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: custom_fields_cleanup_module/__manifest__.py"
    exit 1
fi

# Set default Odoo addons path (update this to match your setup)
ODOO_ADDONS_PATH="${ODOO_ADDONS_PATH:-/var/odoo/addons}"

echo "Using Odoo addons path: $ODOO_ADDONS_PATH"

# Copy the cleanup module
echo "📁 Copying custom_fields_cleanup_module to $ODOO_ADDONS_PATH..."

if [ -w "$ODOO_ADDONS_PATH" ]; then
    cp -r custom_fields_cleanup_module "$ODOO_ADDONS_PATH/"
    echo "✅ Module copied successfully"
else
    echo "⚠️  No write permission to $ODOO_ADDONS_PATH"
    echo "   Please run: sudo cp -r custom_fields_cleanup_module $ODOO_ADDONS_PATH/"
fi

# Set proper permissions
echo "🔧 Setting proper permissions..."
if [ -d "$ODOO_ADDONS_PATH/custom_fields_cleanup_module" ]; then
    sudo chown -R odoo:odoo "$ODOO_ADDONS_PATH/custom_fields_cleanup_module" 2>/dev/null || echo "   (Permission setting skipped - run as odoo user)"
    echo "✅ Permissions set"
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Go to Odoo Apps menu"
echo "2. Click 'Update Apps List'"
echo "3. Search for 'Custom Fields Cleanup'"
echo "4. Install the module"
echo "5. Run the cleanup from Settings > Technical > Server Actions"
echo ""
