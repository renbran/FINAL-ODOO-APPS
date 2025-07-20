@echo off
REM ============================================
REM INSTALL PYTHON PACKAGES FOR ODOO MODULES
REM ============================================

echo 📦 Installing Python Packages for Odoo Modules
echo ===============================================

echo 📋 Required packages:
echo   - pandas (data analysis and manipulation)
echo   - openpyxl (Excel file reading/writing)
echo   - moment (date/time handling)
echo.

echo 🔍 Step 1: Checking current Odoo container...
docker ps | findstr odoo17_final-odoo-1

echo.
echo 📦 Step 2: Installing packages in Odoo container...

echo   🔹 Installing pandas...
docker exec odoo17_final-odoo-1 pip install pandas

echo   🔹 Installing openpyxl...  
docker exec odoo17_final-odoo-1 pip install openpyxl

echo   🔹 Installing moment...
docker exec odoo17_final-odoo-1 pip install moment

echo.
echo 📦 Step 3: Installing additional useful packages...

echo   🔹 Installing xlsxwriter (Excel creation)...
docker exec odoo17_final-odoo-1 pip install xlsxwriter

echo   🔹 Installing python-dateutil (date utilities)...
docker exec odoo17_final-odoo-1 pip install python-dateutil

echo   🔹 Installing numpy (numerical computing)...
docker exec odoo17_final-odoo-1 pip install numpy

echo.
echo 🔍 Step 4: Verifying installations...
docker exec odoo17_final-odoo-1 python3 -c "import pandas; print('✅ pandas version:', pandas.__version__)"
docker exec odoo17_final-odoo-1 python3 -c "import openpyxl; print('✅ openpyxl version:', openpyxl.__version__)"
docker exec odoo17_final-odoo-1 python3 -c "import moment; print('✅ moment installed successfully')"
docker exec odoo17_final-odoo-1 python3 -c "import xlsxwriter; print('✅ xlsxwriter version:', xlsxwriter.__version__)"
docker exec odoo17_final-odoo-1 python3 -c "import numpy; print('✅ numpy version:', numpy.__version__)"

echo.
echo 🔄 Step 5: Restarting Odoo to load new packages...
docker-compose restart odoo
timeout /t 15 /nobreak >nul

echo.
echo ✅ PYTHON PACKAGES INSTALLATION COMPLETE!
echo ========================================
echo 📋 Installed packages:
echo   ✅ pandas - for data analysis in reports
echo   ✅ openpyxl - for Excel file operations  
echo   ✅ moment - for date/time handling
echo   ✅ xlsxwriter - for advanced Excel creation
echo   ✅ python-dateutil - for date utilities
echo   ✅ numpy - for numerical operations
echo.
echo 🌐 Access your Odoo: http://localhost:8069/web?db=propertyosus
echo.
echo 💡 Your modules that require these packages should now work:
echo   - report_xlsx (Excel reports)
echo   - osus_dashboard (data analysis)
echo   - hrms_dashboard (reporting)
echo   - sales_target_vs_achievement (analytics)
echo.

pause
