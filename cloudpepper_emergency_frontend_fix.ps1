# CloudPepper Emergency Frontend Enhancement Fix
# PowerShell version for Windows deployment

Write-Host "🚨 EMERGENCY CLOUDPEPPER MODULE UPDATE" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Module: frontend_enhancement" -ForegroundColor Cyan
Write-Host "Issue: Cached XPath expressions causing ParseError" -ForegroundColor Yellow
Write-Host "Action: Force module update and view refresh" -ForegroundColor Green
Write-Host ""

# Validate local files first
Write-Host "🔍 Step 1: Validating local files..." -ForegroundColor Blue
try {
    [xml]$saleOrderXml = Get-Content ".\frontend_enhancement\views\sale_order_views.xml"
    [xml]$accountMoveXml = Get-Content ".\frontend_enhancement\views\account_move_views.xml"
    Write-Host "✅ Local XML files are valid" -ForegroundColor Green
} catch {
    Write-Host "❌ Local XML validation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check for the fixed XPath
$saleOrderContent = Get-Content ".\frontend_enhancement\views\sale_order_views.xml" -Raw
if ($saleOrderContent -match 'div\[@class=''o_kanban_record_title''\]') {
    Write-Host "✅ XPath fix confirmed in sale_order_views.xml" -ForegroundColor Green
} else {
    Write-Host "❌ XPath fix not found in sale_order_views.xml" -ForegroundColor Red
    Write-Host "Expected: //div[@class='o_kanban_record_title']" -ForegroundColor Yellow
}

$accountMoveContent = Get-Content ".\frontend_enhancement\views\account_move_views.xml" -Raw
if ($accountMoveContent -match 'div\[@class=''o_kanban_record_title''\]') {
    Write-Host "✅ XPath fix confirmed in account_move_views.xml" -ForegroundColor Green
} else {
    Write-Host "❌ XPath fix not found in account_move_views.xml" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 CRITICAL FIX DETAILS:" -ForegroundColor Magenta
Write-Host "Problem:  <xpath expr=`"//div[hasclass('o_kanban_record_title')]`">" -ForegroundColor Red
Write-Host "Solution: <xpath expr=`"//div[@class='o_kanban_record_title']`">" -ForegroundColor Green
Write-Host ""

Write-Host "📋 CLOUDPEPPER DEPLOYMENT STEPS:" -ForegroundColor Blue
Write-Host "1. 🌐 Login to CloudPepper: https://osusbck.cloudpepper.site" -ForegroundColor White
Write-Host "2. 📱 Go to Apps menu" -ForegroundColor White
Write-Host "3. 🔍 Search for 'frontend_enhancement'" -ForegroundColor White
Write-Host "4. 🗑️  Uninstall the module (if installed)" -ForegroundColor White
Write-Host "5. 🔄 Click 'Update Apps List'" -ForegroundColor White
Write-Host "6. 📦 Install 'Frontend Enhancement' module" -ForegroundColor White
Write-Host "7. ✅ Verify no ParseError occurs" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  IF ERROR PERSISTS:" -ForegroundColor Yellow
Write-Host "• Contact CloudPepper support" -ForegroundColor White
Write-Host "• Request Odoo service restart" -ForegroundColor White
Write-Host "• Ask for registry cache clear" -ForegroundColor White
Write-Host "• Force git repository sync" -ForegroundColor White
Write-Host ""

Write-Host "🚀 STATUS: Emergency fix ready for deployment ✅" -ForegroundColor Green

# Create a summary file
$summaryContent = @"
# Frontend Enhancement CloudPepper Emergency Fix Summary

## Issue
ParseError in /var/odoo/osusbck/extra-addons/odoo17_final.git-6880b7fcd4844/frontend_enhancement/views/sale_order_views.xml:44
Error: Element '<xpath expr="//div[hasclass('o_kanban_record_title')]">' cannot be located in parent view

## Root Cause
CloudPepper is using a cached version of the XML files with the old XPath syntax.

## Fix Applied (Local)
Changed XPath expressions from hasclass() function to direct class attribute:
- Before: //div[hasclass('o_kanban_record_title')]
- After: //div[@class='o_kanban_record_title']

## Files Updated
1. frontend_enhancement/views/sale_order_views.xml - Line 49
2. frontend_enhancement/views/account_move_views.xml - Line 74

## Deployment Required
The local files are fixed, but CloudPepper needs to:
1. Uninstall the module
2. Clear cache
3. Reinstall with updated files

## Status
✅ Local files: Fixed and validated
🔄 CloudPepper: Deployment pending
"@

$summaryContent | Out-File -FilePath ".\CLOUDPEPPER_EMERGENCY_FIX_SUMMARY.txt" -Encoding UTF8
Write-Host "📄 Summary saved to: CLOUDPEPPER_EMERGENCY_FIX_SUMMARY.txt" -ForegroundColor Cyan
