@echo off
REM ============================================
REM CHECK MODULE INSTALLATION STATUS
REM ============================================

echo 📊 Checking Module Installation Status in TESTOSUS
echo ==================================================

echo 🔍 Step 1: Checking Odoo container status...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 📋 Step 2: Checking installed modules in testosus database...
docker exec odoo17_final-db-1 psql -U odoo testosus -c "SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;" 2>nul

echo.
echo 🔄 Step 3: Checking if Odoo is accessible...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069/web?db=testosus' -Method Head -TimeoutSec 5; Write-Host '✅ Odoo is accessible' } catch { Write-Host '⚠️  Odoo may be busy installing modules...' }"

echo.
echo 📊 Step 4: Checking recent Odoo logs...
docker logs --tail 20 odoo17_final-odoo-1

echo.
echo 💡 Status Check Complete!
echo   - If modules are installing, please wait
echo   - Check http://localhost:8069/web?db=testosus when ready
echo   - Use Apps menu to see installed modules
echo.

pause
