@echo off
echo 🔧 Fixing web.assets_backend error for payment_account_enhanced module...
echo.

echo ⏹️ Stopping Docker containers...
docker-compose down

echo 🧹 Clearing Docker cache...
docker system prune -f

echo ▶️ Starting containers fresh...
docker-compose up -d

echo ⏳ Waiting for startup (30 seconds)...
timeout /t 30 /nobreak >nul

echo 📋 Checking container status...
docker-compose ps

echo.
echo ✅ RESTART COMPLETE!
echo.
echo 💡 Next steps:
echo    1. Go to http://localhost:8069
echo    2. Login as admin
echo    3. Go to Apps menu
echo    4. Click "Update Apps List" 
echo    5. Search for "OSUS Payment Voucher Enhanced"
echo    6. Try clicking "Upgrade" again
echo.
echo 🔍 If the error persists, the module data may need manual cleanup:
echo    - Go to Apps menu
echo    - Find "OSUS Payment Voucher Enhanced" 
echo    - Click "Uninstall"
echo    - Then click "Install" instead of "Upgrade"
echo.

pause
