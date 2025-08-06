@echo off
REM Enhanced REST API Installation Script for Windows
echo.
echo 🚀 Enhanced REST API for Odoo 17 - Windows Installation Script
echo ================================================================
echo.

REM Check if we're in the right directory
if not exist "enhanced_rest_api\__manifest__.py" (
    echo ❌ Error: Please run this script from the odoo17_final directory
    pause
    exit /b 1
)

echo ✅ Found enhanced_rest_api module
echo.

REM Check Python dependencies
echo 📦 Checking Python dependencies...
python -c "import jwt" 2>nul
if errorlevel 1 (
    echo ⚠️  PyJWT not found. Installing...
    pip install PyJWT
) else (
    echo ✅ PyJWT is installed
)

python -c "import requests" 2>nul
if errorlevel 1 (
    echo ⚠️  requests not found. Installing...
    pip install requests
) else (
    echo ✅ requests is installed
)

echo.
echo 🎉 Enhanced REST API Installation Complete!
echo.
echo 📋 Next Steps:
echo 1. Update your odoo.conf file to include:
echo    server_wide_modules = web, base, rest_api_odoo, enhanced_rest_api
echo 2. Restart your Odoo server
echo 3. Go to Apps ^> Update Apps List
echo 4. Search for 'Enhanced REST API'
echo 5. Install the module
echo 6. Configure API endpoints in Settings
echo.
echo 📚 Documentation:
echo - Module README: enhanced_rest_api\README.md
echo - Postman Collection: enhanced_rest_api\postman\Enhanced_REST_API_Collection.json
echo.
echo 🔗 API Endpoints will be available at:
echo - Health Check: http://localhost:8069/api/v1/status
echo - Generate API Key: http://localhost:8069/api/v1/auth/generate-key
echo - CRM APIs: http://localhost:8069/api/v1/crm/*
echo - Sales APIs: http://localhost:8069/api/v1/sales/*
echo - Payment APIs: http://localhost:8069/api/v1/payments/*
echo.
echo ⚡ Enjoy your enhanced REST API experience!
echo.
pause
