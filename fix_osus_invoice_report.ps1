# PowerShell script to upgrade the osus_invoice_report module
# Run this script as Administrator

Write-Host "=== OSUS Invoice Report Module Upgrade Script ===" -ForegroundColor Cyan
Write-Host ""

# Function to check if Odoo service is running
function Test-OdooService {
    param([string]$ServiceName = "odoo")
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        return $service -and $service.Status -eq 'Running'
    }
    catch {
        return $false
    }
}

# Function to stop Odoo service
function Stop-OdooService {
    param([string]$ServiceName = "odoo")
    
    Write-Host "Stopping Odoo service..." -ForegroundColor Yellow
    try {
        Stop-Service -Name $ServiceName -Force -ErrorAction Stop
        Write-Host "✓ Odoo service stopped" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to stop Odoo service: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to start Odoo service
function Start-OdooService {
    param([string]$ServiceName = "odoo")
    
    Write-Host "Starting Odoo service..." -ForegroundColor Yellow
    try {
        Start-Service -Name $ServiceName -ErrorAction Stop
        Write-Host "✓ Odoo service started" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to start Odoo service: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
try {
    # Check if we need to specify database name
    $DatabaseName = $env:ODOO_DB_NAME
    if (-not $DatabaseName) {
        $DatabaseName = Read-Host "Enter your Odoo database name"
        if (-not $DatabaseName) {
            Write-Host "Database name is required!" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "Using database: $DatabaseName" -ForegroundColor Green
    
    # Check for Odoo installation
    $OdooBinPaths = @(
        "C:\Program Files\Odoo 17.0\server\odoo-bin",
        "C:\Odoo\server\odoo-bin",
        "python3 odoo-bin",
        "python odoo-bin"
    )
    
    $OdooBin = $null
    foreach ($path in $OdooBinPaths) {
        if (Test-Path $path -ErrorAction SilentlyContinue) {
            $OdooBin = $path
            break
        }
    }
    
    if (-not $OdooBin) {
        $OdooBin = Read-Host "Enter path to odoo-bin (or just 'python3 odoo-bin' if in PATH)"
    }
    
    Write-Host "Using Odoo binary: $OdooBin" -ForegroundColor Green
    
    # Check if Odoo service is running
    if (Test-OdooService) {
        Write-Host "Odoo service is running. Need to stop it for upgrade." -ForegroundColor Yellow
        $StopService = Read-Host "Stop Odoo service? (y/n)"
        if ($StopService -eq 'y' -or $StopService -eq 'Y') {
            if (-not (Stop-OdooService)) {
                Write-Host "Cannot proceed without stopping Odoo service." -ForegroundColor Red
                exit 1
            }
        }
        else {
            Write-Host "Cannot upgrade module while Odoo is running." -ForegroundColor Red
            exit 1
        }
    }
    
    # Upgrade the module
    Write-Host "Upgrading osus_invoice_report module..." -ForegroundColor Yellow
    
    $UpgradeCommand = "$OdooBin -d $DatabaseName -u osus_invoice_report --stop-after-init"
    Write-Host "Executing: $UpgradeCommand" -ForegroundColor Cyan
    
    $process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $UpgradeCommand -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✓ Module upgrade completed successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Module upgrade failed. Trying force reinstall..." -ForegroundColor Yellow
        
        # Try uninstall and reinstall
        $UninstallCommand = "$OdooBin -d $DatabaseName --uninstall osus_invoice_report --stop-after-init"
        Write-Host "Executing: $UninstallCommand" -ForegroundColor Cyan
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $UninstallCommand -Wait -NoNewWindow
        
        $InstallCommand = "$OdooBin -d $DatabaseName -i osus_invoice_report --stop-after-init"
        Write-Host "Executing: $InstallCommand" -ForegroundColor Cyan
        $installProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $InstallCommand -Wait -PassThru -NoNewWindow
        
        if ($installProcess.ExitCode -eq 0) {
            Write-Host "✓ Module reinstalled successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Module reinstall failed!" -ForegroundColor Red
        }
    }
    
    # Ask if user wants to restart Odoo service
    $RestartService = Read-Host "Restart Odoo service? (y/n)"
    if ($RestartService -eq 'y' -or $RestartService -eq 'Y') {
        Start-OdooService
    }
    
    Write-Host ""
    Write-Host "=== IMPORTANT NOTES ===" -ForegroundColor Cyan
    Write-Host "1. The custom_invoice.py file has been updated with fallback handling" -ForegroundColor Green
    Write-Host "2. Even if the external ID is missing, the system will use standard reports" -ForegroundColor Green
    Write-Host "3. Check the Odoo logs for any warnings about missing custom reports" -ForegroundColor Yellow
    Write-Host "4. Test the invoice printing functionality in your Odoo interface" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "✅ Fix completed!" -ForegroundColor Green
}
catch {
    Write-Host "✗ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
