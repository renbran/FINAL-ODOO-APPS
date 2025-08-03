#!/bin/bash
# -*- coding: utf-8 -*-

"""
CloudPepper Odoo Server Maintenance Script
For coatest.cloudpepper.site server maintenance and module deployment
"""

echo "🔧 CloudPepper Odoo Server Maintenance"
echo "======================================"
echo ""

# Server Configuration
ODOO_USER="odoo"
ODOO_PATH="/var/odoo/coatest"
ODOO_SRC="$ODOO_PATH/src"
ODOO_LOGS="$ODOO_PATH/logs"
ODOO_CONFIG="$ODOO_PATH/odoo.conf"
PYTHON_BIN="$ODOO_PATH/venv/bin/python3"
ODOO_BIN="$ODOO_SRC/odoo-bin"

echo "📋 Server Information:"
echo "   Source: $ODOO_SRC"
echo "   Logs: $ODOO_LOGS"
echo "   Config: $ODOO_CONFIG"
echo "   Python: $PYTHON_BIN"
echo ""

# Function to check server status
check_server_status() {
    echo "🔍 Checking Odoo server status..."
    if pgrep -f "odoo-bin" > /dev/null; then
        echo "   ✅ Odoo server is running"
        return 0
    else
        echo "   ❌ Odoo server is not running"
        return 1
    fi
}

# Function to restart Odoo
restart_odoo() {
    echo "🔄 Restarting Odoo server..."
    
    # Stop Odoo
    echo "   Stopping Odoo..."
    sudo pkill -f "odoo-bin" 2>/dev/null || true
    sleep 3
    
    # Start Odoo
    echo "   Starting Odoo..."
    cd "$ODOO_PATH" && sudo -u "$ODOO_USER" "$PYTHON_BIN" "$ODOO_BIN" -c "$ODOO_CONFIG" --daemon
    sleep 5
    
    if check_server_status; then
        echo "   ✅ Odoo restarted successfully"
        return 0
    else
        echo "   ❌ Failed to restart Odoo"
        return 1
    fi
}

# Function to check logs
check_logs() {
    echo "📋 Checking recent logs..."
    
    if [ -f "$ODOO_LOGS/odoo.log" ]; then
        echo "   Last 20 lines of odoo.log:"
        tail -20 "$ODOO_LOGS/odoo.log"
    else
        echo "   ⚠️  Log file not found at $ODOO_LOGS/odoo.log"
        echo "   Checking for alternative log locations..."
        find /var/log -name "*odoo*" 2>/dev/null || echo "   No Odoo logs found"
    fi
}

# Function to update all modules
update_all_modules() {
    echo "🔄 Updating all modules..."
    
    # Stop any running Odoo instances
    sudo pkill -f "odoo-bin" 2>/dev/null || true
    sleep 3
    
    # Run module update
    echo "   Running module update (this may take several minutes)..."
    cd "$ODOO_PATH" && sudo -u "$ODOO_USER" "$PYTHON_BIN" "$ODOO_BIN" -c "$ODOO_CONFIG" --no-http --stop-after-init --update all
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Module update completed successfully"
        restart_odoo
        return 0
    else
        echo "   ❌ Module update failed"
        return 1
    fi
}

# Function to check addons directory
check_addons() {
    echo "📦 Checking addons directories..."
    
    # Extract addons paths from config
    if [ -f "$ODOO_CONFIG" ]; then
        echo "   Reading addons paths from config..."
        ADDONS_PATHS=$(grep "addons_path" "$ODOO_CONFIG" | cut -d'=' -f2 | tr ',' '\n' | sed 's/^ *//')
        
        echo "   Configured addons paths:"
        echo "$ADDONS_PATHS" | while read -r path; do
            if [ -d "$path" ]; then
                echo "     ✅ $path (exists)"
                echo "        Modules: $(ls -1 "$path" | head -5 | tr '\n' ' ')..."
            else
                echo "     ❌ $path (missing)"
            fi
        done
    else
        echo "   ❌ Config file not found: $ODOO_CONFIG"
    fi
}

