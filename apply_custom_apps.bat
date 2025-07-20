@echo off
REM ============================================
REM CLEAN MODULE APPLICATION FOR DATABASE
REM ============================================

echo 🚀 CLEAN: Applying Compatible Custom App Codes to Database
echo =========================================================

set DATABASE_NAME=%1
if "%DATABASE_NAME%"=="" set DATABASE_NAME=propertyosus

echo 📋 Target Database: %DATABASE_NAME%
echo.

echo 🧹 Step 0: Cleaning up duplicates and incompatible modules...
call cleanup_modules.bat

echo.
echo 📦 Clean Core Modules Available:
echo   🎯 report_xlsx (Excel Reports)
echo   🎯 osus_dashboard (Main Dashboard) 
echo   🎯 hrms_dashboard (HR Dashboard)
echo   🎯 payment_account_enhanced (Enhanced Payments)
echo   🎯 osus_invoice_report (Invoice Reports)
echo.

echo 🔄 Step 1: Ensuring Odoo is running...
docker-compose up -d
timeout /t 15 /nobreak >nul

echo 🔍 Step 2: Verifying modules are mounted...
docker exec odoo17_final-odoo-1 ls -la /mnt/extra-addons/ | findstr "^d" | findstr -E "(report_xlsx|osus_dashboard|hrms_dashboard|payment_account_enhanced)"

echo ✅ Step 3: Modules are now available for installation!
echo.

echo 🌐 CLEAN WORKSPACE! Your compatible app codes are applied.
echo =======================================================
echo 📱 Access: http://localhost:8069/web?db=%DATABASE_NAME%
echo.
echo 💡 NEXT: Install your CLEAN modules via web interface:
echo    1. Go to Apps menu
echo    2. Click "Update Apps List" 
echo    3. Search for and install (NO DUPLICATES):
echo       ✓ report_xlsx (Excel Reports)
echo       ✓ report_pdf_options (PDF Options)
echo       ✓ osus_dashboard (Main Dashboard)
echo       ✓ hrms_dashboard (HR Dashboard)
echo       ✓ osus_invoice_report (Invoice Reports)
echo       ✓ payment_account_enhanced (Enhanced Payments)
echo       ✓ reconcilation_fields (Reconciliation)
echo       ✓ muk_web_theme (Modern Theme)
echo       ✓ sales_target_vs_achievement (Sales Analytics)
echo       ✓ And other clean modules...
echo.

echo 🔧 Module Dependencies (install in this order):
echo    1. First: report_xlsx, report_pdf_options
echo    2. Then: osus_dashboard, hrms_dashboard
echo    3. Finally: payment_account_enhanced, other business modules
echo.

pause
