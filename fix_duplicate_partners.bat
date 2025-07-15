@echo off
REM Fix Duplicate Partners Batch Script
REM This script connects to the Odoo container and runs the duplicate partner fix

echo 🔧 Starting duplicate partner fix...
echo ========================================

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: docker-compose not found
    pause
    exit /b 1
)

REM Check if containers are running
docker-compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Odoo containers not running. Start with: docker-compose up -d
    pause
    exit /b 1
)

echo 📦 Connecting to Odoo container...

REM Create temporary Python script
echo try: > temp_fix.py
echo     print("🔍 Searching for duplicate partner names...") >> temp_fix.py
echo     hr_employee = env['hr.employee'] >> temp_fix.py
echo     result = hr_employee.fix_existing_duplicate_partners() >> temp_fix.py
echo     print("\n" + "="*60) >> temp_fix.py
echo     print("DUPLICATE PARTNER FIX RESULTS") >> temp_fix.py
echo     print("="*60) >> temp_fix.py
echo     print(f"Duplicates found: {result['duplicates_found']}") >> temp_fix.py
echo     print(f"Records fixed: {result['fixed_count']}") >> temp_fix.py
echo     print(f"Message: {result['message']}") >> temp_fix.py
echo     print("="*60) >> temp_fix.py
echo     if result['fixed_count'] ^> 0: >> temp_fix.py
echo         env.cr.commit() >> temp_fix.py
echo         print("✅ Changes committed to database") >> temp_fix.py
echo     else: >> temp_fix.py
echo         print("ℹ️  No duplicates found or no changes needed") >> temp_fix.py
echo     print("\n🎉 Duplicate partner fix completed successfully!") >> temp_fix.py
echo except Exception as e: >> temp_fix.py
echo     print(f"❌ Error: {str(e)}") >> temp_fix.py
echo     env.cr.rollback() >> temp_fix.py
echo     print("🔄 Transaction rolled back") >> temp_fix.py

REM Copy script to container and run
docker cp temp_fix.py odoo17_final_odoo_1:/tmp/temp_fix.py
docker-compose exec odoo python3 odoo-bin shell -d osuspro -c "exec(open('/tmp/temp_fix.py').read())"

REM Cleanup
del temp_fix.py
docker-compose exec odoo rm /tmp/temp_fix.py

echo ========================================
echo ✅ Duplicate partner fix process completed
echo.
echo 💡 You can now proceed with employee imports
echo    The system will handle any new duplicates automatically
pause
