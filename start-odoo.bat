@echo off
echo Checking Docker availability...

docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running.
    echo Please install Docker Desktop first:
    echo 1. Go to https://www.docker.com/products/docker-desktop/
    echo 2. Download and install Docker Desktop for Windows
    echo 3. Restart your computer
    echo 4. Start Docker Desktop
    echo 5. Run this script again
    pause
    exit /b 1
)

echo ✅ Docker is available!
echo.
echo 🚀 Starting Odoo 17 with custom modules...
echo.

REM Build the Docker images
echo 🔨 Building Docker images...
docker-compose build --no-cache

if errorlevel 1 (
    echo ❌ Build failed! Check the logs above.
    pause
    exit /b 1
)

REM Start the services
echo 🚀 Starting services...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start services!
    pause
    exit /b 1
)

echo ⏳ Waiting for services to initialize...
timeout /t 30 /nobreak >nul

echo ✅ Odoo 17 is now running!
echo.
echo 🌐 Access Odoo at: http://localhost:8069
echo 🗄️  PostgreSQL Database: localhost:5432
echo.
echo 📋 Default database credentials:
echo    Database: postgres
echo    Username: odoo
echo    Password: odoo
echo.
echo 📝 To create your first database:
echo    1. Go to http://localhost:8069
echo    2. Click "Create Database"
echo    3. Enter your desired database name
echo    4. Set master password (use: VillaRicca)
echo    5. Click Create Database
echo.
echo 📊 To view logs: docker-compose logs -f
echo 🛑 To stop services: docker-compose down
echo.
pause
