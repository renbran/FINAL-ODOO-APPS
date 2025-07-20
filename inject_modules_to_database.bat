@echo off
REM ============================================
REM MODULE INJECTION SCRIPT FOR NEW/RESTORED DATABASES
REM ============================================

echo 🚀 Module Injection to New/Restored Database
echo =============================================

set DATABASE_NAME=%1
if "%DATABASE_NAME%"=="" set DATABASE_NAME=propertyosus

echo 📋 Database Target: %DATABASE_NAME%
echo.

echo 📦 Available Module Sets:
echo 1. 🎯 CORE MODULES (Essential for basic functionality)
echo    - report_xlsx, report_pdf_options, osus_dashboard, hrms_dashboard
echo.
echo 2. 💼 BUSINESS MODULES (Business logic and workflows)  
echo    - payment_account_enhanced, automated_employee_announce, calendar_extended
echo.
echo 3. 📊 REPORTING MODULES (Advanced reports and analytics)
echo    - osus_invoice_report, oe_sale_dashboard_17, sales_target_vs_achievement
echo.
echo 4. 🎨 UI/THEME MODULES (User interface enhancements)
echo    - muk_web_theme, muk_web_colors, theme_levelup
echo.
echo 5. 🚀 ALL MODULES (Complete injection)
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" goto CORE_MODULES
if "%choice%"=="2" goto BUSINESS_MODULES  
if "%choice%"=="3" goto REPORTING_MODULES
if "%choice%"=="4" goto UI_MODULES
if "%choice%"=="5" goto ALL_MODULES

echo ❌ Invalid choice. Exiting...
pause
exit /b 1

:CORE_MODULES
echo 💉 Injecting CORE modules...
set MODULES=report_xlsx,report_pdf_options,osus_dashboard,hrms_dashboard
goto INJECT

:BUSINESS_MODULES
echo 💉 Injecting BUSINESS modules...
set MODULES=payment_account_enhanced,automated_employee_announce,calendar_extended,reconcilation_fields,order_status_override
goto INJECT

:REPORTING_MODULES
echo 💉 Injecting REPORTING modules...
set MODULES=osus_invoice_report,oe_sale_dashboard_17,sales_target_vs_achievement,statement_report
goto INJECT

:UI_MODULES
echo 💉 Injecting UI/THEME modules...
set MODULES=muk_web_theme,muk_web_colors,theme_levelup,muk_web_dialog
goto INJECT

:ALL_MODULES
echo 💉 Injecting ALL modules...
set MODULES=report_xlsx,report_pdf_options,osus_dashboard,hrms_dashboard,payment_account_enhanced,automated_employee_announce,calendar_extended,reconcilation_fields,osus_invoice_report,oe_sale_dashboard_17,muk_web_theme
goto INJECT

:INJECT
echo.
echo 🔄 INJECTION PROCESS STARTING...
echo ================================

echo ⏹️  Step 1: Stopping current Odoo instance...
docker-compose stop odoo
if errorlevel 1 (
    echo ❌ Failed to stop Odoo
    pause
    exit /b 1
)

echo 🗄️  Step 2: Starting database service only...
docker-compose up -d db
timeout /t 5 >nul

echo 💉 Step 3: Injecting modules: %MODULES%
echo    This may take several minutes...

REM Use docker run to inject modules into the database
docker run --rm --network odoo17_final_default ^
    -v "%CD%:/mnt/extra-addons" ^
    -e HOST=db ^
    -e USER=odoo ^
    -e PASSWORD=odoo ^
    odoo:17.0 ^
    odoo -d %DATABASE_NAME% -i %MODULES% --stop-after-init --load-language=en_US

if errorlevel 1 (
    echo ❌ Module injection failed!
    echo 🔧 Trying alternative injection method...
    
    REM Alternative: Start Odoo and inject via exec
    docker-compose up -d odoo
    timeout /t 10 >nul
    docker exec odoo17_final-odoo-1 odoo -d %DATABASE_NAME% -i %MODULES% --stop-after-init
)

echo 🔄 Step 4: Starting full Odoo stack...
docker-compose up -d
timeout /t 15 >nul

echo.
echo ✅ MODULE INJECTION COMPLETE!
echo =============================
echo 🌐 Access your database at: http://localhost:8069/web?db=%DATABASE_NAME%
echo 📋 Injected modules: %MODULES%
echo.
echo 💡 Next steps:
echo    1. Go to Apps menu in Odoo
echo    2. Click "Update Apps List"  
echo    3. Your modules should now be available
echo.

pause
