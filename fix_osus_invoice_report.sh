#!/bin/bash
# Shell script to upgrade the osus_invoice_report module
# Make sure to run this with appropriate permissions

echo "=== OSUS Invoice Report Module Upgrade Script ==="
echo ""

# Function to check if Odoo is running
check_odoo_running() {
    if pgrep -f "odoo-bin" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to stop Odoo
stop_odoo() {
    echo "Stopping Odoo processes..."
    pkill -f "odoo-bin"
    sleep 3
    if check_odoo_running; then
        echo "Force killing Odoo processes..."
        pkill -9 -f "odoo-bin"
        sleep 2
    fi
    echo "✓ Odoo processes stopped"
}

# Get database name
if [ -z "$ODOO_DB_NAME" ]; then
    read -p "Enter your Odoo database name: " DATABASE_NAME
    if [ -z "$DATABASE_NAME" ]; then
        echo "Database name is required!"
        exit 1
    fi
else
    DATABASE_NAME="$ODOO_DB_NAME"
fi

echo "Using database: $DATABASE_NAME"

# Find Odoo binary
ODOO_BIN=""
POSSIBLE_PATHS=(
    "/usr/bin/odoo"
    "/opt/odoo/odoo-bin"
    "/var/odoo/osuspro/src/odoo-bin"
    "python3 odoo-bin"
    "python odoo-bin"
    "./odoo-bin"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if command -v $path &> /dev/null || [ -f "$path" ]; then
        ODOO_BIN="$path"
        break
    fi
done

if [ -z "$ODOO_BIN" ]; then
    read -p "Enter path to odoo-bin: " ODOO_BIN
    if [ -z "$ODOO_BIN" ]; then
        echo "Odoo binary path is required!"
        exit 1
    fi
fi

echo "Using Odoo binary: $ODOO_BIN"

# Check if Odoo is running
if check_odoo_running; then
    echo "Odoo is currently running. Need to stop it for upgrade."
    read -p "Stop Odoo? (y/n): " STOP_ODOO
    if [[ "$STOP_ODOO" =~ ^[Yy]$ ]]; then
        stop_odoo
    else
        echo "Cannot upgrade module while Odoo is running."
        exit 1
    fi
fi

# Upgrade the module
echo "Upgrading osus_invoice_report module..."
UPGRADE_CMD="$ODOO_BIN -d $DATABASE_NAME -u osus_invoice_report --stop-after-init"
echo "Executing: $UPGRADE_CMD"

if $UPGRADE_CMD; then
    echo "✓ Module upgrade completed successfully!"
else
    echo "✗ Module upgrade failed. Trying force reinstall..."
    
    # Try uninstall and reinstall
    echo "Uninstalling module..."
    $ODOO_BIN -d $DATABASE_NAME --uninstall osus_invoice_report --stop-after-init
    
    echo "Reinstalling module..."
    if $ODOO_BIN -d $DATABASE_NAME -i osus_invoice_report --stop-after-init; then
        echo "✓ Module reinstalled successfully!"
    else
        echo "✗ Module reinstall failed!"
        echo "Please check the Odoo logs for detailed error information."
        exit 1
    fi
fi

echo ""
echo "=== IMPORTANT NOTES ==="
echo "1. The custom_invoice.py file has been updated with fallback handling"
echo "2. Even if the external ID is missing, the system will use standard reports"
echo "3. Check the Odoo logs for any warnings about missing custom reports"
echo "4. Test the invoice printing functionality in your Odoo interface"
echo ""
echo "✅ Fix completed!"

# Ask if user wants to restart Odoo
read -p "Would you like to start Odoo now? (y/n): " START_ODOO
if [[ "$START_ODOO" =~ ^[Yy]$ ]]; then
    echo "Starting Odoo..."
    nohup $ODOO_BIN -d $DATABASE_NAME > /dev/null 2>&1 &
    echo "✓ Odoo started in background"
fi

echo ""
echo "Script completed. You can now test the invoice printing functionality."
