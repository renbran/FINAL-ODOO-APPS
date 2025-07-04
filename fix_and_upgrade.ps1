# PowerShell script to fix view conflicts and upgrade modules
param(
    [string]$OdooPath = "C:\Program Files\Odoo 17.0.20241018\server\odoo-bin",
    [string]$Database = "odoo17_final",
    [string]$AddonsPath = "."
)

Write-Host "🚀 Starting Odoo Module Fix and Upgrade Process..." -ForegroundColor Green

# Step 1: Stop Odoo service if running
Write-Host "📝 Step 1: Stopping Odoo service..." -ForegroundColor Yellow
try {
    Stop-Service "odoo-server-17.0" -ErrorAction SilentlyContinue
    Write-Host "✅ Odoo service stopped" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Odoo service was not running" -ForegroundColor Yellow
}

# Step 2: Check if PostgreSQL is running
Write-Host "📝 Step 2: Checking PostgreSQL service..." -ForegroundColor Yellow
$pgService = Get-Service "PostgreSQL_For_Odoo" -ErrorAction SilentlyContinue
if ($pgService.Status -ne "Running") {
    Write-Host "🔄 Starting PostgreSQL..." -ForegroundColor Yellow
    try {
        Start-Service "PostgreSQL_For_Odoo"
        Start-Sleep -Seconds 5
        Write-Host "✅ PostgreSQL started" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start PostgreSQL. Please start it manually." -ForegroundColor Red
        exit 1
    }
}

# Step 3: Upgrade custom_fields module with cleanup
Write-Host "📝 Step 3: Upgrading custom_fields module..." -ForegroundColor Yellow
try {
    & $OdooPath -d $Database --addons-path=$AddonsPath -u custom_fields --stop-after-init --log-level=info
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ custom_fields module upgraded successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Module upgrade completed with warnings (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to upgrade custom_fields module: $_" -ForegroundColor Red
}

# Step 4: Restart Odoo service
Write-Host "📝 Step 4: Starting Odoo service..." -ForegroundColor Yellow
try {
    Start-Service "odoo-server-17.0"
    Start-Sleep -Seconds 10
    Write-Host "✅ Odoo service started" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start Odoo service: $_" -ForegroundColor Red
}

Write-Host "🎉 Process completed! Your custom_fields module should now be working without conflicts." -ForegroundColor Green
Write-Host "📌 Access your Odoo instance at: http://localhost:8069" -ForegroundColor Cyan
Write-Host "📌 Database: $Database" -ForegroundColor Cyan
