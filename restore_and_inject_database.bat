@echo off
REM ============================================
REM DATABASE RESTORE + MODULE INJECTION SCRIPT
REM ============================================

echo 🗄️  Database Restore + Module Injection Tool
echo ============================================

set DATABASE_NAME=%1
if "%DATABASE_NAME%"=="" (
    set /p DATABASE_NAME="Enter database name to restore/create: "
)

echo 📋 Target Database: %DATABASE_NAME%
echo.

echo 📦 Choose restoration method:
echo 1. 🆕 CREATE NEW empty database + inject modules
echo 2. 📁 RESTORE from backup file + inject modules  
echo 3. 🔄 RESET existing database + inject modules
echo.

set /p restore_choice="Select option (1-3): "

if "%restore_choice%"=="1" goto CREATE_NEW
if "%restore_choice%"=="2" goto RESTORE_BACKUP
if "%restore_choice%"=="3" goto RESET_EXISTING

echo ❌ Invalid choice. Exiting...
pause
exit /b 1

:CREATE_NEW
echo 🆕 Creating new database: %DATABASE_NAME%
echo ⏹️  Stopping Odoo...
docker-compose stop odoo

echo 🗄️  Starting database service...
docker-compose up -d db
timeout /t 5 >nul

echo 🆕 Creating empty database...
docker run --rm --network odoo17_final_default ^
    -e HOST=db ^
    -e USER=odoo ^
    -e PASSWORD=odoo ^
    odoo:17.0 ^
    odoo -d %DATABASE_NAME% --init=base --stop-after-init

if errorlevel 1 (
    echo ❌ Failed to create database
    pause
    exit /b 1
)
goto INJECT_MODULES

:RESTORE_BACKUP
echo 📁 Restore from backup file
set /p backup_file="Enter backup file path (*.sql or *.dump): "

if not exist "%backup_file%" (
    echo ❌ Backup file not found: %backup_file%
    pause
    exit /b 1
)

echo ⏹️  Stopping Odoo...
docker-compose stop odoo

echo 🗄️  Starting database service...
docker-compose up -d db
timeout /t 5 >nul

echo 📥 Restoring database from backup...
REM Determine backup type and restore accordingly
if "%backup_file:~-4%"==".sql" (
    docker exec -i odoo17_final-db-1 psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS %DATABASE_NAME%;"
    docker exec -i odoo17_final-db-1 psql -U odoo -d postgres -c "CREATE DATABASE %DATABASE_NAME%;"
    docker exec -i odoo17_final-db-1 psql -U odoo -d %DATABASE_NAME% < "%backup_file%"
) else (
    docker exec -i odoo17_final-db-1 pg_restore -U odoo -d %DATABASE_NAME% < "%backup_file%"
)

if errorlevel 1 (
    echo ❌ Failed to restore database
    pause
    exit /b 1
)
goto INJECT_MODULES

:RESET_EXISTING
echo 🔄 Resetting existing database: %DATABASE_NAME%
echo ⚠️  WARNING: This will delete all data in %DATABASE_NAME%
set /p confirm="Are you sure? (y/N): "

if not "%confirm%"=="y" if not "%confirm%"=="Y" (
    echo ❌ Operation cancelled
    pause
    exit /b 1
)

echo ⏹️  Stopping Odoo...
docker-compose stop odoo

echo 🗄️  Starting database service...
docker-compose up -d db
timeout /t 5 >nul

echo 🔄 Dropping and recreating database...
docker exec odoo17_final-db-1 psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS %DATABASE_NAME%;"
docker exec odoo17_final-db-1 psql -U odoo -d postgres -c "CREATE DATABASE %DATABASE_NAME%;"

echo 🆕 Initializing fresh database...
docker run --rm --network odoo17_final_default ^
    -e HOST=db ^
    -e USER=odoo ^
    -e PASSWORD=odoo ^
    odoo:17.0 ^
    odoo -d %DATABASE_NAME% --init=base --stop-after-init

goto INJECT_MODULES

:INJECT_MODULES
echo.
echo 💉 MODULE INJECTION PHASE
echo ========================

echo 📦 Available module sets:
echo 1. 🎯 ESSENTIAL (Core functionality)
echo 2. 💼 BUSINESS (Business processes)
echo 3. 📊 REPORTING (Reports and analytics)
echo 4. 🎨 UI/THEMES (User interface)
echo 5. 🚀 EVERYTHING (All modules)
echo.

set /p module_choice="Select modules to inject (1-5): "

if "%module_choice%"=="1" set MODULES=report_xlsx,report_pdf_options,osus_dashboard,hrms_dashboard
if "%module_choice%"=="2" set MODULES=payment_account_enhanced,automated_employee_announce,calendar_extended,reconcilation_fields
if "%module_choice%"=="3" set MODULES=osus_invoice_report,oe_sale_dashboard_17,sales_target_vs_achievement,statement_report  
if "%module_choice%"=="4" set MODULES=muk_web_theme,muk_web_colors,theme_levelup,muk_web_dialog
if "%module_choice%"=="5" set MODULES=report_xlsx,report_pdf_options,osus_dashboard,hrms_dashboard,payment_account_enhanced,automated_employee_announce,calendar_extended,osus_invoice_report,muk_web_theme

echo 💉 Injecting modules: %MODULES%
echo    Please wait, this may take several minutes...

docker run --rm --network odoo17_final_default ^
    -v "%CD%:/mnt/extra-addons" ^
    -e HOST=db ^
    -e USER=odoo ^
    -e PASSWORD=odoo ^
    odoo:17.0 ^
    odoo -d %DATABASE_NAME% -i %MODULES% --stop-after-init --load-language=en_US

if errorlevel 1 (
    echo ⚠️  Primary injection method failed, trying alternative...
    docker-compose up -d odoo
    timeout /t 10 >nul
    docker exec odoo17_final-odoo-1 odoo -d %DATABASE_NAME% -i %MODULES% --stop-after-init
)

echo 🔄 Starting full Odoo stack...
docker-compose up -d
timeout /t 15 >nul

echo.
echo 🎉 DATABASE RESTORE + INJECTION COMPLETE!
echo ========================================
echo 🗄️  Database: %DATABASE_NAME%
echo 💉 Modules: %MODULES%
echo 🌐 Access: http://localhost:8069/web?db=%DATABASE_NAME%
echo.
echo 💡 What to do next:
echo    1. Open the URL above
echo    2. Log in to your database
echo    3. Go to Apps → Update Apps List
echo    4. Your custom modules are now available!
echo.

pause
