# OSUS Premium Settings Page Fix - Windows Deployment
# ===================================================

Write-Host "🔧 OSUS Premium Settings Page Fix Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$MODULE_NAME = "osus_premium"
$ODOO_SERVER = "erposus.com"
$ODOO_DB = "odoo"

Write-Host "📋 Fix Summary:" -ForegroundColor Yellow
Write-Host "  ✓ Added osus_settings.scss - Settings page styling"
Write-Host "  ✓ Added settings_fixes.js - Removes rogue Toggle Dropdown button"
Write-Host "  ✓ Updated module version to 17.0.1.0.1"
Write-Host ""

Write-Host "🚀 Deployment Options:" -ForegroundColor Green
Write-Host ""
Write-Host "Option 1 - Via SSH (Recommended):" -ForegroundColor White
Write-Host "  ssh odoo@$ODOO_SERVER" -ForegroundColor Gray
Write-Host "  cd /opt/odoo17/odoo17_final" -ForegroundColor Gray
Write-Host "  git pull origin main" -ForegroundColor Gray
Write-Host "  /opt/odoo17/venv/bin/python3 /opt/odoo17/odoo/odoo-bin -c /etc/odoo17.conf -d $ODOO_DB -u $MODULE_NAME --stop-after-init" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 2 - Via Odoo Web UI:" -ForegroundColor White
Write-Host "  1. Login to https://$ODOO_SERVER" -ForegroundColor Gray
Write-Host "  2. Go to Apps menu" -ForegroundColor Gray
Write-Host "  3. Remove 'Apps' filter, search for '$MODULE_NAME'" -ForegroundColor Gray
Write-Host "  4. Click 'Upgrade' button" -ForegroundColor Gray
Write-Host "  5. Hard refresh browser (Ctrl+Shift+R)" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 3 - Automatic SSH Deployment:" -ForegroundColor White
$response = Read-Host "Do you want to deploy now via SSH? (y/n)"

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "🔄 Connecting to server..." -ForegroundColor Yellow
    
    $commands = @"
cd /opt/odoo17/odoo17_final && 
git pull origin main && 
/opt/odoo17/venv/bin/python3 /opt/odoo17/odoo/odoo-bin -c /etc/odoo17.conf -d $ODOO_DB -u $MODULE_NAME --stop-after-init
"@
    
    ssh "odoo@$ODOO_SERVER" $commands
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📌 Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
        Write-Host "  2. Hard refresh the page (Ctrl+Shift+R)" -ForegroundColor White
        Write-Host "  3. Navigate to Settings page" -ForegroundColor White
        Write-Host "  4. Verify 'Toggle Dropdown' button is gone" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Deployment failed. Please check SSH connection." -ForegroundColor Red
        Write-Host "   Try manual deployment using Option 1 or 2 above." -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host ""
    Write-Host "ℹ️  Deployment skipped. Use one of the options above when ready." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "📚 What the fix does:" -ForegroundColor Cyan
Write-Host "  • Hides empty dropdown toggle buttons in settings" -ForegroundColor White
Write-Host "  • Applies OSUS burgundy & gold styling to settings page" -ForegroundColor White
Write-Host "  • Improves settings container layout and shadows" -ForegroundColor White
Write-Host "  • Styles Save/Discard buttons with OSUS gradient" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
