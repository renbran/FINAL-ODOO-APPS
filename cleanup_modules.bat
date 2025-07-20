@echo off
REM ============================================
REM MODULE CLEANUP - REMOVE DUPLICATES & INCOMPATIBLE
REM ============================================

echo 🧹 Cleaning Up Duplicate and Incompatible Modules
echo ================================================

echo 📋 Identified Issues:
echo   🔸 Duplicate modules (same module in multiple locations)
echo   🔸 Version 16.0 modules (incompatible with Odoo 17)
echo   🔸 Nested duplicate directories
echo   🔸 Disabled modules (.disabled extension)
echo.

echo 🗑️  Step 1: Removing incompatible version modules...

REM Remove version 16 modules
if exist "ideo_website_remove_promotion_message-16.0.1.0" (
    echo   ❌ Removing: ideo_website_remove_promotion_message-16.0.1.0 (v16.0 incompatible)
    rmdir /s /q "ideo_website_remove_promotion_message-16.0.1.0"
)

echo 🗑️  Step 2: Removing duplicate modules...

REM Remove duplicates - keep root level, remove custom/ versions
if exist "custom\muk_web_appsbar" if exist "muk_web_appsbar" (
    echo   ❌ Removing duplicate: custom\muk_web_appsbar
    rmdir /s /q "custom\muk_web_appsbar"
)

if exist "custom\muk_web_chatter" if exist "muk_web_chatter" (
    echo   ❌ Removing duplicate: custom\muk_web_chatter
    rmdir /s /q "custom\muk_web_chatter"
)

if exist "custom\muk_web_colors" if exist "muk_web_colors" (
    echo   ❌ Removing duplicate: custom\muk_web_colors
    rmdir /s /q "custom\muk_web_colors"
)

if exist "custom\muk_web_dialog" if exist "muk_web_dialog" (
    echo   ❌ Removing duplicate: custom\muk_web_dialog
    rmdir /s /q "custom\muk_web_dialog"
)

if exist "custom\muk_web_theme" if exist "muk_web_theme" (
    echo   ❌ Removing duplicate: custom\muk_web_theme
    rmdir /s /q "custom\muk_web_theme"
)

if exist "custom\ingenuity_invoice_qr_code" if exist "ingenuity_invoice_qr_code" (
    echo   ❌ Removing duplicate: custom\ingenuity_invoice_qr_code
    rmdir /s /q "custom\ingenuity_invoice_qr_code"
)

if exist "custom\le_sale_type" if exist "le_sale_type" (
    echo   ❌ Removing duplicate: custom\le_sale_type
    rmdir /s /q "custom\le_sale_type"
)

if exist "custom\odoo_accounting_dashboard" if exist "odoo_accounting_dashboard" (
    echo   ❌ Removing duplicate: custom\odoo_accounting_dashboard
    rmdir /s /q "custom\odoo_accounting_dashboard"
)

if exist "custom\oe_sale_dashboard_17" if exist "oe_sale_dashboard_17" (
    echo   ❌ Removing duplicate: custom\oe_sale_dashboard_17
    rmdir /s /q "custom\oe_sale_dashboard_17"
)

if exist "custom\order_status_override" if exist "order_status_override" (
    echo   ❌ Removing duplicate: custom\order_status_override
    rmdir /s /q "custom\order_status_override"
)

if exist "custom\reconcilation_fields" if exist "reconcilation_fields" (
    echo   ❌ Removing duplicate: custom\reconcilation_fields
    rmdir /s /q "custom\reconcilation_fields"
)

if exist "custom\report_pdf_options" if exist "report_pdf_options" (
    echo   ❌ Removing duplicate: custom\report_pdf_options
    rmdir /s /q "custom\report_pdf_options"
)

if exist "custom\report_xlsx" if exist "report_xlsx" (
    echo   ❌ Removing duplicate: custom\report_xlsx
    rmdir /s /q "custom\report_xlsx"
)

if exist "custom\sales_target_vs_achievement" if exist "sales_target_vs_achievement" (
    echo   ❌ Removing duplicate: custom\sales_target_vs_achievement
    rmdir /s /q "custom\sales_target_vs_achievement"
)

if exist "custom\sale_invoice_detail" if exist "sale_invoice_detail" (
    echo   ❌ Removing duplicate: custom\sale_invoice_detail
    rmdir /s /q "custom\sale_invoice_detail"
)

if exist "custom\sale_invoice_due_date_reminder" if exist "sale_invoice_due_date_reminder" (
    echo   ❌ Removing duplicate: custom\sale_invoice_due_date_reminder
    rmdir /s /q "custom\sale_invoice_due_date_reminder"
)

if exist "custom\sale_order_invoicing_qty_percentage" if exist "sale_order_invoicing_qty_percentage" (
    echo   ❌ Removing duplicate: custom\sale_order_invoicing_qty_percentage
    rmdir /s /q "custom\sale_order_invoicing_qty_percentage"
)