# Function to deploy CRM dashboard
deploy_crm_dashboard() {
    echo "🚀 Deploying CRM Executive Dashboard..."
    
    # Find the addons directory
    ADDONS_PATH=$(grep "addons_path" "$ODOO_CONFIG" | cut -d'=' -f2 | cut -d',' -f1 | sed 's/^ *//')
    
    if [ -z "$ADDONS_PATH" ] || [ ! -d "$ADDONS_PATH" ]; then
        echo "   ❌ Cannot find addons directory"
        return 1
    fi
    
    echo "   Target directory: $ADDONS_PATH"
    
    # Check if we have the module locally
    if [ -d "./deployment_package/crm_executive_dashboard" ]; then
        echo "   📁 Found deployment package"
        
        # Copy the module
        sudo cp -r "./deployment_package/crm_executive_dashboard" "$ADDONS_PATH/"
        sudo chown -R "$ODOO_USER:$ODOO_USER" "$ADDONS_PATH/crm_executive_dashboard"
        sudo chmod -R 755 "$ADDONS_PATH/crm_executive_dashboard"
        
        echo "   ✅ Module deployed to $ADDONS_PATH/crm_executive_dashboard"
        
        # Update modules
        echo "   🔄 Updating module list..."
        cd "$ODOO_PATH" && sudo -u "$ODOO_USER" "$PYTHON_BIN" "$ODOO_BIN" -c "$ODOO_CONFIG" --no-http --stop-after-init --init crm_executive_dashboard
        
        if [ $? -eq 0 ]; then
            echo "   ✅ CRM Executive Dashboard deployed successfully"
            restart_odoo
            return 0
        else
            echo "   ❌ Module initialization failed"
            return 1
        fi
    else
        echo "   ❌ Deployment package not found"
        echo "   Please ensure you have the deployment_package/crm_executive_dashboard directory"
        return 1
    fi
}

# Function to run diagnostics
run_diagnostics() {
    echo "🔍 Running server diagnostics..."
    
    # Check disk space
    echo "   💾 Disk space:"
    df -h "$ODOO_PATH"
    
    # Check memory
    echo "   🧠 Memory usage:"
    free -h
    
    # Check Odoo processes
    echo "   🔄 Odoo processes:"
    ps aux | grep odoo-bin | grep -v grep || echo "     No Odoo processes found"
    
    # Check listening ports
    echo "   🌐 Listening ports:"
    netstat -tlnp | grep :8069 || echo "     Port 8069 not listening"
    
    # Check recent errors in logs
    echo "   ⚠️  Recent errors:"
    if [ -f "$ODOO_LOGS/odoo.log" ]; then
        grep -i "error\|exception\|traceback" "$ODOO_LOGS/odoo.log" | tail -5 || echo "     No recent errors found"
    else
        echo "     Log file not accessible"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "🎯 Choose an action:"
    echo "   1) Check server status"
    echo "   2) Restart Odoo server"
    echo "   3) Check logs"
    echo "   4) Update all modules"
    echo "   5) Check addons directories"
    echo "   6) Deploy CRM Executive Dashboard"
    echo "   7) Run diagnostics"
    echo "   8) Emergency fix (restart + update)"
    echo "   9) Exit"
    echo ""
    read -p "Enter your choice (1-9): " choice
    
    case $choice in
        1) check_server_status ;;
        2) restart_odoo ;;
        3) check_logs ;;
        4) update_all_modules ;;
        5) check_addons ;;
        6) deploy_crm_dashboard ;;
        7) run_diagnostics ;;
        8) 
            echo "🚨 Emergency fix initiated..."
            restart_odoo
            sleep 5
            update_all_modules
            ;;
        9) 
            echo "👋 Goodbye!"
            exit 0
            ;;
        *) 
            echo "❌ Invalid choice"
            ;;
    esac
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs sudo privileges to manage the Odoo server"
    echo "   Please run: sudo $0"
    exit 1
fi

# Initial status check
check_server_status
echo ""

# Main loop
while true; do
    show_menu
    echo ""
    read -p "Press Enter to continue..." dummy
done
