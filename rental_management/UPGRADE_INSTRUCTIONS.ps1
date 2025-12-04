# ============================================================================
# RENTAL MANAGEMENT MODULE - UPGRADE GUIDE (Windows PowerShell)
# ============================================================================
# Quick reference for upgrading the rental_management module
# ============================================================================

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  RENTAL MANAGEMENT MODULE - UPGRADE INSTRUCTIONS"  -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "THE PROBLEM:" -ForegroundColor Yellow
Write-Host "  Your code is correct and pushed to GitHub, but Odoo hasn't loaded"
Write-Host "  the new view structure yet. You need to UPGRADE the module in Odoo."
Write-Host ""

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "METHOD 1: Via Odoo UI (RECOMMENDED)" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1: Enable Developer Mode" -ForegroundColor Yellow
Write-Host "  1. Login to Odoo as Administrator"
Write-Host "  2. Go to Settings"
Write-Host "  3. Click 'Activate Developer Mode'"
Write-Host "     (OR add ?debug=1 to your URL)"
Write-Host ""

Write-Host "STEP 2: Update Apps List" -ForegroundColor Yellow
Write-Host "  1. Go to Apps menu (main menu bar)"
Write-Host "  2. Click 'Update Apps List' button (top menu)"
Write-Host "  3. Click 'Update' to confirm"
Write-Host ""

Write-Host "STEP 3: Upgrade Module" -ForegroundColor Yellow
Write-Host "  1. Still in Apps menu, click the 'Apps' filter to remove it"
Write-Host "  2. Search for 'rental_management'"
Write-Host "  3. Click on the rental_management module card"
Write-Host "  4. Click the 'Upgrade' button"
Write-Host "  5. Wait 30-60 seconds for upgrade to complete"
Write-Host ""

Write-Host "STEP 4: Clear Browser Cache" -ForegroundColor Yellow
Write-Host "  1. Press Ctrl + Shift + R (hard refresh)"
Write-Host "  2. OR: Press Ctrl + Shift + Delete and clear cache"
Write-Host ""

Write-Host "STEP 5: Verify Changes" -ForegroundColor Yellow
Write-Host "  1. Go to Property -> Sales -> Sales Contracts"
Write-Host "  2. Open the contract from your screenshot (PS/2025/12/0079)"
Write-Host "  3. You should now see:"
Write-Host "     - 6 smart buttons at top right (Booking, Installments, etc.)"
Write-Host "     - Payment Progress Dashboard below header"
Write-Host "     - 'Create Booking Invoices' button in header"
Write-Host ""

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "METHOD 2: Via Command Line (ALTERNATIVE)" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "If you have access to Odoo server:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Stop Odoo service"
Write-Host 'Stop-Service -Name "Odoo"' -ForegroundColor White
Write-Host ""
Write-Host "# Upgrade module"
Write-Host '& "C:\Program Files\Odoo 17.0\python\python.exe" \'
Write-Host '  "C:\Program Files\Odoo 17.0\server\odoo-bin" \'
Write-Host '  -d YOUR_DATABASE_NAME \'
Write-Host '  -u rental_management \'
Write-Host '  --stop-after-init'
Write-Host ""
Write-Host "# Start Odoo service"
Write-Host 'Start-Service -Name "Odoo"' -ForegroundColor White
Write-Host ""

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "WHAT YOU'LL SEE AFTER UPGRADE" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "When you open Sales Contract PS/2025/12/0079, you'll see:" -ForegroundColor Yellow
Write-Host ""
Write-Host "+-----------------------------------------------------------------+"
Write-Host "| Property Sale Contract                    [Smart Buttons -->]   |"
Write-Host "|                                          +---------+---------+   |"
Write-Host "| Title: Property Name                     | Booking | Install |   |"
Write-Host "| Reference: PS/2025/12/0079               |   (3)   |   (12)  |   |"
Write-Host "|                                          +---------+---------+   |"
Write-Host "|                                                                  |"
Write-Host "| +--------------------------------------------------------------+ |"
Write-Host "| | Payment Progress Overview                                    | |"
Write-Host "| | Overall Progress: [########------] 65%                       | |"
Write-Host "| | Paid: 325,000 AED / Total: 500,000 AED                       | |"
Write-Host "| +--------------------------------------------------------------+ |"
Write-Host "|                                                                  |"
Write-Host "| [Other fields...]                                                |"
Write-Host "+-----------------------------------------------------------------+"
Write-Host ""

Write-Host "Smart Buttons (top right):" -ForegroundColor Yellow
Write-Host "  - Booking (count)"
Write-Host "  - Installments (count)"
Write-Host "  - All Invoices (count)"
Write-Host "  - Created (count)"
Write-Host "  - Paid (count)"
Write-Host "  - Maintenance (count)"
Write-Host ""

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "TROUBLESHOOTING" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Q: Smart buttons still not showing?" -ForegroundColor Yellow
Write-Host "A: - Clear browser cache (Ctrl + Shift + Delete)"
Write-Host "   - Hard refresh (Ctrl + Shift + R)"
Write-Host "   - Close and reopen the form"
Write-Host "   - Try a different browser"
Write-Host ""

Write-Host "Q: 'Field not found' error?" -ForegroundColor Yellow
Write-Host "A: - Module didn't upgrade properly"
Write-Host "   - Check Odoo logs for errors"
Write-Host "   - Try upgrading again"
Write-Host "   - Restart Odoo service"
Write-Host ""

Write-Host "Q: Old view still showing?" -ForegroundColor Yellow
Write-Host "A: - Go to Settings -> Technical -> User Interface -> Views"
Write-Host "   - Search: 'property.vendor.form.view'"
Write-Host "   - Delete the view"
Write-Host "   - Upgrade module again"
Write-Host ""

Write-Host "Q: Changes not taking effect?" -ForegroundColor Yellow
Write-Host "A: - Restart Odoo service"
Write-Host "   - Clear Odoo asset cache"
Write-Host "   - Verify module version in Apps (should be 3.5.0)"
Write-Host ""

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC TOOLS" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Run the diagnostic script:" -ForegroundColor Yellow
Write-Host "  python check_module_status.py"
Write-Host ""

Write-Host "Read the documentation:" -ForegroundColor Yellow
Write-Host "  - MODULE_UPGRADE_GUIDE.md"
Write-Host "  - INVOICE_TRACKING_QUICK_START.md"
Write-Host "  - TROUBLESHOOTING_GUIDE.md"
Write-Host ""

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SUMMARY: Your code is correct. Just upgrade the module in Odoo!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Pause to keep window open
Read-Host "Press Enter to close"
