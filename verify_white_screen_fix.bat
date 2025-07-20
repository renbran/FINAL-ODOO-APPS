@echo off
REM ============================================
REM VERIFY WHITE SCREEN FIX
REM ============================================

echo 🔍 Verifying White Screen Fix
echo =============================

echo 🔍 Step 1: Checking remaining problematic modules...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT name, state FROM ir_module_module WHERE state = 'installed' AND (name LIKE '%muk%' OR name LIKE '%theme%' OR name LIKE '%login%') ORDER BY name;"

echo.
echo 🌐 Step 2: Testing database accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -TimeoutSec 5; Write-Host 'Status:' $response.StatusCode; if ($response.StatusCode -eq 200) { Write-Host '✅ Database is accessible - WHITE SCREEN FIXED!' } } catch { Write-Host '⚠️  Database still loading or issue persists' }"

echo.
echo 📊 Step 3: Checking total installed modules...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT count(*) as remaining_modules FROM ir_module_module WHERE state = 'installed';"

echo.
echo 🔄 Step 4: Checking if Odoo container is running...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 💡 If still having issues:
echo   1. Clear browser cache (Ctrl+F5)
echo   2. Try incognito/private browsing mode
echo   3. Check browser console for JavaScript errors (F12)
echo   4. Wait a bit more for complete startup
echo.

pause
