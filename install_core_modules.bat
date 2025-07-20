@echo off
echo 🏗️ Installing Essential OSUS Modules
echo ====================================
echo.

echo This will install the core OSUS modules:
echo - osus_dashboard
echo - osus_invoice_report  
echo - hrms_dashboard
echo - payment_account_enhanced
echo - oe_sale_dashboard_17
echo - sales_target_vs_achievement
echo.

set /p confirm=Install these modules? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo 🔧 Installing core OSUS modules...
docker exec -it odoo17_final-odoo-1 odoo -d propertyosus -i osus_dashboard,osus_invoice_report,hrms_dashboard,payment_account_enhanced,oe_sale_dashboard_17,sales_target_vs_achievement --stop-after-init

if errorlevel 1 (
    echo ❌ Installation failed! Trying one by one...
    
    echo Installing osus_dashboard...
    docker exec -it odoo17_final-odoo-1 odoo -d propertyosus -i osus_dashboard --stop-after-init
    
    echo Installing osus_invoice_report...
    docker exec -it odoo17_final-odoo-1 odoo -d propertyosus -i osus_invoice_report --stop-after-init
    
    echo Installing hrms_dashboard...
    docker exec -it odoo17_final-odoo-1 odoo -d propertyosus -i hrms_dashboard --stop-after-init
    
) else (
    echo ✅ All modules installed successfully!
)

echo.
echo 🔄 Restarting Odoo...
docker-compose restart odoo

echo.
echo 🌐 Access your database: http://localhost:8069/web?db=propertyosus
echo.
pause
