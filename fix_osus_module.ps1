# PowerShell script to fix OSUS Invoice Report module installation
# This script handles the paper format external ID issue

param(
    [string]$Database = "odoo17_final",
    [string]$OdooPath = "C:\Program Files\Odoo 17.0\server\odoo-bin",
    [string]$ConfigPath = "C:\Program Files\Odoo 17.0\server\odoo.conf",
    [string]$AddonsPath = $null
)

Write-Host "OSUS Invoice Report Module Fix Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Set default addons path if not provided
if (-not $AddonsPath) {
    $AddonsPath = Get-Location
}

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Database: $Database" -ForegroundColor White
Write-Host "  Odoo Path: $OdooPath" -ForegroundColor White
Write-Host "  Config Path: $ConfigPath" -ForegroundColor White
Write-Host "  Addons Path: $AddonsPath" -ForegroundColor White

# Check if Odoo binary exists
if (-not (Test-Path $OdooPath)) {
    Write-Host "❌ Odoo binary not found at: $OdooPath" -ForegroundColor Red
    Write-Host "Please provide the correct path using -OdooPath parameter" -ForegroundColor Yellow
    exit 1
}

# Check if config file exists
if (-not (Test-Path $ConfigPath)) {
    Write-Host "⚠️ Config file not found at: $ConfigPath" -ForegroundColor Yellow
    Write-Host "Will run without config file" -ForegroundColor Yellow
    $ConfigPath = $null
}

# Check if fix script exists
$FixScriptPath = Join-Path $AddonsPath "fix_osus_module.py"
if (-not (Test-Path $FixScriptPath)) {
    Write-Host "❌ Fix script not found at: $FixScriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "`nStarting OSUS module fix..." -ForegroundColor Green

try {
    # Build the command
    $Command = "`"$OdooPath`" shell -d $Database --addons-path=`"$AddonsPath`""
    
    if ($ConfigPath) {
        $Command += " -c `"$ConfigPath`""
    }
    
    # Add the fix script
    $Command += " < `"$FixScriptPath`""
    
    Write-Host "Executing command:" -ForegroundColor Cyan
    Write-Host $Command -ForegroundColor White
    
    # Execute the command
    $Result = Invoke-Expression $Command
    
    Write-Host "`n✅ Fix script executed successfully!" -ForegroundColor Green
    Write-Host "Check the output above for details." -ForegroundColor White
    
} catch {
    Write-Host "❌ Error executing fix script:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Alternative method: Direct module installation via Odoo CLI
Write-Host "`nTrying alternative installation method..." -ForegroundColor Yellow

try {
    $InstallCommand = "`"$OdooPath`" -d $Database --addons-path=`"$AddonsPath`" -i osus_invoice_report --stop-after-init"
    
    if ($ConfigPath) {
        $InstallCommand += " -c `"$ConfigPath`""
    }
    
    Write-Host "Executing installation command:" -ForegroundColor Cyan
    Write-Host $InstallCommand -ForegroundColor White
    
    $InstallResult = Invoke-Expression $InstallCommand
    
    Write-Host "`n✅ Installation command executed!" -ForegroundColor Green
    
} catch {
    Write-Host "⚠️ Alternative installation failed:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Yellow
}

# Try upgrade as well
Write-Host "`nTrying module upgrade..." -ForegroundColor Yellow

try {
    $UpgradeCommand = "`"$OdooPath`" -d $Database --addons-path=`"$AddonsPath`" -u osus_invoice_report --stop-after-init"
    
    if ($ConfigPath) {
        $UpgradeCommand += " -c `"$ConfigPath`""
    }
    
    Write-Host "Executing upgrade command:" -ForegroundColor Cyan
    Write-Host $UpgradeCommand -ForegroundColor White
    
    $UpgradeResult = Invoke-Expression $UpgradeCommand
    
    Write-Host "`n✅ Upgrade command executed!" -ForegroundColor Green
    
} catch {
    Write-Host "⚠️ Upgrade failed:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "OSUS Module Fix Complete!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start your Odoo server" -ForegroundColor White
Write-Host "2. Go to Apps menu and check if 'OSUS Invoice Report' is installed" -ForegroundColor White
Write-Host "3. If not installed, try installing it manually from the Apps menu" -ForegroundColor White
Write-Host "4. Test the invoice reports to ensure they work correctly" -ForegroundColor White
Write-Host ""
Write-Host "If you still encounter issues, check the Odoo log files for detailed error messages." -ForegroundColor Cyan
