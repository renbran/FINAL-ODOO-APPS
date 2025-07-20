@echo off
REM ============================================
REM WHITE SCREEN FIX VERIFICATION
REM ============================================

echo ✅ VERIFYING WHITE SCREEN FIX
echo =============================

echo 🔍 Step 1: Checking Odoo service status...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 🔍 Step 2: Testing HTTP response...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069' -Method Head -TimeoutSec 10; Write-Host '✅ HTTP Status:' $response.StatusCode $response.StatusDescription } catch { Write-Host '❌ Connection failed:' $_.Exception.Message }"

echo.
echo 🔍 Step 3: Opening test URLs...
echo   📱 Database Manager: http://localhost:8069/web/database/manager
start http://localhost:8069/web/database/manager

timeout /t 3 /nobreak >nul

echo   📱 Database propertyosus: http://localhost:8069/web?db=propertyosus
start http://localhost:8069/web?db=propertyosus

echo.
echo ✅ VERIFICATION COMPLETE!
echo ========================
echo 💡 What to check in the browser:
echo   ✅ No more white screen
echo   ✅ No JavaScript errors in console (F12)
echo   ✅ Database manager loads properly
echo   ✅ Login screen appears
echo.
echo 🚨 If you STILL see white screen:
echo   1. Press F12 and check Console tab for new errors
echo   2. Clear browser cache completely (Ctrl+Shift+Delete)
echo   3. Try incognito/private browser window
echo   4. Try different browser (Chrome/Firefox/Edge)
echo.
echo 🎯 Next Steps (if working):
echo   1. Log into database
echo   2. Go to Apps → Update Apps List  
echo   3. Install your cleaned modules:
echo      - report_xlsx
echo      - osus_dashboard
echo      - hrms_dashboard
echo.

pause
