#!/bin/bash
# Bash script to upgrade account_payment_approval module on Odoo server
# Updated for your specific Odoo setup with virtual environment

echo "Starting Odoo Payment Approval Module Upgrade..."

# Configuration for your specific setup
ODOO_DB="osuspro"
MODULE_NAME="account_payment_approval"
ODOO_BASE_PATH="/var/odoo/osuspro"
ODOO_PYTHON="$ODOO_BASE_PATH/venv/bin/python3"
ODOO_BIN="$ODOO_BASE_PATH/src/odoo-bin"
ODOO_CONFIG="$ODOO_BASE_PATH/odoo.conf"
ODOO_USER="odoo"

echo "Configuration:"
echo "  Database: $ODOO_DB"
echo "  Module: $MODULE_NAME"
echo "  Odoo Path: $ODOO_BASE_PATH"
echo "  Python: $ODOO_PYTHON"
echo "  Config: $ODOO_CONFIG"
echo ""

# Navigate to Odoo directory
echo "Navigating to Odoo directory..."
cd $ODOO_BASE_PATH

# Check if paths exist
if [ ! -f "$ODOO_PYTHON" ]; then
    echo "Error: Python executable not found at $ODOO_PYTHON"
    exit 1
fi

if [ ! -f "$ODOO_BIN" ]; then
    echo "Error: Odoo binary not found at $ODOO_BIN"
    exit 1
fi

if [ ! -f "$ODOO_CONFIG" ]; then
    echo "Error: Odoo config not found at $ODOO_CONFIG"
    exit 1
fi

echo "All paths verified successfully."
echo ""

# Function to upgrade module
upgrade_module() {
    echo "Upgrading module: $MODULE_NAME for database: $ODOO_DB"
    echo "Command: sudo -u $ODOO_USER $ODOO_PYTHON $ODOO_BIN -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --update $MODULE_NAME"
    echo ""
    
    sudo -u $ODOO_USER $ODOO_PYTHON $ODOO_BIN -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --update $MODULE_NAME
    
    if [ $? -eq 0 ]; then
        echo "Module upgrade completed successfully!"
        return 0
    else
        echo "Module upgrade failed! Trying to install..."
        return 1
    fi
}

# Function to install module
install_module() {
    echo "Installing module: $MODULE_NAME for database: $ODOO_DB"
    echo "Command: sudo -u $ODOO_USER $ODOO_PYTHON $ODOO_BIN -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --install $MODULE_NAME"
    echo ""
    
    sudo -u $ODOO_USER $ODOO_PYTHON $ODOO_BIN -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --install $MODULE_NAME
    
    if [ $? -eq 0 ]; then
        echo "Module installation completed successfully!"
        return 0
    else
        echo "Module installation failed!"
        return 1
    fi
}

# Try to upgrade first, then install if upgrade fails
if ! upgrade_module; then
    echo ""
    echo "Upgrade failed, attempting installation..."
    if ! install_module; then
        echo ""
        echo "Both upgrade and installation failed!"
        echo "Please check the logs for more details."
        exit 1
    fi
fi

echo ""
echo "=== Operation completed successfully! ==="
echo ""
echo "You may need to restart your Odoo service:"
echo "sudo systemctl restart odoo"
echo ""
echo "Or if running manually, restart your Odoo process."
