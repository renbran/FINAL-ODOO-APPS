@echo off
REM Announcement Banner Enhancement Deployment Script for Windows

echo.
echo ========================================
echo  Deploying Announcement Banner Enhancements
echo ========================================
echo.

REM Check if docker-compose is available
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] docker-compose not found. Please install Docker Desktop.
    pause
    exit /b 1
)

echo [INFO] Changes being deployed:
echo   1. Enhanced title contrast and readability
echo   2. Fixed HTML content sanitization
echo   3. Improved WYSIWYG editor configuration
echo.

REM Step 1: Check if Odoo container is running
echo [INFO] Checking Odoo container status...
docker-compose ps | findstr /C:"odoo" | findstr /C:"Up" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Odoo container is not running. Starting services...
    docker-compose up -d
    timeout /t 10 /nobreak >nul
) else (
    echo [OK] Odoo container is running
)
echo.

REM Step 2: Update the module
echo [INFO] Updating announcement_banner module...
docker-compose exec -T odoo odoo --update=announcement_banner --stop-after-init -d odoo

if %ERRORLEVEL% EQU 0 (
    echo [OK] Module updated successfully
) else (
    echo [ERROR] Module update failed. Check logs for details.
    echo.
    echo View logs with: docker-compose logs -f odoo
    pause
    exit /b 1
)
echo.

REM Step 3: Restart Odoo
echo [INFO] Restarting Odoo service...
docker-compose restart odoo

if %ERRORLEVEL% EQU 0 (
    echo [OK] Odoo restarted successfully
) else (
    echo [ERROR] Failed to restart Odoo
    pause
    exit /b 1
)
echo.

REM Step 4: Wait for Odoo to start
echo [INFO] Waiting for Odoo to start (30 seconds)...
timeout /t 30 /nobreak >nul
echo.

REM Step 5: Check logs for errors
echo [INFO] Checking logs for errors...
docker-compose logs --tail=50 odoo | findstr /I /C:"ERROR" /C:"CRITICAL" | findstr /I /C:"announcement" >nul
if %ERRORLEVEL% EQU 0 (
    echo [WARN] Errors detected in logs. Please review.
    echo.
    echo View full logs with: docker-compose logs -f odoo
) else (
    echo [OK] No errors detected in recent logs
)
echo.

REM Step 6: Summary
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Next Steps:
echo   1. Clear your browser cache (Ctrl+Shift+Delete)
echo   2. Force refresh the page (Ctrl+F5)
echo   3. Test announcement creation with formatted content
echo   4. Verify title readability and HTML rendering
echo.
echo Module Information:
echo   - Module: announcement_banner
echo   - Version: 17.0.1.0.2
echo   - Status: Updated
echo.
echo Useful Commands:
echo   - View logs: docker-compose logs -f odoo
echo   - Restart: docker-compose restart odoo
echo   - Stop: docker-compose down
echo.
echo [SUCCESS] Enhancements deployed successfully!
echo.
pause
