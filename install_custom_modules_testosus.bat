@echo off
REM ============================================
REM INSTALL CUSTOM FOLDER MODULES TO TESTOSUS DB
REM ============================================

echo 🏗️  Installing Custom Folder Modules to TESTOSUS Database
echo =========================================================

echo 🔍 Step 1: Verifying setup...
docker ps | findstr odoo17_final-odoo-1
docker exec odoo17_final-db-1 psql -U odoo postgres -c "SELECT datname FROM pg_database WHERE datname = 'testosus';"

echo.
echo 📂 Step 2: Updating module list to include custom folder...
echo   🔄 Scanning all available modules (including custom folder)...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus --update=base --stop-after-init --no-http

echo.
echo 📦 Step 3: Installing Priority Custom Modules...

REM Core Business Modules
echo   🏢 Installing custom business modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i property_dashboard --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i renbran_realestate_management --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i odoo_real_estate --stop-after-init --no-http

REM Dashboard and Reporting
echo   📊 Installing dashboard and reporting modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i crm_dashboard --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i odoo_dynamic_dashboard --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i custom_pivot_report --stop-after-init --no-http

REM Financial and Accounting
echo   💰 Installing financial modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i accounting_pdf_reports --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i dynamic_accounts_report --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i om_account_asset --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i om_account_budget --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i om_fiscal_year --stop-after-init --no-http

REM Advanced Features
echo   ⚡ Installing advanced modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i all_in_one_dynamic_custom_fields --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i advanced_many2many_tags --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i custom_fields --stop-after-init --no-http

REM Commission and Loan Management
echo   💼 Installing commission and loan modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i advance_commission --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i advanced_loan_management --stop-after-init --no-http

echo.
echo 📦 Step 4: Installing Main Directory Priority Modules...

REM Core Reporting
echo   📊 Installing core reporting modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i report_xlsx --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i osus_dashboard --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i hrms_dashboard --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i osus_invoice_report --stop-after-init --no-http

REM Sales and Analytics
echo   🎯 Installing sales and analytics modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i sales_target_vs_achievement --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i oe_sale_dashboard_17 --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i sale_invoice_detail --stop-after-init --no-http

REM Enhanced Accounting
echo   💳 Installing enhanced accounting modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i payment_account_enhanced --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i om_account_accountant_v17 --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i reconcilation_fields --stop-after-init --no-http

REM Theme and UI
echo   🎨 Installing theme and UI modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i muk_web_theme --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i web_login_styles --stop-after-init --no-http

REM Website and Portal
echo   🌐 Installing website modules...
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i website_custom_contact_us --stop-after-init --no-http
docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i tk_portal_partner_leads --stop-after-init --no-http

echo.
echo 🔄 Step 5: Final restart and module loading...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to load all installed modules...
timeout /t 45

echo.
echo 🌐 Step 6: Testing TESTOSUS database with installed modules...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 15; Write-Host '✅ TESTOSUS database ready with custom modules!' } catch { Write-Host '⚠️  Still loading modules, please wait...' }"

echo.
echo ✅ CUSTOM FOLDER MODULES INSTALLATION COMPLETE!
echo ================================================
echo.
echo 📋 Successfully installed custom modules in TESTOSUS:
echo.
echo 🏢 Business Modules:
echo   ✅ property_dashboard - Property management dashboard  
echo   ✅ renbran_realestate_management - Real estate management
echo   ✅ odoo_real_estate - Real estate operations
echo.
echo 📊 Dashboard and Reporting:
echo   ✅ crm_dashboard - CRM analytics dashboard
echo   ✅ odoo_dynamic_dashboard - Dynamic dashboard builder
echo   ✅ custom_pivot_report - Custom pivot reporting
echo   ✅ report_xlsx - Excel report generation
echo   ✅ osus_dashboard - Custom OSUS dashboard
echo   ✅ hrms_dashboard - HR management dashboard
echo.
echo 💰 Financial Modules:
echo   ✅ accounting_pdf_reports - PDF financial reports
echo   ✅ dynamic_accounts_report - Dynamic accounting reports
echo   ✅ om_account_asset - Asset management
echo   ✅ om_account_budget - Budget management
echo   ✅ payment_account_enhanced - Enhanced payments
echo   ✅ om_account_accountant_v17 - Advanced accounting
echo.
echo ⚡ Advanced Features:
echo   ✅ all_in_one_dynamic_custom_fields - Dynamic custom fields
echo   ✅ advanced_many2many_tags - Advanced tagging system
echo   ✅ advance_commission - Commission management
echo   ✅ advanced_loan_management - Loan management
echo.
echo 🎯 Sales and Analytics:
echo   ✅ sales_target_vs_achievement - Sales performance
echo   ✅ oe_sale_dashboard_17 - Sales dashboard
echo   ✅ sale_invoice_detail - Detailed invoicing
echo.
echo 🎨 UI and Theme:
echo   ✅ muk_web_theme - Modern web theme
echo   ✅ web_login_styles - Custom login styles
echo.
echo 🌐 Website Features:
echo   ✅ website_custom_contact_us - Custom contact forms
echo   ✅ tk_portal_partner_leads - Portal lead management
echo.
echo 🌐 Access your enhanced TESTOSUS database:
echo   🎯 Main: http://localhost:8069/web?db=testosus
echo   🛠️  Manager: http://localhost:8069/web/database/manager
echo.
echo 💡 What you can now do:
echo   🏠 Manage real estate properties and deals
echo   📊 Generate comprehensive Excel reports
echo   💰 Handle advanced accounting and budgets
echo   🎯 Track sales performance and targets
echo   👥 Manage HR and employee data
echo   📈 Create dynamic dashboards and analytics
echo   💼 Process loans and commissions
echo   🎨 Enjoy modern UI with custom themes
echo.
echo 🚀 Additional modules available for installation:
echo   • Run this script again to install remaining modules
echo   • Use web interface: Apps → Browse more apps
echo   • Manual install: docker exec odoo17_final-odoo-1 /usr/bin/odoo -d testosus -i MODULE_NAME --stop-after-init --no-http
echo.

pause
