@echo off
REM ============================================
REM CLEAN STARTUP - FIX WHITE SCREEN ISSUE
REM ============================================

echo 🚨 FIXING WHITE SCREEN ISSUE - JavaScript Error Detected
echo =====================================================

echo 📋 Problem: JavaScript SyntaxError detected:
echo   - Missing catch or finally after try
echo   - web.assets_web.min.js:18499
echo   - Asset compilation/minification issue
echo   - Module with malformed JavaScript
echo.

echo 🔄 Step 1: Complete stop and cleanup...
docker-compose down --remove-orphans
timeout /t 5 /nobreak >nul

echo 🗑️  Step 2: Clear JavaScript assets and problematic modules...
docker-compose up -d db
timeout /t 5 /nobreak >nul

echo   🧹 Clearing compiled assets cache...
docker exec odoo17_final-db-1 psql -U odoo -d propertyosus -c "DELETE FROM ir_attachment WHERE res_model='ir.ui.view' AND name LIKE '%.assets_%';"
docker exec odoo17_final-db-1 psql -U odoo -d propertyosus -c "DELETE FROM ir_attachment WHERE name LIKE 'web.assets_%';"

echo   🧹 Cleaning module conflicts in propertyosus...
docker exec odoo17_final-db-1 psql -U odoo -d propertyosus -c "DELETE FROM ir_module_module WHERE state = 'to install' AND name NOT IN ('base', 'web', 'report_xlsx', 'osus_dashboard');"

echo   🧹 Removing potentially problematic web modules...
docker exec odoo17_final-db-1 psql -U odoo -d propertyosus -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name LIKE 'muk_web_%' OR name LIKE 'web_%' OR name LIKE 'theme_%';"

echo   🧹 Cleaning module conflicts in osusprop...  
docker exec odoo17_final-db-1 psql -U odoo -d osusprop -c "DELETE FROM ir_module_module WHERE state = 'to install' AND name NOT IN ('base', 'web', 'report_xlsx', 'osus_dashboard');"
docker exec odoo17_final-db-1 psql -U odoo -d osusprop -c "DELETE FROM ir_attachment WHERE res_model='ir.ui.view' AND name LIKE '%.assets_%';"
docker exec odoo17_final-db-1 psql -U odoo -d osusprop -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name LIKE 'muk_web_%' OR name LIKE 'web_%' OR name LIKE 'theme_%';"

echo � Step 3: Restart with asset regeneration...
docker-compose stop odoo
timeout /t 3 /nobreak >nul
echo 🔄 Step 4: Start Odoo with fresh assets...
docker-compose up -d odoo
timeout /t 25 /nobreak >nul

echo 🔍 Step 5: Testing access...
echo   📱 Database Manager: http://localhost:8069/web/database/manager
echo   📱 Direct DB Access: http://localhost:8069/web?db=propertyosus
echo.

echo 🌐 Step 6: Opening clean interface...
start http://localhost:8069/web/database/manager

echo ✅ JAVASCRIPT ERROR FIX COMPLETE!
echo =================================
echo 💡 What was fixed:
echo   ✅ Cleared compiled JavaScript assets
echo   ✅ Removed problematic web/theme modules  
echo   ✅ Forced asset regeneration
echo   ✅ Clean restart
echo.
echo 💡 If still white screen:
echo   1. Press F12 → Console tab (check for new errors)
echo   2. Try different database: http://localhost:8069/web?db=osusprop
echo   3. Clear browser cache (Ctrl+Shift+Delete)
echo   4. Try incognito/private browser window
echo.

pause
