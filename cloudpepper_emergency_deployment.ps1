# CloudPepper Emergency Deployment Script (PowerShell)
# This script forces a complete module update to resolve XPath caching issues

Write-Host "🚨 CLOUDPEPPER EMERGENCY DEPLOYMENT" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Yellow
Write-Host "Module: frontend_enhancement"
Write-Host "Issue: Cached XPath expressions causing parse errors"
Write-Host "Solution: Force complete module reinstall"
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend_enhancement")) {
    Write-Host "❌ Error: frontend_enhancement directory not found" -ForegroundColor Red
    Write-Host "Please run this script from the odoo17_final root directory"
    exit 1
}

Write-Host "📋 Pre-deployment validation..." -ForegroundColor Cyan

# Validate XML files
Write-Host "  🔍 Validating XML syntax..."
$xmlFiles = Get-ChildItem -Path "frontend_enhancement" -Recurse -Filter "*.xml"
$xmlValid = $true

foreach ($xmlFile in $xmlFiles) {
    try {
        $xml = [xml](Get-Content $xmlFile.FullName)
        Write-Host "    ✅ $($xmlFile.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "    ❌ $($xmlFile.Name) - SYNTAX ERROR" -ForegroundColor Red
        $xmlValid = $false
    }
}

# Check for problematic XPath expressions
Write-Host "  🔍 Checking for hasclass() expressions..."
$hasclassFiles = Select-String -Path "frontend_enhancement\**\*.xml" -Pattern "hasclass\(" -SimpleMatch 2>$null
if ($hasclassFiles.Count -eq 0) {
    Write-Host "    ✅ No problematic XPath expressions found" -ForegroundColor Green
} else {
    Write-Host "    ❌ Found hasclass() expressions - MUST BE FIXED" -ForegroundColor Red
    $hasclassFiles | ForEach-Object { Write-Host "      $($_.Filename):$($_.LineNumber)" }
    exit 1
}

if (-not $xmlValid) {
    Write-Host "❌ XML validation failed - please fix syntax errors" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ All validation checks passed!" -ForegroundColor Green
Write-Host ""

Write-Host "📤 CLOUDPEPPER DEPLOYMENT INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "🔄 Method 1: Git Update (Recommended)" -ForegroundColor Yellow
Write-Host "  1. Commit all changes to git:"
Write-Host "     git add frontend_enhancement/"
Write-Host "     git commit -m 'Fix XPath expressions in frontend_enhancement module'"
Write-Host "     git push origin main"
Write-Host ""
Write-Host "  2. In CloudPepper, go to Apps and update the module:"
Write-Host "     - Find 'Frontend Enhancement' module"
Write-Host "     - Click 'Upgrade' button"
Write-Host "     - Wait for completion"
Write-Host ""

Write-Host "🔄 Method 2: Manual Module Reinstall" -ForegroundColor Yellow
Write-Host "  1. In CloudPepper Odoo:"
Write-Host "     - Go to Apps menu"
Write-Host "     - Remove filters, search 'frontend_enhancement'"
Write-Host "     - Click 'Uninstall' if installed"
Write-Host "     - Click 'Install' to reinstall with latest code"
Write-Host ""

Write-Host "🔄 Method 3: Force Registry Reload (Advanced)" -ForegroundColor Yellow
Write-Host "  1. In CloudPepper server terminal:"
Write-Host "     sudo systemctl restart odoo"
Write-Host "     # OR"
Write-Host "     sudo service odoo restart"
Write-Host ""

Write-Host "🧪 VERIFICATION STEPS" -ForegroundColor Cyan
Write-Host "====================="
Write-Host "After deployment, verify in CloudPepper:"
Write-Host "  1. Go to Sales > Orders"
Write-Host "  2. Switch to Kanban view"
Write-Host "  3. Check for client reference display"
Write-Host "  4. Verify no errors in browser console"
Write-Host "  5. Test invoice kanban view as well"
Write-Host ""

Write-Host "🆘 IF ERRORS PERSIST" -ForegroundColor Red
Write-Host "===================="
Write-Host "  1. Check CloudPepper logs: /var/log/odoo/odoo.log"
Write-Host "  2. Clear Odoo cache: rm -rf /tmp/odoo_cache/*"
Write-Host "  3. Restart with cache clear: sudo systemctl restart odoo"
Write-Host "  4. Contact CloudPepper support if needed"
Write-Host ""

Write-Host "✅ Deployment script completed successfully!" -ForegroundColor Green
Write-Host "All files are ready for CloudPepper deployment."
