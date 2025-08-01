@echo off
REM CloudPeer Deployment Script for Odoo 17 Sales Dashboard
REM Simple deployment package creator

echo === Odoo 17 Sales Dashboard CloudPeer Deployment ===
echo.

REM Check if we're in the right directory
if not exist "__manifest__.py" (
    echo ERROR: Not in module directory. Please run from oe_sale_dashboard_17 folder.
    pause
    exit /b 1
)

echo [1/4] Validating module files...

REM Check required files
set "missing_files="
if not exist "__manifest__.py" set "missing_files=%missing_files% __manifest__.py"
if not exist "models\sale_dashboard.py" set "missing_files=%missing_files% models\sale_dashboard.py"
if not exist "static\src\js\dashboard.js" set "missing_files=%missing_files% static\src\js\dashboard.js"
if not exist "views\dashboard_views.xml" set "missing_files=%missing_files% views\dashboard_views.xml"

if not "%missing_files%"=="" (
    echo ERROR: Missing required files:%missing_files%
    pause
    exit /b 1
)

echo ✓ All required files present

echo.
echo [2/4] Creating deployment package...

REM Create timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set "package_name=oe_sale_dashboard_17_%timestamp%.zip"
set "temp_dir=%TEMP%\oe_sale_dashboard_17_deploy"
set "package_path=%TEMP%\%package_name%"

REM Clean up temp directory if exists
if exist "%temp_dir%" rmdir /s /q "%temp_dir%"

REM Create temp directory and copy module
mkdir "%temp_dir%"
xcopy /E /I /Q . "%temp_dir%" > nul

echo ✓ Files copied to temporary directory

echo.
echo [3/4] Creating ZIP package...

REM Create ZIP using PowerShell (available on Windows 10+)
powershell -Command "Compress-Archive -Path '%temp_dir%' -DestinationPath '%package_path%' -Force"

if exist "%package_path%" (
    echo ✓ Deployment package created: %package_name%
) else (
    echo ERROR: Failed to create deployment package
    pause
    exit /b 1
)

REM Clean up temp directory
rmdir /s /q "%temp_dir%"

echo.
echo [4/4] CloudPeer Deployment Instructions
echo =========================================
echo.
echo Your deployment package is ready at:
echo %package_path%
echo.
echo MANUAL DEPLOYMENT STEPS:
echo 1. Download the package from: %package_path%
echo 2. Upload to your CloudPeer file manager
echo 3. Extract to /odoo/addons/ directory
echo 4. Set proper permissions (chown odoo:odoo)
echo 5. Go to Odoo Settings → Apps → Update Apps List
echo 6. Search for "OSUS Executive Sales Dashboard"
echo 7. Click Install or Upgrade
echo 8. Test dashboard functionality
echo.
echo POST-DEPLOYMENT CHECKLIST:
echo ✓ Dashboard appears in Sales menu
echo ✓ Charts render correctly with Chart.js
echo ✓ AED currency formatting displays
echo ✓ Commission data from agents/brokers shows
echo ✓ No JavaScript errors in browser console
echo ✓ Data loads with booking_date/sale_value fields
echo.
echo TROUBLESHOOTING:
echo - Check Odoo logs for errors
echo - Clear browser cache if needed
echo - Verify internet access for Chart.js CDN
echo - Test with different date ranges
echo.
echo Package location: %package_path%
echo Ready for CloudPeer upload!
echo.
pause
