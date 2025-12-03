# Module Cleanup Script - DELETE modules scoring <80%
# Generated: December 3, 2025
# Review ALL modules before deletion - some may be in active use!

# CRITICAL WARNING: rental_management (66%) is production-ready but has wrong version number
# DO NOT DELETE rental_management - FIX VERSION INSTEAD!

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "MODULE DELETION SCRIPT" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "This script will move 33 low-scoring modules (<80%) to archive/" -ForegroundColor Cyan
Write-Host ""
Write-Host "CRITICAL: rental_management will NOT be deleted - needs version fix only" -ForegroundColor Red
Write-Host ""

# Modules to DELETE (33 total - score <80%)
$modulesToDelete = @(
    "account_line_view",  # 79%
    "automatic_invoice_and_post",  # 79%
    "comprehensive_greetings",  # 79% - 7 XML errors
    "invoice_bill_select_orderlines",  # 79%
    "odoo_accounting_dashboard",  # 79%
    "om_data_remove",  # 79%
    "sale_invoice_detail",  # 79%
    "website_custom_contact_us",  # 79%
    "crm_ai_field_compatibility",  # 78%
    "muk_web_colors",  # 78%
    "report_xlsx",  # 78%
    "partner_statement_followup",  # 77% - deprecated attrs
    "website_menu_fix",  # 77%
    "account_reconcile_model_oca",  # 75%
    "sale_order_invoicing_qty_percentage",  # 75%
    "wt_birthday_reminder",  # 73%
    "gsk_automatic_mail_server",  # 72%
    "user_admin_field_compatibility",  # 71%
    "osus_report_header_footer",  # 69%
    "form_edit_button_restore",  # 68%
    "employee_access_manager",  # 66% - Not Odoo 17
    # "rental_management",  # 66% - EXCLUDED - FIX VERSION INSTEAD
    "sgc_tech_ai_theme",  # 66%
    "hr_uae",  # 62% - Not Odoo 17
    "le_sale_type",  # 62% - Not Odoo 17
    "tk_portal_partner_leads",  # 59% - Not Odoo 17
    "odoo_crm_dashboard",  # 58% - Not Odoo 17
    "tk_partner_ledger",  # 58% - Not Odoo 17
    "tk_sale_split_invoice",  # 55% - Not Odoo 17
    "reconcilation_fields",  # 52% - Not Odoo 17
    "eg_mo_today_yesterday_filter",  # 49% - Not Odoo 17
    "event_so_trigger",  # 47% - Not Odoo 17
    "pretty_buttons"  # 47% - Not Odoo 17
)

Write-Host "Modules to delete: $($modulesToDelete.Count)" -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Type 'DELETE' to proceed with archiving these modules"

if ($confirm -ne "DELETE") {
    Write-Host "Aborted - No modules were deleted" -ForegroundColor Green
    exit
}

# Create archive directory if it doesn't exist
$archivePath = "archive\deleted_$(Get-Date -Format 'yyyy-MM-dd_HHmmss')"
if (-not (Test-Path $archivePath)) {
    New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
    Write-Host "Created archive directory: $archivePath" -ForegroundColor Green
}

# Move modules to archive
$successCount = 0
$failCount = 0

foreach ($module in $modulesToDelete) {
    if (Test-Path $module) {
        try {
            Write-Host "Archiving: $module..." -NoNewline
            Move-Item -Path $module -Destination "$archivePath\$module" -Force
            Write-Host " ✓ Done" -ForegroundColor Green
            $successCount++
        }
        catch {
            Write-Host " ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
            $failCount++
        }
    }
    else {
        Write-Host "Skipping: $module (not found)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "SUMMARY" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Successfully archived: $successCount modules" -ForegroundColor Green
Write-Host "Failed: $failCount modules" -ForegroundColor Red
Write-Host "Archive location: $archivePath" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  REMINDER: Fix rental_management version in __manifest__.py" -ForegroundColor Red
Write-Host "   Change: 'version': '3.5.0'" -ForegroundColor Red
Write-Host "   To:     'version': '17.0.3.5.0'" -ForegroundColor Green
Write-Host ""
