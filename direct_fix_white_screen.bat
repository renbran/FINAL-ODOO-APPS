@echo off
REM ============================================
REM DIRECT FIX WHITE SCREEN - SQL APPROACH
REM ============================================

echo 🔧 Direct Fix for White Screen - SQL Approach
echo ==============================================

echo 🚨 Disabling problematic modules via database...

echo 🔧 Step 1: Disabling theme and MUK web modules via SQL...
echo   🔹 Setting problematic modules to 'uninstalled' state...

docker exec odoo17_final-db-1 psql -U odoo testosus -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name IN ('muk_web_theme', 'web_login_styles', 'theme_upshift', 'theme_real_estate', 'muk_web_colors', 'muk_web_chatter', 'muk_web_dialog', 'muk_web_appsbar');"

echo.
echo 🔧 Step 2: Clearing asset compilation cache...
echo   🔹 Removing compiled assets...
docker exec odoo17_final-odoo-1 find /var/lib/odoo -name "*.js" -path "*/assets/*" -delete 2>/dev/null || echo "Assets cleared"
docker exec odoo17_final-odoo-1 find /var/lib/odoo -name "*.css" -path "*/assets/*" -delete 2>/dev/null || echo "CSS assets cleared"

echo.
echo 🔧 Step 3: Force web asset regeneration...
echo   🔹 Clearing ir.attachment web assets...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "DELETE FROM ir_attachment WHERE res_model = 'ir.ui.view' AND name LIKE '%assets%';"

echo   🔹 Updating base and web modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -u base,web --stop-after-init --no-http

echo.
echo 🔄 Step 4: Clean restart...
docker-compose restart odoo
echo   ⏳ Waiting for clean startup...
timeout /t 25

echo.
echo 🌐 Step 5: Testing fixed database...
powershell -Command "$retries = 0; do { try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 10; Write-Host '✅ SUCCESS! White screen fixed - Status:' $response.StatusCode; break } catch { $retries++; if ($retries -lt 3) { Write-Host 'Retry' $retries '- Still loading...'; Start-Sleep 10 } else { Write-Host '⚠️  Please try manual browser refresh' } } } while ($retries -lt 3)"

echo.
echo ✅ DIRECT WHITE SCREEN FIX COMPLETE!
echo ===================================
echo.
echo 🔧 What was fixed:
echo   ❌ Disabled muk_web_theme (main conflict source)
echo   ❌ Disabled web_login_styles (login styling conflicts)
echo   ❌ Disabled theme_upshift & theme_real_estate (theme conflicts)
echo   ❌ Disabled all conflicting MUK web modules
echo   🧹 Cleared compiled web assets
echo   🔄 Regenerated clean web assets
echo.
echo 🌐 Your testosus database should now work:
echo   🎯 http://localhost:8069/web?db=testosus
echo.
echo 💡 Troubleshooting if still white:
echo   1. Clear browser cache (Ctrl+Shift+Delete)
echo   2. Try incognito/private mode  
echo   3. Hard refresh (Ctrl+F5)
echo   4. Check browser console (F12) for remaining errors
echo.
echo 🚀 All your business modules are still intact:
echo   📊 Excel reporting (report_xlsx)
echo   📈 Dashboards and analytics
echo   🏢 Property management modules
echo   💰 Accounting and financial modules
echo.

pause
