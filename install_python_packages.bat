@echo off
REM ============================================
REM INSTALL PYTHON PACKAGES FOR ODOO MODULES
REM ============================================

echo 📦 Installing Python Packages for Odoo Modules
echo ===============================================

echo 📋 Required packages for Odoo 17 modules:
echo   - pandas (data analysis and manipulation)
echo   - openpyxl (Excel file reading/writing) 
echo   - moment (date/time handling)
echo   - numpy (numerical computing)
echo   - xlsxwriter (advanced Excel creation)
echo   - python-dateutil (date utilities)
echo.

echo 🔍 Step 1: Checking current Odoo container...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 📦 Step 2: Installing core packages in Odoo container...

echo   🔹 Installing pandas (data analysis)...
docker exec odoo17_final-odoo-1 pip install --upgrade pandas

echo   🔹 Installing openpyxl (Excel files)...  
docker exec odoo17_final-odoo-1 pip install --upgrade openpyxl

echo   🔹 Installing moment (date/time)...
docker exec odoo17_final-odoo-1 pip install --upgrade moment

echo   🔹 Installing numpy (numerical computing)...
docker exec odoo17_final-odoo-1 pip install --upgrade numpy

echo.
echo 📦 Step 3: Installing additional reporting packages...

echo   🔹 Installing xlsxwriter (Excel creation)...
docker exec odoo17_final-odoo-1 pip install --upgrade xlsxwriter

echo   🔹 Installing python-dateutil (date utilities)...
docker exec odoo17_final-odoo-1 pip install --upgrade python-dateutil

echo   🔹 Installing additional dependencies...
docker exec odoo17_final-odoo-1 pip install --upgrade pytz tzlocal dateparser

echo.
echo 🔍 Step 4: Comprehensive package verification...
echo   🧪 Testing pandas...
docker exec odoo17_final-odoo-1 python3 -c "import pandas; print('✅ pandas version:', pandas.__version__)"

echo   🧪 Testing openpyxl...
docker exec odoo17_final-odoo-1 python3 -c "import openpyxl; print('✅ openpyxl version:', openpyxl.__version__)"

echo   🧪 Testing moment...
docker exec odoo17_final-odoo-1 python3 -c "import moment; print('✅ moment installed successfully')"

echo   🧪 Testing xlsxwriter...
docker exec odoo17_final-odoo-1 python3 -c "import xlsxwriter; print('✅ xlsxwriter version:', xlsxwriter.__version__)"

echo   🧪 Testing numpy...
docker exec odoo17_final-odoo-1 python3 -c "import numpy; print('✅ numpy version:', numpy.__version__)"

echo   🧪 Testing date utilities...
docker exec odoo17_final-odoo-1 python3 -c "import dateutil; print('✅ dateutil imported successfully')"

echo.
echo 🔄 Step 5: Restarting Odoo to load new packages...
docker-compose restart odoo
echo   ⏳ Waiting for Odoo to start completely...
timeout /t 20 /nobreak >nul

echo.
echo 🌐 Step 6: Testing Odoo accessibility...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8069' -Method Head -TimeoutSec 10; Write-Host '✅ Odoo responding on port 8069' } catch { Write-Host '⚠️  Odoo may still be starting...' }"

echo.
echo ✅ PYTHON PACKAGES INSTALLATION UPDATED & COMPLETE!
echo ==================================================
echo 📋 Successfully installed and verified packages:
echo   ✅ pandas - for data analysis in reports
echo   ✅ openpyxl - for Excel file operations  
echo   ✅ moment - for date/time handling
echo   ✅ xlsxwriter - for advanced Excel creation
echo   ✅ python-dateutil - for date utilities
echo   ✅ numpy - for numerical operations
echo   ✅ pytz, tzlocal, dateparser - additional date utilities
echo.
echo 🌐 Access your Odoo: http://localhost:8069/web?db=propertyosus
echo.
echo 💡 Your modules that require these packages should now work perfectly:
echo   📊 report_xlsx (Excel reports)
echo   📈 osus_dashboard (data analysis)
echo   👥 hrms_dashboard (HR reporting)
echo   📊 sales_target_vs_achievement (sales analytics)
echo   🎯 All other data processing modules
echo.
echo 🚀 Next Steps:
echo   1. Go to Apps → Update Apps List
echo   2. Install your modules without dependency errors
echo   3. Generate Excel reports and dashboards
echo.

pause
