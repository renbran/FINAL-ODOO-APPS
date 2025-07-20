@echo off
REM ============================================
REM EMERGENCY RESTORE - FIX 500 ERROR
REM ============================================

echo 🚨 Emergency Fix for 500 Error - Restoring Database
echo ===================================================

echo 🔧 Step 1: Re-enabling essential web modules that were disabled...
echo   🔹 Re-enabling core web modules...

docker exec odoo17_final-db-1 psql -U odoo testosus -c "UPDATE ir_module_module SET state = 'installed' WHERE name IN ('web', 'base', 'web_editor', 'web_tour') AND state != 'installed';"

echo   🔹 Keeping problematic theme modules disabled but restoring dependencies...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "UPDATE ir_module_module SET state = 'installed' WHERE name IN ('theme_common') AND state != 'installed';"

echo.
echo 🔧 Step 2: Checking current module states...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT name, state FROM ir_module_module WHERE name LIKE '%web%' OR name LIKE '%theme%' ORDER BY name;"

echo.
echo 🔧 Step 3: Force update essential modules...
echo   🔹 Updating base, web, and essential modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -u base,web,web_editor --stop-after-init --no-http

echo.
echo 🔄 Step 4: Restart with essential modules...
docker-compose restart odoo
echo   ⏳ Waiting for proper startup...
timeout /t 30

echo.
echo 🌐 Step 5: Testing database recovery...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 15; Write-Host '✅ Database Status:' $response.StatusCode } catch { Write-Host '❌ Still getting errors - Status:' $_.Exception.Message }"

echo.
echo 🔧 If still 500 error, reverting to propertyosus database...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=propertyosus' -Method Head -TimeoutSec 10; Write-Host '✅ PropertyOSUS Status:' $response.StatusCode } catch { Write-Host '❌ PropertyOSUS also has issues' }"

echo.
echo 💡 EMERGENCY RECOVERY STATUS
echo ============================
echo   If testosus still shows 500 error:
echo   1. Use propertyosus database instead
echo   2. We'll create a fresh testosus database
echo   3. Import only essential modules step by step
echo.
echo 🌐 Access points to try:
echo   🎯 TestOSUS: http://localhost:8069/web?db=testosus
echo   🔗 PropertyOSUS: http://localhost:8069/web?db=propertyosus
echo   🛠️  Manager: http://localhost:8069/web/database/manager
echo.

pause
