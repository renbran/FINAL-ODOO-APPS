@echo off
echo 🔍 Odoo Docker Troubleshooting Guide
echo =====================================
echo.

:menu
echo Choose a troubleshooting option:
echo 1. Check Docker status
echo 2. View Odoo logs
echo 3. View database logs
echo 4. Restart all services
echo 5. Clean up and rebuild
echo 6. Check port availability
echo 7. Reset everything (DANGER: deletes all data)
echo 8. Exit
echo.

set /p choice=Enter your choice (1-8): 

if "%choice%"=="1" goto check_docker
if "%choice%"=="2" goto odoo_logs
if "%choice%"=="3" goto db_logs
if "%choice%"=="4" goto restart_services
if "%choice%"=="5" goto clean_rebuild
if "%choice%"=="6" goto check_ports
if "%choice%"=="7" goto reset_all
if "%choice%"=="8" goto exit_script

echo ❌ Invalid option. Please choose 1-8.
goto menu

:check_docker
echo 📊 Checking Docker status...
docker --version
echo.
docker ps
echo.
docker-compose ps
pause
goto menu

:odoo_logs
echo 📄 Viewing Odoo logs (press Ctrl+C to stop)...
docker-compose logs -f odoo
goto menu

:db_logs
echo 📄 Viewing database logs (press Ctrl+C to stop)...
docker-compose logs -f db
goto menu

:restart_services
echo 🔄 Restarting all services...
docker-compose down
echo ⏳ Waiting 5 seconds...
timeout /t 5 /nobreak >nul
docker-compose up -d
echo ✅ Services restarted!
pause
goto menu

:clean_rebuild
echo 🧹 Cleaning up and rebuilding...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo ✅ Clean rebuild completed!
pause
goto menu

:check_ports
echo 🔌 Checking if ports 8069 and 5432 are available...
netstat -an | findstr :8069
if errorlevel 1 (
    echo ✅ Port 8069 is available
) else (
    echo ❌ Port 8069 is in use
)

netstat -an | findstr :5432
if errorlevel 1 (
    echo ✅ Port 5432 is available
) else (
    echo ❌ Port 5432 is in use
)
pause
goto menu

:reset_all
echo ⚠️  WARNING: This will delete ALL data and containers!
set /p confirm=Are you sure? Type YES to continue: 
if not "%confirm%"=="YES" (
    echo Operation cancelled.
    goto menu
)

echo 🗑️  Removing all containers and volumes...
docker-compose down -v
docker system prune -a -f
echo ✅ Everything has been reset!
pause
goto menu

:exit_script
echo 👋 Goodbye!
exit /b 0
