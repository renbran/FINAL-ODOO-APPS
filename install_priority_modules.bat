@echo off
REM ============================================
REM INSTALL PRIORITY ODOO MODULES
REM ============================================

echo 📦 Installing Priority Odoo Modules
echo ====================================

echo 🔍 Step 1: Verifying Odoo container...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 📋 Step 2: Installing core reporting modules...

echo   📊 Installing report_xlsx (Excel reports)...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i report_xlsx --stop-after-init --no-http

echo.
echo   📈 Installing osus_dashboard (Custom dashboard)...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i osus_dashboard --stop-after-init --no-http

echo.
echo   👥 Installing hrms_dashboard (HR dashboard)...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i hrms_dashboard --stop-after-init --no-http

echo.
echo   💰 Installing osus_invoice_report (Invoice reporting)...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i osus_invoice_report --stop-after-init --no-http

echo.
echo   🎯 Installing sales_target_vs_achievement (Sales analytics)...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i sales_target_vs_achievement --stop-after-init --no-http

echo.
echo 🔄 Step 3: Restarting Odoo with new modules...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to load new modules...
timeout /t 25

echo.
echo 🌐 Step 4: Testing Odoo accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069' -Method Head -TimeoutSec 10; Write-Host '✅ Odoo ready with new modules!' } catch { Write-Host '⚠️  Still loading, please wait...' }"

echo.
echo ✅ PRIORITY MODULES INSTALLATION COMPLETE!
echo ==========================================
echo 📋 Installed modules:
echo   ✅ report_xlsx - Excel report generation
echo   ✅ osus_dashboard - Custom dashboard with data analytics
echo   ✅ hrms_dashboard - HR management dashboard
echo   ✅ osus_invoice_report - Enhanced invoice reporting
echo   ✅ sales_target_vs_achievement - Sales performance analytics
echo.
echo 🌐 Access your updated Odoo: http://localhost:8069/web?db=propertyosus
echo.
echo 💡 Test your new features:
echo   📊 Generate Excel reports from any list view
echo   📈 Check dashboard for analytics and charts  
echo   👥 HR module for employee management
echo   💰 Enhanced invoice reporting capabilities
echo.
echo 🚀 To install additional modules:
echo   • Use the web interface: Apps → Browse more apps
echo   • Or run: docker exec odoo17_final-odoo-1 /usr/bin/odoo -d propertyosus -i MODULE_NAME --stop-after-init --no-http
echo.

pause
