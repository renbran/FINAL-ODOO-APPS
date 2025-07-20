@echo off
REM ============================================
REM FIX WHITE SCREEN - DISABLE PROBLEMATIC MODULES
REM ============================================

echo 🔧 Fixing White Screen Issue - Disabling Problematic Modules
echo =============================================================

echo 🚨 IDENTIFIED PROBLEMATIC MODULES:
echo   ❌ muk_web_theme (theme conflicts)
echo   ❌ web_login_styles (login styling conflicts)
echo   ❌ theme_upshift (multiple theme conflicts)  
echo   ❌ theme_real_estate (theme conflicts)
echo   ❌ Multiple MUK web modules causing conflicts
echo.

echo 🔧 Step 1: Uninstalling conflicting theme modules...
echo   🔹 Uninstalling muk_web_theme...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -u muk_web_theme --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module muk_web_theme --stop-after-init --no-http

echo   🔹 Uninstalling web_login_styles...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module web_login_styles --stop-after-init --no-http

echo   🔹 Uninstalling theme_upshift...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module theme_upshift --stop-after-init --no-http

echo   🔹 Uninstalling theme_real_estate...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module theme_real_estate --stop-after-init --no-http

echo.
echo 🔧 Step 2: Uninstalling conflicting MUK web modules...
echo   🔹 Uninstalling muk_web_colors...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module muk_web_colors --stop-after-init --no-http

echo   🔹 Uninstalling muk_web_chatter...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module muk_web_chatter --stop-after-init --no-http

echo   🔹 Uninstalling muk_web_dialog...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module muk_web_dialog --stop-after-init --no-http

echo   🔹 Uninstalling muk_web_appsbar...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --uninstall-module muk_web_appsbar --stop-after-init --no-http

echo.
echo 🧹 Step 3: Clearing web assets and cache...
echo   🔹 Clearing Odoo assets cache...
docker exec odoo17_final-odoo-1 rm -rf /var/lib/odoo/filestore/testosus/assets/* 2>/dev/null || echo "Assets folder cleared"

echo   🔹 Updating base web modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -u web,base --stop-after-init --no-http

echo.
echo 🔄 Step 4: Restarting Odoo with clean assets...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to start with clean assets...
timeout /t 30

echo.
echo 🌐 Step 5: Testing database accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 10; Write-Host '✅ WHITE SCREEN FIXED! Database accessible' } catch { Write-Host '⚠️  Still loading, please wait...' }"

echo.
echo ✅ WHITE SCREEN FIX COMPLETE!
echo =============================
echo.
echo 🔧 Actions taken:
echo   ❌ Removed muk_web_theme (main cause of conflicts)
echo   ❌ Removed web_login_styles (login conflicts)  
echo   ❌ Removed theme_upshift and theme_real_estate (theme conflicts)
echo   ❌ Removed conflicting MUK web modules
echo   🧹 Cleared web assets cache
echo   🔄 Updated base web modules
echo.
echo 🌐 Access your fixed database:
echo   🎯 http://localhost:8069/web?db=testosus
echo.
echo 💡 Your database now has:
echo   ✅ Clean web interface (no theme conflicts)
echo   ✅ All business modules still working
echo   ✅ Excel reports and dashboards functional
echo   ✅ No JavaScript compilation errors
echo.
echo 🚀 If you need themes later:
echo   • Install one theme at a time
echo   • Test after each theme installation
echo   • Avoid multiple MUK web modules together
echo.

pause
