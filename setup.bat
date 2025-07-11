@echo off
setlocal

REM OSUS Odoo 17 Docker Setup Script for Windows
REM This script helps you set up and manage your Odoo 17 environment with custom modules

echo 🚀 OSUS Odoo 17 Docker Setup
echo ==================================

:menu
echo.
echo Choose an option:
echo 1. Build and start Odoo (first time setup)
echo 2. Start existing containers
echo 3. Stop containers
echo 4. View logs
echo 5. Reset database (WARNING: This will delete all data)
echo 6. Update modules
echo 7. Backup database
echo 8. Restore database
echo 9. Exit
echo.

set /p choice=Enter your choice (1-9): 

if "%choice%"=="1" goto build_and_start
if "%choice%"=="2" goto start_containers
if "%choice%"=="3" goto stop_containers
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto reset_database
if "%choice%"=="6" goto update_modules
if "%choice%"=="7" goto backup_database
if "%choice%"=="8" goto restore_database
if "%choice%"=="9" goto exit_script

echo ❌ Invalid option. Please choose 1-9.
goto menu

:build_and_start
echo 🔨 Building Docker images...
docker-compose build --no-cache
if errorlevel 1 (
    echo ❌ Build failed!
    pause
    goto menu
)

echo 🚀 Starting services...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services!
    pause
    goto menu
)

echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

echo ✅ Services started successfully!
echo 🌐 Odoo is available at: http://localhost:8069
echo 🗄️  Database: PostgreSQL on localhost:5432
echo.
echo 📋 Default credentials:
echo    Database: odoo
echo    Username: admin
echo    Password: admin
pause
goto menu

:start_containers
echo ▶️  Starting existing containers...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start containers!
    pause
    goto menu
)
echo ✅ Containers started!
echo 🌐 Odoo is available at: http://localhost:8069
pause
goto menu

:stop_containers
echo ⏹️  Stopping containers...
docker-compose down
echo ✅ Containers stopped!
pause
goto menu

:view_logs
echo 📋 Viewing Odoo logs (Press Ctrl+C to exit)...
docker-compose logs -f odoo
goto menu

:reset_database
echo ⚠️  WARNING: This will delete ALL data!
set /p confirm=Are you sure you want to reset the database? (yes/no): 

if not "%confirm%"=="yes" (
    echo ❌ Database reset cancelled.
    pause
    goto menu
)

echo 🗑️  Stopping containers...
docker-compose down

echo 🗑️  Removing database volume...
docker volume rm odoo17_final_odoo-db-data 2>nul || echo Volume already removed

echo 🚀 Starting fresh containers...
docker-compose up -d

echo ✅ Database reset complete!
pause
goto menu

:update_modules
echo 🔄 Updating Odoo modules...
docker-compose exec odoo odoo --update=all --stop-after-init
docker-compose restart odoo
echo ✅ Modules updated!
pause
goto menu

:backup_database
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%%dt:~12,2%"
set "backup_file=backup_%timestamp%.sql"

echo 💾 Creating database backup...
docker-compose exec db pg_dump -U odoo odoo > "%backup_file%"
echo ✅ Database backed up to: %backup_file%
pause
goto menu

:restore_database
echo 📋 Available backup files:
dir backup_*.sql /b 2>nul || echo No backup files found
echo.
set /p backup_file=Enter backup file name: 

if not exist "%backup_file%" (
    echo ❌ Backup file not found: %backup_file%
    pause
    goto menu
)

echo 📥 Restoring database from: %backup_file%
docker-compose exec -T db psql -U odoo -d odoo < "%backup_file%"
docker-compose restart odoo
echo ✅ Database restored successfully!
pause
goto menu

:exit_script
echo 👋 Goodbye!
pause
exit /b 0
