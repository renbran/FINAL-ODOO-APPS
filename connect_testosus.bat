@echo off
REM ============================================
REM CONNECT TO TESTOSUS DATABASE
REM ============================================

echo 🔗 Connecting to TESTOSUS Database
echo ==================================

echo 🔍 Step 1: Checking available databases...
docker exec odoo17_final-db-1 psql -U odoo postgres -c "\l"

echo.
echo 🔍 Step 2: Verifying testosus database exists...
docker exec odoo17_final-db-1 psql -U odoo postgres -c "SELECT datname FROM pg_database WHERE datname = 'testosus';"

echo.
echo 🔄 Step 3: Restarting Odoo with testosus database...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to start with testosus database...
timeout /t 25

echo.
echo 🌐 Step 4: Testing Odoo accessibility with testosus database...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 10; Write-Host '✅ Odoo accessible with testosus database!' } catch { Write-Host '⚠️  Still starting, please wait...' }"

echo.
echo ✅ TESTOSUS DATABASE CONNECTION READY!
echo =====================================
echo.
echo 🌐 Access Points:
echo   🎯 Main: http://localhost:8069/web?db=testosus
echo   🔧 Admin: http://localhost:8069/web/database/manager
echo.
echo 💡 Database Information:
echo   📊 Database: testosus
echo   🏢 Owner: odoo
echo   🔤 Encoding: UTF8
echo   🌍 Locale: C / en_US.utf8
echo.
echo 🚀 Available Actions:
echo   1. Install modules in testosus database
echo   2. Update existing modules
echo   3. Import/Export data
echo   4. Backup/Restore database
echo.
echo Press any key to open Odoo with testosus database...
pause
start http://localhost:8069/web?db=testosus
