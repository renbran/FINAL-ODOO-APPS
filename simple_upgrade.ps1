# Simple PowerShell script to upgrade the custom_fields module
param(
    [string]$Database = "odoo17_final"
)

Write-Host "🔧 Upgrading custom_fields module..." -ForegroundColor Green

# Try different possible Odoo paths
$OdooPaths = @(
    "C:\Program Files\Odoo 17.0\server\odoo-bin",
    "C:\Program Files\Odoo 17.0.20241018\server\odoo-bin",
    "C:\odoo\server\odoo-bin",
    "odoo-bin"
)

$OdooPath = $null
foreach ($path in $OdooPaths) {
    if (Test-Path $path) {
        $OdooPath = $path
        break
    }
}

if (-not $OdooPath) {
    Write-Host "❌ Odoo executable not found. Please check your Odoo installation." -ForegroundColor Red
    Write-Host "Searched paths:" -ForegroundColor Yellow
    $OdooPaths | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}

Write-Host "📍 Using Odoo at: $OdooPath" -ForegroundColor Cyan

try {
    Write-Host "🔄 Running module upgrade..." -ForegroundColor Yellow
    
    # First, try to install/upgrade without starting the server
    $process = Start-Process -FilePath $OdooPath -ArgumentList @(
        "-d", $Database,
        "--addons-path=.",
        "-u", "custom_fields",
        "--stop-after-init",
        "--log-level=info"
    ) -NoNewWindow -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Module upgrade completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Module upgrade completed with exit code: $($process.ExitCode)" -ForegroundColor Yellow
        Write-Host "This might be normal if there were warnings but no errors." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error during module upgrade: $_" -ForegroundColor Red
    Write-Host "💡 Try running this command manually:" -ForegroundColor Cyan
    Write-Host "   & `"$OdooPath`" -d $Database --addons-path=. -u custom_fields --stop-after-init" -ForegroundColor Cyan
}

Write-Host "🎉 Process completed!" -ForegroundColor Green
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Start your Odoo server" -ForegroundColor White
Write-Host "   2. Go to Sales > Orders to see the enhanced custom fields" -ForegroundColor White
Write-Host "   3. Go to Accounting > Invoices to see the deal information fields" -ForegroundColor White
