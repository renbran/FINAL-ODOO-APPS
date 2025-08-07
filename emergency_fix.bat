@echo off
echo 🚨 EMERGENCY ASSETS BACKEND FIX
echo =============================================

echo.
echo Step 1: Stopping Odoo server...
docker-compose down

echo.
echo Step 2: Running database emergency fix...
docker-compose up -d db
timeout /t 5 /nobreak >nul

echo.
echo Step 3: Executing SQL cleanup...
docker-compose exec -T db psql -U odoo -d odoo < emergency_sql_fix.sql

echo.
echo Step 4: Running Python emergency fix...
docker-compose run --rm odoo python /var/odoo/testerp/src/odoo-bin shell -d odoo --addons-path=/mnt/extra-addons < fix_assets_emergency.py

echo.
echo Step 5: Restarting Odoo with update...
docker-compose up -d

echo.
echo 🎉 EMERGENCY FIX COMPLETE!
echo.
echo Next steps:
echo 1. Wait for Odoo to start (check logs with: docker-compose logs -f odoo)
echo 2. Go to Apps and Update Apps List
echo 3. Try installing payment_account_enhanced again
echo.
pause
