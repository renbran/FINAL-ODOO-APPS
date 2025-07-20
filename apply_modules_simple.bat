@echo off
REM ============================================
REM SIMPLE MODULE APPLICATION SCRIPT
REM ============================================

echo 🚀 Applying Custom Modules to Database
echo ======================================

set DATABASE_NAME=%1
if "%DATABASE_NAME%"=="" set DATABASE_NAME=propertyosus

set MODULES=%2
if "%MODULES%"=="" set MODULES=report_xlsx,osus_dashboard,hrms_dashboard

echo 📋 Database: %DATABASE_NAME%
echo 📦 Modules: %MODULES%
echo.

echo 🔄 Step 1: Restarting Odoo stack...
docker-compose restart

echo ⏳ Step 2: Waiting for services to be ready...
timeout /t 20 /nobreak >nul

echo 💾 Step 3: Registering modules in database...

REM Split modules and register each one
for %%i in (%MODULES%) do (
    echo   🔸 Registering: %%i
    docker exec odoo17_final-db-1 psql -U odoo -d %DATABASE_NAME% -c "INSERT INTO ir_module_module (name, state, author, website, summary, description, category_id, auto_install, application) VALUES ('%%i', 'uninstalled', 'Custom', '', 'Custom Module: %%i', 'Custom Module: %%i', 1, false, true) ON CONFLICT (name) DO UPDATE SET state = 'uninstalled', author = 'Custom', summary = 'Custom Module: %%i', description = 'Custom Module: %%i', application = true;"
)

echo 📱 Step 4: Scanning for module files...
docker exec odoo17_final-odoo-1 ls -la /mnt/extra-addons/

echo.
echo ✅ MODULE APPLICATION COMPLETE!
echo ===============================
echo 🌐 Access: http://localhost:8069/web?db=%DATABASE_NAME%
echo.
echo 💡 Next steps:
echo    1. Go to Apps menu
echo    2. Click "Update Apps List" button  
echo    3. Search for your modules:
for %%i in (%MODULES%) do (
    echo       - %%i
)
echo    4. Click "Install" on each module
echo.
echo 🔧 If modules don't appear, they may need dependencies installed first:
echo    - report_xlsx requires: base
echo    - osus_dashboard requires: report_xlsx, report_pdf_options  
echo    - hrms_dashboard requires: hr, report_xlsx
echo.

pause
