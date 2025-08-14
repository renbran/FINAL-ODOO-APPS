# CloudPepper Emergency Restart and Asset Reload Script (Windows)

Write-Host "🚨 CLOUDPEPPER EMERGENCY RESTART SEQUENCE" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red

# Step 1: Clear local cache
Write-Host "📁 Clearing local cache..." -ForegroundColor Yellow
Remove-Item -Path "$env:TEMP\*odoo*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\*odoo*" -Recurse -Force -ErrorAction SilentlyContinue

# Step 2: Browser cache clearing instruction  
Write-Host "🌐 BROWSER CACHE CLEARING REQUIRED:" -ForegroundColor Cyan
Write-Host "   1. Open browser" -ForegroundColor White
Write-Host "   2. Press Ctrl+Shift+R (hard refresh)" -ForegroundColor White
Write-Host "   3. Or press F12 then Application then Storage then Clear site data" -ForegroundColor White
Write-Host "   4. Or go to Settings then Clear browsing data" -ForegroundColor White

# Step 3: Manual restart instruction for CloudPepper
Write-Host "🔄 CLOUDPEPPER SERVICE RESTART REQUIRED:" -ForegroundColor Yellow
Write-Host "   CloudPepper hosting requires manual restart through control panel" -ForegroundColor White
Write-Host "   1. Log into CloudPepper control panel" -ForegroundColor White
Write-Host "   2. Go to your Odoo instance" -ForegroundColor White
Write-Host "   3. Click 'Restart' or 'Reboot'" -ForegroundColor White
Write-Host "   4. Wait for service to come back online" -ForegroundColor White

# Step 4: Test sequence
Write-Host "🧪 TESTING SEQUENCE:" -ForegroundColor Green
Write-Host "   1. Open https://stagingtry.cloudpepper.site/" -ForegroundColor White
Write-Host "   2. Login with: salescompliance@osusproperties.com" -ForegroundColor White
Write-Host "   3. Open Developer Tools (F12)" -ForegroundColor White
Write-Host "   4. Go to Console tab" -ForegroundColor White
Write-Host "   5. Look for '[EMERGENCY]' or '[CloudPepper Nuclear]' messages" -ForegroundColor White
Write-Host "   6. Navigate to Payments then Payment Vouchers" -ForegroundColor White
Write-Host "   7. Check for JavaScript errors" -ForegroundColor White

Write-Host ""
Write-Host "⚡ MANUAL BROWSER FIX AVAILABLE:" -ForegroundColor Magenta
Write-Host "   If errors persist after restart:" -ForegroundColor White
Write-Host "   1. Open: MANUAL_BROWSER_FIX.js" -ForegroundColor White
Write-Host "   2. Copy entire contents" -ForegroundColor White
Write-Host "   3. Paste into browser console" -ForegroundColor White
Write-Host "   4. Press Enter to execute" -ForegroundColor White
Write-Host "   5. Watch for protection messages" -ForegroundColor White

Write-Host ""
Write-Host "✅ PREPARATION COMPLETE" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host "Now restart CloudPepper service and test!" -ForegroundColor Yellow
