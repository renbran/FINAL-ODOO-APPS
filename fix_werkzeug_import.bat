@echo off
REM fix_werkzeug_import.bat - Windows script to resolve the werkzeug import error

echo === Payment Approval Workflow - Import Fix Script ===
echo.

echo 🔍 Checking current portal.py import section:
echo.
type "payment_approval_workflow\controllers\portal.py" | findstr /n "import"
echo.

echo 🧹 Cleaning Python cache...
for /d /r "payment_approval_workflow" %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q "payment_approval_workflow\*.pyc" 2>nul
echo ✅ Python cache cleaned
echo.

echo 🔧 RESOLUTION STEPS:
echo 1. ✅ Import fix has been applied locally
echo 2. 🔄 Deploy changes to your server
echo 3. 🔄 Restart the Odoo server to clear import cache
echo 4. 🔄 Try installing the module again
echo.

echo 💡 The fix changes:
echo    FROM: from werkzeug.security import safe_str_cmp as consteq
echo    TO:   from odoo.tools import consteq
echo.

echo ✅ Script completed!
pause
