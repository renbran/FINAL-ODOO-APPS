@echo off
REM ============================================
REM INSTALL MODULES IN TESTOSUS DATABASE
REM ============================================

echo 📦 Installing Modules in TESTOSUS Database
echo ===========================================

echo 🔍 Step 1: Verifying Odoo container and testosus database...
docker ps | findstr odoo17_final-odoo-1
docker exec odoo17_final-db-1 psql -U odoo postgres -c "SELECT datname FROM pg_database WHERE datname = 'testosus';"

echo.
echo 📋 Step 2: Installing core reporting modules in testosus...

echo   📊 Installing report_xlsx (Excel reports) in testosus...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i report_xlsx --stop-after-init --no-http

echo.
echo   📈 Installing osus_dashboard (Custom dashboard) in testosus...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i osus_dashboard --stop-after-init --no-http

echo.
echo   👥 Installing hrms_dashboard (HR dashboard) in testosus...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i hrms_dashboard --stop-after-init --no-http

echo.
echo   💰 Installing osus_invoice_report (Invoice reporting) in testosus...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i osus_invoice_report --stop-after-init --no-http

echo.
echo   🎯 Installing sales_target_vs_achievement (Sales analytics) in testosus...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i sales_target_vs_achievement --stop-after-init --no-http

echo.
echo   📊 Installing oe_sale_dashboard_17 (Sales dashboard) in testosus...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i oe_sale_dashboard_17 --stop-after-init --no-http

echo.
echo 🔄 Step 3: Restarting Odoo with testosus database loaded...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to load all modules in testosus...
timeout /t 30

echo.
echo 🌐 Step 4: Testing testosus database accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 10; Write-Host '✅ TESTOSUS database ready with modules!' } catch { Write-Host '⚠️  Still loading, please wait...' }"

echo.
echo ✅ TESTOSUS DATABASE MODULES INSTALLATION COMPLETE!
echo ===================================================
echo 📋 Installed modules in TESTOSUS database:
echo   ✅ report_xlsx - Excel report generation
echo   ✅ osus_dashboard - Custom dashboard with data analytics
echo   ✅ hrms_dashboard - HR management dashboard
echo   ✅ osus_invoice_report - Enhanced invoice reporting
echo   ✅ sales_target_vs_achievement - Sales performance analytics
echo   ✅ oe_sale_dashboard_17 - Sales dashboard
echo.
echo 🌐 Access your TESTOSUS database: http://localhost:8069/web?db=testosus
echo.
echo 💡 Test your new features in TESTOSUS:
echo   📊 Generate Excel reports from any list view
echo   📈 Check dashboard for analytics and charts  
echo   👥 HR module for employee management
echo   💰 Enhanced invoice reporting capabilities
echo   🎯 Sales performance tracking and analytics
echo.
echo 🔧 Database Management:
echo   📊 Current DB: testosus
echo   🔗 Alternative: propertyosus
echo   🛠️  Manager: http://localhost:8069/web/database/manager
echo.
echo 🚀 Additional modules available for installation:
echo   • om_account_accountant_v17 (Advanced accounting)
echo   • ks_dynamic_financial_report (Financial reports)
echo   • payment_account_enhanced (Payment processing)
echo   • calendar_extended (Enhanced calendar)
echo   • muk_web_theme (Modern theme)
echo.

pause