if exist "custom\statement_report" if exist "statement_report" (
    echo   ❌ Removing duplicate: custom\statement_report
    rmdir /s /q "custom\statement_report"
)

if exist "custom\subscription_package" if exist "subscription_package" (
    echo   ❌ Removing duplicate: custom\subscription_package
    rmdir /s /q "custom\subscription_package"
)

if exist "custom\tk_partner_ledger" if exist "tk_partner_ledger" (
    echo   ❌ Removing duplicate: custom\tk_partner_ledger
    rmdir /s /q "custom\tk_partner_ledger"
)

if exist "custom\tk_portal_partner_leads" if exist "tk_portal_partner_leads" (
    echo   ❌ Removing duplicate: custom\tk_portal_partner_leads
    rmdir /s /q "custom\tk_portal_partner_leads"
)

if exist "custom\tk_sale_split_invoice" if exist "tk_sale_split_invoice" (
    echo   ❌ Removing duplicate: custom\tk_sale_split_invoice
    rmdir /s /q "custom\tk_sale_split_invoice"
)

if exist "custom\upper_unicity_partner_product" if exist "upper_unicity_partner_product" (
    echo   ❌ Removing duplicate: custom\upper_unicity_partner_product
    rmdir /s /q "custom\upper_unicity_partner_product"
)

if exist "custom\web_login_styles" if exist "web_login_styles" (
    echo   ❌ Removing duplicate: custom\web_login_styles
    rmdir /s /q "custom\web_login_styles"
)

if exist "custom\whatsapp_mail_messaging" if exist "whatsapp_mail_messaging" (
    echo   ❌ Removing duplicate: custom\whatsapp_mail_messaging
    rmdir /s /q "custom\whatsapp_mail_messaging"
)

if exist "custom\whatsapp_redirect" if exist "whatsapp_redirect" (
    echo   ❌ Removing duplicate: custom\whatsapp_redirect
    rmdir /s /q "custom\whatsapp_redirect"
)

echo 🗑️  Step 3: Removing nested duplicates in theme directories...

REM Remove nested om_account_accountant duplicates in theme directories
if exist "theme_upshift\om_account_accountant-18.0.1.0.3" (
    echo   ❌ Removing nested duplicate: theme_upshift\om_account_accountant-18.0.1.0.3
    rmdir /s /q "theme_upshift\om_account_accountant-18.0.1.0.3"
)

echo 🗑️  Step 4: Removing conflicting HR modules...

REM Remove duplicate hr_payroll_community (keep main one, remove nested)
if exist "uae_wps_report-17.0.1.0.0\hr_payroll_community" (
    echo   ❌ Removing nested duplicate: uae_wps_report-17.0.1.0.0\hr_payroll_community
    rmdir /s /q "uae_wps_report-17.0.1.0.0\hr_payroll_community"
)

REM Remove duplicate hr_uae_extended (keep main one, remove nested)
if exist "hr_uae_extended\hr_uae_extended" (
    echo   ❌ Removing nested duplicate: hr_uae_extended\hr_uae_extended
    rmdir /s /q "hr_uae_extended\hr_uae_extended"
)

echo 🗑️  Step 5: Removing disabled modules...

if exist "custom\hide_menu_user.disabled" (
    echo   ❌ Removing disabled module: custom\hide_menu_user.disabled
    rmdir /s /q "custom\hide_menu_user.disabled"
)

echo 🗑️  Step 6: Removing conflicting account modules...

REM Keep one version of om_account_followup
if exist "custom\om_account_followup" if exist "om_account_followup" (
    echo   ❌ Removing duplicate: custom\om_account_followup
    rmdir /s /q "custom\om_account_followup"
)

REM Keep one version of om_data_remove
if exist "custom\om_data_remove" if exist "om_data_remove" (
    echo   ❌ Removing duplicate: custom\om_data_remove
    rmdir /s /q "custom\om_data_remove"
)

echo ✅ Step 7: Cleanup Complete!
echo.
echo 📊 CLEANUP SUMMARY:
echo   ✅ Removed incompatible v16.0 modules
echo   ✅ Removed duplicate modules (kept root versions)  
echo   ✅ Removed nested duplicates
echo   ✅ Removed disabled modules
echo   ✅ Resolved module conflicts
echo.
echo 🎯 Remaining Clean Modules Ready for Installation:
echo   📦 Core: report_xlsx, report_pdf_options
echo   📊 Dashboards: hrms_dashboard, osus_dashboard, oe_sale_dashboard_17
echo   💼 Business: payment_account_enhanced, reconcilation_fields
echo   🎨 UI: muk_web_theme, theme_levelup
echo   📋 Reports: osus_invoice_report, sales_target_vs_achievement
echo.

pause
