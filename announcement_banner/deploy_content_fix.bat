@echo off
REM Message Content Display Fix - Deployment Script (Windows)
REM Version: 1.2.0
REM Date: November 13, 2025

echo ================================================
echo Announcement Banner - Message Content Fix
echo ================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running
    exit /b 1
)

echo Step 1: Cleaning Python cache...
call clean_cache.bat
echo [OK] Cache cleaned
echo.

echo Step 2: Restarting Odoo container...
docker-compose restart odoo
echo [OK] Container restarted
echo.

echo Step 3: Waiting for Odoo to start (30 seconds)...
timeout /t 30 /nobreak >nul
echo [OK] Wait complete
echo.

echo Step 4: Updating announcement_banner module...
docker-compose exec odoo odoo --update=announcement_banner --stop-after-init --no-http
echo [OK] Module updated
echo.

echo Step 5: Starting Odoo service...
docker-compose up -d odoo
echo [OK] Service started
echo.

echo Step 6: Waiting for service to be ready (20 seconds)...
timeout /t 20 /nobreak >nul
echo [OK] Service ready
echo.

echo ================================================
echo Deployment Complete!
echo ================================================
echo.
echo Next Steps:
echo 1. Clear your browser cache (Ctrl+Shift+R)
echo 2. Log in to Odoo
echo 3. Create a test announcement with:
echo    - Text content (paragraphs, headings)
echo    - Images (upload via HTML editor)
echo    - Tables (use editor table tool)
echo    - Mixed content
echo 4. Verify content displays correctly
echo 5. Test on mobile device
echo.
echo To view logs:
echo   docker-compose logs -f odoo
echo.
echo To check module status:
echo   Navigate to Apps ^> Announcement Banner
echo.

pause
