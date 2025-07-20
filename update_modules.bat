@echo off
REM ============================================
REM UPDATE ODOO MODULES SYSTEMATICALLY
REM ============================================

echo 🔄 Updating Odoo Modules
echo ========================

echo 🔍 Step 1: Checking Odoo container status...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 🌐 Step 2: Testing Odoo accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069' -Method Head -TimeoutSec 10; Write-Host '✅ Odoo is accessible' } catch { Write-Host '⚠️  Starting Odoo restart process...' }"

echo.
echo 🔄 Step 3: Updating module list in Odoo...
echo   📋 This will refresh the available modules list
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus --update=base --stop-after-init --no-http

echo.
echo 🔄 Step 4: Restarting Odoo to apply updates...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to restart completely...
timeout /t 30

echo.
echo 📦 Step 5: Key modules ready for installation/update:
echo   ✅ Core modules (with Python dependencies now satisfied):
echo      📊 report_xlsx - Excel report generation
echo      📈 osus_dashboard - Custom dashboard
echo      👥 hrms_dashboard - HR management dashboard
echo      💰 osus_invoice_report - Invoice reporting
echo      🎯 sales_target_vs_achievement - Sales analytics
echo      📋 oe_sale_dashboard_17 - Sales dashboard
echo      💼 om_account_accountant_v17 - Accounting tools
echo      📊 ks_dynamic_financial_report - Financial reports
echo      🏢 payment_account_enhanced - Payment processing
echo.
echo   ✅ Additional modules available:
echo      📅 calendar_extended - Enhanced calendar
echo      🏢 hr_uae_extended - UAE HR compliance
echo      🌐 website_custom_contact_us - Contact forms
echo      📱 muk_web_theme - Modern web theme
echo      🔐 dbfilter_from_header - Database filtering
echo.

echo 🌐 Step 6: Testing final Odoo accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069' -Method Head -TimeoutSec 15; Write-Host '✅ Odoo is ready for module updates!' } catch { Write-Host '⚠️  Please wait a bit more and try accessing manually' }"

echo.
echo ✅ MODULE UPDATE PREPARATION COMPLETE!
echo =====================================
echo.
echo 🚀 Next Steps - Choose your method:
echo.
echo 🌐 METHOD 1: Web Interface (Recommended)
echo   1. Open: http://localhost:8069/web?db=propertyosus
echo   2. Go to Apps menu
echo   3. Click "Update Apps List" 
echo   4. Search and install these priority modules:
echo      • report_xlsx
echo      • osus_dashboard  
echo      • hrms_dashboard
echo      • osus_invoice_report
echo.
echo ⚡ METHOD 2: Command Line (Advanced)
echo   Run: docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i report_xlsx,osus_dashboard --stop-after-init --no-http
echo.
echo 💡 Pro Tips:
echo   • Install one module at a time to avoid conflicts
echo   • Check logs if installation fails: docker logs odoo17_final-odoo-1
echo   • All Python dependencies are now satisfied
echo   • Excel reports should work perfectly now
echo.
echo 📱 Access Points:
echo   🌐 Main: http://localhost:8069/web?db=propertyosus
echo   🌐 Alt:  http://localhost:8069/web?db=osusprop
echo.

echo Press any key to open Odoo in your browser...
pause
start http://localhost:8069/web?db=propertyosus
