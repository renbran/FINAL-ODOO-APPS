@echo off
echo 🗃️ Database Restoration Script for PropertyOSUS
echo ================================================
echo.

set /p confirm=This will restore the database from dump.sql. Continue? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo 🛑 Stopping Odoo service...
docker-compose stop odoo

echo.
echo 🗂️ Creating fresh database...
docker exec -it odoo17_final-db-1 psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS propertyosus;"
docker exec -it odoo17_final-db-1 psql -U odoo -d postgres -c "CREATE DATABASE propertyosus WITH OWNER odoo;"

echo.
echo 📥 Restoring database from dump.sql...
echo This may take several minutes...
docker exec -i odoo17_final-db-1 psql -U odoo -d propertyosus < "d:\odoo17_final\custom\dump.sql"

if errorlevel 1 (
    echo ❌ Database restore failed!
    pause
    exit /b 1
)

echo.
echo ✅ Database restored successfully!
echo.
echo 🚀 Starting Odoo...
docker-compose start odoo

echo.
echo ⏳ Waiting for Odoo to start...
timeout /t 20 /nobreak >nul

echo.
echo 🌐 PropertyOSUS should now be available at:
echo http://localhost:8069/web?db=propertyosus
echo.
echo 📋 If you encounter module errors, you may need to:
echo 1. Update the Apps list in Odoo
echo 2. Install/upgrade specific modules
echo.
pause
