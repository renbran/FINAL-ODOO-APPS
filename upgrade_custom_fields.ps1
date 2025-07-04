#!/usr/bin/env pwsh
# PowerShell script to upgrade custom_fields module with proper dependency handling

param(
    [string]$OdooPath = "C:\Program Files\Odoo 17.0.20241018\server\odoo-bin",
    [string]$Database = "odoo17_final",
    [string]$AddonsPath = "."
)

Write-Host "Upgrading custom_fields module with dependencies..." -ForegroundColor Green

try {
    # First, upgrade le_sale_type to ensure it's up to date
    Write-Host "Step 1: Upgrading le_sale_type module..." -ForegroundColor Yellow
    & $OdooPath -d $Database --addons-path=$AddonsPath -u le_sale_type --stop-after-init --log-level=info
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade le_sale_type module"
    }
    
    # Then upgrade custom_fields
    Write-Host "Step 2: Upgrading custom_fields module..." -ForegroundColor Yellow
    & $OdooPath -d $Database --addons-path=$AddonsPath -u custom_fields --stop-after-init --log-level=info
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade custom_fields module"
    }
    
    Write-Host "Successfully upgraded both modules!" -ForegroundColor Green
    Write-Host "You can now start your Odoo server to test the changes." -ForegroundColor Cyan
    
} catch {
    Write-Host "Error during upgrade: $_" -ForegroundColor Red
    Write-Host "Please check the Odoo logs for more details." -ForegroundColor Yellow
    exit 1
}
