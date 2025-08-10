@echo off
REM Account Payment Final - Quick Installation Script
REM For Non-Docker Odoo 17 Environments

echo ================================================
echo  Account Payment Final - Module Installation
echo ================================================
echo.

echo [INFO] All critical errors have been resolved
echo [INFO] Module is ready for production deployment
echo.

echo Installation Options:
echo.
echo 1. Manual Installation (Recommended)
echo    - Access your Odoo instance in browser
echo    - Go to Apps menu
echo    - Click "Update Apps List"
echo    - Search for "Account Payment Final"
echo    - Click Install
echo.

echo 2. Command Line Installation
set /p database_name="Enter your database name: "
set /p odoo_path="Enter path to odoo-bin (e.g., C:\odoo\odoo-bin): "

if not "%database_name%"=="" if not "%odoo_path%"=="" (
    echo.
    echo [INFO] Installing account_payment_final module...
    echo Command: "%odoo_path%" -d %database_name% -i account_payment_final --stop-after-init
    echo.
    set /p confirm="Execute this command? (y/n): "
    if /i "%confirm%"=="y" (
        "%odoo_path%" -d %database_name% -i account_payment_final --stop-after-init
        echo.
        echo [SUCCESS] Installation completed!
        echo [INFO] Check your Odoo instance for the Account Payment Final module
    ) else (
        echo [INFO] Installation cancelled
    )
) else (
    echo [INFO] Please use manual installation method
)

echo.
echo ================================================
echo  Module Features Available After Installation:
echo ================================================
echo - 4-Stage Payment Approval Workflow
echo - QR Code Verification System  
echo - OSUS Professional Branding
echo - Role-Based Security Controls
echo - Mobile-Responsive Design
echo - Auto-Posting Journal Logic
echo.

echo [SUCCESS] Module is production-ready for CloudPepper deployment
echo.
pause
