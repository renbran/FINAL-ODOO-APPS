@echo off
REM ============================================
REM COMPREHENSIVE TESTOSUS DATABASE REPAIR
REM ============================================

echo 🔧 Comprehensive TESTOSUS Database Repair
echo ==========================================

echo 🔍 Step 1: Checking current database state...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT count(*) as total_modules, count(*) FILTER (WHERE state = 'installed') as installed_modules FROM ir_module_module;"

echo.
echo 🔧 Step 2: Restoring essential web modules to installed state...
echo   🔹 Re-enabling critical web modules...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "UPDATE ir_module_module SET state = 'installed' WHERE name IN ('web', 'base', 'web_editor', 'web_tour', 'theme_common', 'website') AND state != 'installed';"

echo   🔹 Ensuring problematic modules stay disabled...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name IN ('muk_web_theme', 'web_login_styles', 'theme_upshift', 'theme_real_estate', 'muk_web_colors', 'muk_web_chatter', 'muk_web_dialog', 'muk_web_appsbar', 'custom_background');"

echo.
echo 🧹 Step 3: Complete database cleanup...
echo   🔹 Clearing all web assets from database...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "DELETE FROM ir_attachment WHERE name LIKE '%.css' OR name LIKE '%.js' OR name LIKE '%assets%';"

echo   🔹 Clearing session data...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "DELETE FROM ir_sessions;"

echo   🔹 Clearing view cache...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "DELETE FROM ir_ui_view WHERE type = 'qweb' AND name LIKE '%assets%';"

echo.
echo 🔄 Step 4: Initialize database with clean modules...
echo   🔹 Stopping Odoo...
docker-compose stop odoo

echo   🔹 Starting with database initialization...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --init=base,web --stop-after-init --no-http --without-demo=all

echo   🔹 Updating essential modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -u base,web,web_editor --stop-after-init --no-http --without-demo=all

echo.
echo 🚀 Step 5: Starting Odoo normally...
docker-compose start odoo
echo   ⏳ Waiting for complete startup...
timeout /t 35

echo.
echo 🌐 Step 6: Testing repaired database...
echo   🔹 Testing testosus database...
powershell -Command "for ($i=1; $i -le 3; $i++) { try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 15; Write-Host 'Attempt' $i ': SUCCESS! Status:' $response.StatusCode; break } catch { Write-Host 'Attempt' $i ': Error -' $_.Exception.Response.StatusCode; if ($i -eq 3) { Write-Host 'Database repair may need manual intervention' } else { Start-Sleep 10 } } }"

echo.
echo 🔧 Step 7: Checking module status after repair...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT count(*) as installed_modules FROM ir_module_module WHERE state = 'installed';"

echo.
echo ✅ TESTOSUS DATABASE REPAIR COMPLETE!
echo ====================================
echo.
echo 🔧 Repair Actions Taken:
echo   🔄 Re-initialized base and web modules
echo   🧹 Cleared all cached web assets
echo   ❌ Disabled all problematic theme modules
echo   🔄 Clean restart with essential modules only
echo.
echo 🌐 Access your repaired database:
echo   🎯 http://localhost:8069/web?db=testosus
echo.
echo 💡 If still having issues:
echo   1. Clear browser cache completely
echo   2. Try incognito/private browsing
echo   3. Check browser console (F12) for specific errors
echo   4. Database manager: http://localhost:8069/web/database/manager
echo.
echo 🚀 Next steps after successful repair:
echo   1. Login to testosus database
echo   2. Go to Apps menu
echo   3. Install modules one by one (avoid themes for now)
echo   4. Test each module after installation
echo.

pause
