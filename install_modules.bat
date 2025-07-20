@echo off
echo 🚀 Custom Module Installation Script
echo ====================================
echo.

echo Available custom modules in your workspace:
echo.
echo 📦 Main Custom Modules:
echo - osus_dashboard (OSUS Dashboard)
echo - osus_invoice_report (Invoice Reports)
echo - hrms_dashboard (HR Dashboard) 
echo - payment_account_enhanced (Enhanced Payments)
echo - automated_employee_announce (Employee Announcements)
echo - calendar_extended (Extended Calendar)
echo - reconcilation_fields (Reconciliation Fields)
echo - order_status_override (Order Status Override)
echo - upper_unicity_partner_product (Product Uniqueness)
echo.

echo 📊 Reporting & Analytics:
echo - oe_sale_dashboard_17 (Sales Dashboard)
echo - sales_target_vs_achievement (Sales Targets)
echo - statement_report (Statement Reports)
echo - report_pdf_options (PDF Report Options)
echo - report_xlsx (Excel Reports)
echo.

echo 🎨 UI/UX Enhancements:
echo - muk_web_theme (Web Theme)
echo - muk_web_colors (Web Colors)
echo - muk_web_dialog (Web Dialog)
echo - muk_web_chatter (Web Chatter)
echo - theme_levelup (Levelup Theme)
echo - theme_upshift (Upshift Theme)
echo.

set /p modules=Enter module names to install (separated by commas): 
if "%modules%"=="" (
    echo No modules specified. Exiting.
    pause
    exit /b 0
)

echo.
echo 🔧 Installing modules: %modules%
echo.

REM Replace commas with spaces for Odoo command
set "odoo_modules=%modules:,= %"

echo Running: docker exec -it odoo17_final-odoo-1 odoo -d propertyosus -i %odoo_modules% --stop-after-init
docker exec -it odoo17_final-odoo-1 odoo -d propertyosus -i %odoo_modules% --stop-after-init

if errorlevel 1 (
    echo ❌ Module installation failed!
    echo Try installing modules one by one or check for dependencies.
) else (
    echo ✅ Modules installed successfully!
)

echo.
echo 🔄 Restarting Odoo...
docker-compose restart odoo

echo.
echo 🌐 Access your database: http://localhost:8069/web?db=propertyosus
echo.
pause
