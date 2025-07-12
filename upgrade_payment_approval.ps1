# PowerShell script to upgrade the account_payment_approval module in Odoo
# This script uses the exact Odoo setup with virtual environment

Write-Host "Starting Odoo Payment Approval Module Upgrade..." -ForegroundColor Green

# Configuration - Updated for your specific Odoo setup
$ODOO_DB = "osuspro"
$ODOO_USER = "admin"
$ODOO_PASSWORD = "admin"  # Change this to your actual admin password
$ODOO_HOST = "139.84.163.11"  # Your remote server IP
$ODOO_PORT = "8069"
$MODULE_NAME = "account_payment_approval"

# Odoo installation paths for your setup
$ODOO_BASE_PATH = "/var/odoo/osuspro"
$ODOO_PYTHON = "$ODOO_BASE_PATH/venv/bin/python3"
$ODOO_BIN_PATH = "$ODOO_BASE_PATH/src/odoo-bin"
$ODOO_CONFIG = "$ODOO_BASE_PATH/odoo.conf"
$ODOO_SYSTEM_USER = "odoo"

Write-Host "Attempting to upgrade module: $MODULE_NAME" -ForegroundColor Yellow

# Method 1: Using curl to call Odoo JSON-RPC API (requires curl to be installed)
try {
    Write-Host "Method 1: Using API call to upgrade module..." -ForegroundColor Cyan
    
    # First, authenticate and get session
    $authPayload = @{
        jsonrpc = "2.0"
        method = "call"
        params = @{
            service = "common"
            method = "authenticate"
            args = @($ODOO_DB, $ODOO_USER, $ODOO_PASSWORD, @{})
        }
        id = 1
    } | ConvertTo-Json -Depth 5

    $authResponse = Invoke-RestMethod -Uri "http://$ODOO_HOST`:$ODOO_PORT/jsonrpc" -Method Post -Body $authPayload -ContentType "application/json"
    
    if ($authResponse.result) {
        $uid = $authResponse.result
        Write-Host "Authentication successful. User ID: $uid" -ForegroundColor Green
        
        # Search for the module
        $searchPayload = @{
            jsonrpc = "2.0"
            method = "call"
            params = @{
                service = "object"
                method = "execute_kw"
                args = @(
                    $ODOO_DB,
                    $uid,
                    $ODOO_PASSWORD,
                    "ir.module.module",
                    "search",
                    @(@(@("name", "=", $MODULE_NAME)))
                )
            }
            id = 2
        } | ConvertTo-Json -Depth 6

        $searchResponse = Invoke-RestMethod -Uri "http://$ODOO_HOST`:$ODOO_PORT/jsonrpc" -Method Post -Body $searchPayload -ContentType "application/json"
        
        if ($searchResponse.result -and $searchResponse.result.Count -gt 0) {
            $moduleId = $searchResponse.result[0]
            Write-Host "Module found with ID: $moduleId" -ForegroundColor Green
            
            # Upgrade the module
            $upgradePayload = @{
                jsonrpc = "2.0"
                method = "call"
                params = @{
                    service = "object"
                    method = "execute_kw"
                    args = @(
                        $ODOO_DB,
                        $uid,
                        $ODOO_PASSWORD,
                        "ir.module.module",
                        "button_immediate_upgrade",
                        @(@($moduleId))
                    )
                }
                id = 3
            } | ConvertTo-Json -Depth 6

            $upgradeResponse = Invoke-RestMethod -Uri "http://$ODOO_HOST`:$ODOO_PORT/jsonrpc" -Method Post -Body $upgradePayload -ContentType "application/json"
            
            if ($upgradeResponse.error) {
                Write-Host "Error upgrading module: $($upgradeResponse.error.message)" -ForegroundColor Red
            } else {
                Write-Host "Module upgrade initiated successfully!" -ForegroundColor Green
            }
        } else {
            Write-Host "Module $MODULE_NAME not found!" -ForegroundColor Red
        }
    } else {
        Write-Host "Authentication failed!" -ForegroundColor Red
    }
} catch {
    Write-Host "API method failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
}

# Method 2: Using odoo-bin command line with virtual environment (recommended)
try {
    Write-Host "Method 2: Using odoo-bin command line with virtual environment..." -ForegroundColor Cyan
    
    # Commands to run on the remote server
    $commands = @(
        "# Navigate to Odoo directory",
        "cd $ODOO_BASE_PATH",
        "",
        "# Install/Upgrade the specific module",
        "sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --update $MODULE_NAME",
        "",
        "# Alternative: Install if not installed yet",
        "# sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --install $MODULE_NAME",
        "",
        "# Alternative: Update all modules (use with caution)",
        "# sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --update all"
    )
    
    Write-Host "Commands to execute on your remote server ($ODOO_HOST):" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Yellow
    foreach ($cmd in $commands) {
        if ($cmd.StartsWith("#") -or $cmd -eq "") {
            Write-Host $cmd -ForegroundColor Gray
        } else {
            Write-Host $cmd -ForegroundColor White
        }
    }
    Write-Host "================================================================" -ForegroundColor Yellow
    
} catch {
    Write-Host "Command preparation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 3: Manual instructions
Write-Host "`n=== MANUAL INSTRUCTIONS ===" -ForegroundColor Magenta
Write-Host "If the automated methods don't work, follow these steps manually:" -ForegroundColor White
Write-Host "1. Access your Odoo instance via web browser at http://$ODOO_HOST`:$ODOO_PORT" -ForegroundColor White
Write-Host "2. Go to Apps menu" -ForegroundColor White
Write-Host "3. Remove the 'Apps' filter and search for 'Payment Approvals' or 'account_payment_approval'" -ForegroundColor White
Write-Host "4. Click on the module and then click 'Upgrade' or 'Install'" -ForegroundColor White
Write-Host "`nOR SSH to your server and run:" -ForegroundColor White
Write-Host "ssh root@$ODOO_HOST" -ForegroundColor Cyan
Write-Host "cd $ODOO_BASE_PATH" -ForegroundColor Cyan
Write-Host "sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --update $MODULE_NAME" -ForegroundColor Cyan

Write-Host "`n=== ADDITIONAL USEFUL COMMANDS ===" -ForegroundColor Magenta
Write-Host "To check if module is installed:" -ForegroundColor White
Write-Host "sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --list-apps | grep $MODULE_NAME" -ForegroundColor Cyan
Write-Host "`nTo install the module (if not installed):" -ForegroundColor White
Write-Host "sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --install $MODULE_NAME" -ForegroundColor Cyan
Write-Host "`nTo update all modules (use with caution):" -ForegroundColor White
Write-Host "sudo -u $ODOO_SYSTEM_USER $ODOO_PYTHON $ODOO_BIN_PATH -c $ODOO_CONFIG -d $ODOO_DB --no-http --stop-after-init --update all" -ForegroundColor Cyan

Write-Host "`nScript execution completed." -ForegroundColor Green
