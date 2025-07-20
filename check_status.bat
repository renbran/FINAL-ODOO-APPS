@echo off
echo 🔍 Odoo System Status Check
echo ===========================
echo.

echo 📊 Docker Services Status:
docker-compose ps
echo.

echo 🗄️ Available Databases:
docker exec -it odoo17_final-db-1 psql -U odoo -d postgres -c "\l"
echo.

echo 🌐 Web Interface Test:
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web/database/selector' -UseBasicParsing -TimeoutSec 5; Write-Host '✅ Web interface accessible (HTTP' $response.StatusCode ')' } catch { Write-Host '❌ Web interface not accessible:' $_.Exception.Message }"
echo.

echo 📋 Recent Errors (last 10 lines):
docker exec -i odoo17_final-db-1 psql -U odoo -d postgres -c "SELECT datname as database_name FROM pg_database WHERE datistemplate = false AND datname != 'postgres';" 2>nul
echo.

echo 📁 Module Status:
if exist "d:\odoo17_final\custom\hide_menu_user.disabled" (
    echo ⚠️  hide_menu_user module is disabled
) else if exist "d:\odoo17_final\custom\hide_menu_user" (
    echo ✅ hide_menu_user module is active
) else (
    echo ❌ hide_menu_user module not found
)
echo.

pause
