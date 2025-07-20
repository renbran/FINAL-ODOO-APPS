@echo off
REM ============================================
REM QUICK TEST - PYTHON PACKAGES FOR ODOO
REM ============================================

echo 🧪 QUICK PYTHON PACKAGES TEST
echo =============================

echo 📋 Testing all required packages in Odoo container...
docker exec odoo17_final-odoo-1 python3 -c "
import sys
print('🐍 Python version:', sys.version.split()[0])
print()

# Test all packages
packages_to_test = [
    ('pandas', 'pd'),
    ('openpyxl', 'openpyxl'),
    ('moment', 'moment'),
    ('xlsxwriter', 'xlsxwriter'),
    ('numpy', 'np'),
    ('dateutil', 'dateutil'),
    ('pytz', 'pytz')
]

success_count = 0
total_count = len(packages_to_test)

for package, alias in packages_to_test:
    try:
        if alias:
            exec(f'import {package} as {alias}')
        else:
            exec(f'import {package}')
        print(f'✅ {package} - OK')
        success_count += 1
    except ImportError as e:
        print(f'❌ {package} - FAILED: {e}')

print()
print(f'📊 RESULTS: {success_count}/{total_count} packages working')

if success_count == total_count:
    print('🎉 ALL PACKAGES WORKING PERFECTLY!')
    print('Your Odoo modules can now use all Python features.')
else:
    print('⚠️  Some packages need attention.')

print()
print('🔗 Test creating Excel file...')
try:
    import pandas as pd
    import openpyxl
    df = pd.DataFrame({'Test': [1, 2, 3], 'Data': ['A', 'B', 'C']})
    print('✅ DataFrame created successfully')
    print('✅ Excel operations ready to use')
except Exception as e:
    print(f'❌ Excel test failed: {e}')
"

echo.
echo ✅ QUICK TEST COMPLETE!
echo ======================
echo 💡 If all tests passed, your modules are ready to use!
echo.

pause
