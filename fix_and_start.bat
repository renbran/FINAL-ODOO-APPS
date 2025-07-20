@echo off
echo 🔧 Starting Odoo with module upgrade for hide_menu_user...

REM Start only the database first
docker-compose up -d db

echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Run Odoo with upgrade for the problematic module
echo 🔄 Upgrading hide_menu_user module...
docker-compose run --rm odoo odoo -d osusre -u hide_menu_user --stop-after-init

if errorlevel 1 (
    echo ❌ Module upgrade failed, trying to start normally...
) else (
    echo ✅ Module upgrade completed successfully
)

echo 🚀 Starting Odoo normally...
docker-compose up -d

echo.
echo 🌐 Odoo should be available at http://localhost:8069/web?db=osusre
echo.
pause
