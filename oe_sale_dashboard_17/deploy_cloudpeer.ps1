# CloudPeer Odoo 17 Dashboard Deployment Script
# Enhanced for AED currency and commission_ax module integration

param(
    [Parameter(Mandatory=$true)]
    [string]$CloudPeerHost,
    
    [Parameter(Mandatory=$true)]
    [string]$DatabaseName,
    
    [Parameter(Mandatory=$false)]
    [string]$ModulePath = ".",
    
    [Parameter(Mandatory=$false)]
    [switch]$TestMode = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$ForceUpdate = $false
)

Write-Host "=== Odoo 17 Sales Dashboard CloudPeer Deployment ===" -ForegroundColor Green
Write-Host "Target: $CloudPeerHost" -ForegroundColor Yellow
Write-Host "Database: $DatabaseName" -ForegroundColor Yellow
Write-Host "Module Path: $ModulePath" -ForegroundColor Yellow

# Pre-deployment validation
Write-Host "`n[1/6] Pre-deployment Validation..." -ForegroundColor Cyan

# Check required files
$requiredFiles = @(
    "__manifest__.py",
    "__init__.py", 
    "models/sale_dashboard.py",
    "static/src/js/dashboard.js",
    "static/src/xml/dashboard_template.xml",
    "static/src/scss/dashboard.scss",
    "views/dashboard_views.xml",
    "security/ir.model.access.csv"
)

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $ModulePath $file
    if (-not (Test-Path $filePath)) {
        Write-Host "ERROR: Required file missing: $file" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✓ $file" -ForegroundColor Green
    }
}

# Validate Python syntax
Write-Host "`n[2/6] Python Syntax Validation..." -ForegroundColor Cyan
try {
    python -m py_compile "$ModulePath\__manifest__.py"
    python -m py_compile "$ModulePath\models\sale_dashboard.py"
    Write-Host "✓ Python syntax valid" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python syntax errors found" -ForegroundColor Red
    exit 1
}

# Validate JavaScript syntax
Write-Host "`n[3/6] JavaScript Syntax Validation..." -ForegroundColor Cyan
try {
    node -c "$ModulePath\static\src\js\dashboard.js"
    Write-Host "✓ JavaScript syntax valid" -ForegroundColor Green
} catch {
    Write-Host "ERROR: JavaScript syntax errors found" -ForegroundColor Red
    Write-Host "Please fix JavaScript errors before deployment" -ForegroundColor Yellow
    exit 1
}
}

# Create deployment package
Write-Host "`n[4/6] Creating Deployment Package..." -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packageName = "oe_sale_dashboard_17_$timestamp.zip"
$deploymentPath = Join-Path $env:TEMP $packageName

# Copy module to temp directory for packaging
$tempModulePath = Join-Path $env:TEMP "oe_sale_dashboard_17_temp"
if (Test-Path $tempModulePath) {
    Remove-Item $tempModulePath -Recurse -Force
}

Copy-Item $ModulePath $tempModulePath -Recurse

# Update manifest with deployment info
$manifestPath = Join-Path $tempModulePath "__manifest__.py"
$manifestContent = Get-Content $manifestPath -Raw

# Increment version for deployment
$versionPattern = "'version':\s*'([^']+)'"
if ($manifestContent -match $versionPattern) {
    $currentVersion = $matches[1]
    $versionParts = $currentVersion.Split('.')
    $buildNumber = [int]$versionParts[-1] + 1
    $versionParts[-1] = $buildNumber.ToString()
    $newVersion = $versionParts -join '.'
    
    $manifestContent = $manifestContent -replace $versionPattern, "'version': '$newVersion'"
    Set-Content -Path $manifestPath -Value $manifestContent
    
    Write-Host "✓ Version updated to: $newVersion" -ForegroundColor Green
}
}

# Create ZIP package
Compress-Archive -Path $tempModulePath -DestinationPath $deploymentPath -Force
Write-Host "✓ Deployment package created: $packageName" -ForegroundColor Green

# CloudPeer deployment steps
Write-Host "`n[5/6] CloudPeer Deployment..." -ForegroundColor Cyan

if ($TestMode) {
    Write-Host "TEST MODE: Skipping actual deployment" -ForegroundColor Yellow
    Write-Host "Package ready at: $deploymentPath" -ForegroundColor Yellow
} else {
    Write-Host "DEPLOYMENT INSTRUCTIONS FOR CLOUDPEER:" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "1. Upload module package: $packageName" -ForegroundColor White
    Write-Host "2. Extract to addons directory" -ForegroundColor White
    Write-Host "3. Update module list in Odoo Apps" -ForegroundColor White
    Write-Host "4. Install/Upgrade oe_sale_dashboard_17" -ForegroundColor White
    Write-Host "5. Clear assets cache if needed" -ForegroundColor White
    Write-Host "6. Test dashboard functionality" -ForegroundColor White
    
    # If SSH/SCP credentials are available, could automate upload
    Write-Host "`nFor automated deployment, configure SSH access to CloudPeer" -ForegroundColor Cyan
}

# Post-deployment validation checklist
Write-Host "`n[6/6] Post-Deployment Checklist..." -ForegroundColor Cyan
Write-Host "After deployment, verify the following:" -ForegroundColor Yellow
Write-Host "✓ Module appears in Apps list" -ForegroundColor White
Write-Host "✓ No installation errors in logs" -ForegroundColor White
Write-Host "✓ Dashboard menu appears in Sales app" -ForegroundColor White
Write-Host "✓ Charts render correctly with Chart.js" -ForegroundColor White
Write-Host "✓ AED currency formatting displays properly" -ForegroundColor White
Write-Host "✓ Commission fields from commission_ax module work" -ForegroundColor White
Write-Host "✓ No JavaScript errors in browser console" -ForegroundColor White
Write-Host "✓ Data loads correctly with booking_date/sale_value fields" -ForegroundColor White

# Enhanced monitoring commands
Write-Host "`nMONITORING COMMANDS:" -ForegroundColor Yellow
Write-Host "- Check Odoo logs: tail -f /var/log/odoo/odoo.log | grep dashboard" -ForegroundColor White
Write-Host "- Monitor JavaScript console for errors" -ForegroundColor White
Write-Host "- Test with different date ranges and sales types" -ForegroundColor White
Write-Host "- Verify commission calculations and AED formatting" -ForegroundColor White

# Rollback instructions
Write-Host "`nROLLBACK PLAN:" -ForegroundColor Red
Write-Host "If deployment fails:" -ForegroundColor Red
Write-Host "1. Uninstall module from Apps" -ForegroundColor White
Write-Host "2. Remove module folder from addons" -ForegroundColor White
Write-Host "3. Restart Odoo service" -ForegroundColor White
Write-Host "4. Clear browser cache" -ForegroundColor White

Write-Host "`n=== Deployment Package Ready ===" -ForegroundColor Green
Write-Host "Location: $deploymentPath" -ForegroundColor Yellow
Write-Host "Ready for CloudPeer upload and installation!" -ForegroundColor Green

# Cleanup temp directory
Remove-Item $tempModulePath -Recurse -Force

exit 0
