@echo off
REM ============================================
REM DETECT PROBLEMATIC MODULES CAUSING WHITE SCREEN
REM ============================================

echo 🔍 Detecting Problematic Modules - White Screen Issue
echo ====================================================

echo 🚨 Step 1: Checking Odoo logs for JavaScript errors...
docker logs --tail 50 odoo17_final-odoo-1 | findstr /i "error\|exception\|traceback\|failed"

echo.
echo 🔍 Step 2: Checking for asset compilation errors...
docker logs --tail 100 odoo17_final-odoo-1 | findstr /i "asset\|js\|css\|webpack\|bundle"

echo.
echo 📋 Step 3: Listing recently installed modules that might cause conflicts...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT name, state, latest_version FROM ir_module_module WHERE state = 'installed' AND name LIKE '%web%' OR name LIKE '%theme%' OR name LIKE '%muk%' ORDER BY name;"

echo.
echo 🔍 Step 4: Checking for problematic web modules...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT name FROM ir_module_module WHERE state = 'installed' AND (name LIKE '%js%' OR name LIKE '%asset%' OR name LIKE '%frontend%' OR name LIKE '%ui%');"

echo.
echo 🚨 Step 5: Common problematic modules for white screen:
echo   - muk_web_theme (theme conflicts)
echo   - web_login_styles (login styling conflicts)  
echo   - custom_background (background conflicts)
echo   - theme modules (multiple theme conflicts)
echo   - JavaScript compilation errors
echo.
echo 💡 Next steps will be to disable problematic modules...
echo.

pause
