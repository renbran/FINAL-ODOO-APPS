# ============================================================================
# Rental Management Module - Quick Upgrade Script (Windows)
# ============================================================================
# This script helps you upgrade the rental_management module in Odoo
# Run this from PowerShell as Administrator
# ============================================================================

param(
    [string]$OdooPath = "C:\Program Files\Odoo 17.0",
    [string]$Database = "your_database_name",
    [switch]$CheckOnly,
    [switch]$Help
)

function Show-Help {
    Write-Host @"

╔════════════════════════════════════════════════════════════════════╗
║  RENTAL MANAGEMENT MODULE - QUICK UPGRADE SCRIPT                   ║
╚════════════════════════════════════════════════════════════════════╝

USAGE:
    .\upgrade_rental_module.ps1 -Database "your_db_name"
    .\upgrade_rental_module.ps1 -CheckOnly
    .\upgrade_rental_module.ps1 -Help

PARAMETERS:
    -Database      Your Odoo database name (required for upgrade)
    -OdooPath      Path to Odoo installation (default: C:\Program Files\Odoo 17.0)
    -CheckOnly     Only check if upgrade is needed (don't upgrade)
    -Help          Show this help message

EXAMPLES:
    # Check if upgrade is needed
    .\upgrade_rental_module.ps1 -CheckOnly

    # Upgrade the module
    .\upgrade_rental_module.ps1 -Database "production_db"

    # Upgrade with custom Odoo path
    .\upgrade_rental_module.ps1 -Database "test_db" -OdooPath "D:\Odoo"

NOTE:
    This is for Windows Odoo installations. If you're using:
    • Docker: Use docker-compose commands instead
    • Linux: Use the bash upgrade script
    • CloudPepper/Remote: Use the deployment scripts

"@
}

function Write-ColorOutput {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Step {
    param([string]$Text)
    Write-ColorOutput "`n→ $Text" "Cyan"
}

function Write-Success {
    param([string]$Text)
    Write-ColorOutput "✓ $Text" "Green"
}

function Write-Error {
    param([string]$Text)
    Write-ColorOutput "✗ $Text" "Red"
}

function Write-Warning {
    param([string]$Text)
    Write-ColorOutput "⚠ $Text" "Yellow"
}

function Test-OdooInstallation {
    Write-Step "Checking Odoo installation..."
    
    if (Test-Path $OdooPath) {
        Write-Success "Odoo found at: $OdooPath"
        return $true
    } else {
        Write-Error "Odoo not found at: $OdooPath"
        Write-Warning "Please specify correct path with -OdooPath parameter"
        return $false
    }
}

function Get-ModuleInfo {
    Write-Step "Checking rental_management module..."
    
    $modulePath = Join-Path $PSScriptRoot ""
    if (Test-Path $modulePath) {
        Write-Success "Module found in current directory"
        
        # Check __manifest__.py for version
        $manifestPath = Join-Path $PSScriptRoot "__manifest__.py"
        if (Test-Path $manifestPath) {
            $content = Get-Content $manifestPath -Raw
            if ($content -match "'version':\s*'([\d\.]+)'") {
                $version = $matches[1]
                Write-ColorOutput "  Current module version: $version" "Cyan"
                return $version
            }
        }
    } else {
        Write-Error "Module not found. Run this script from the rental_management directory"
        return $null
    }
}

function Show-UpgradeInstructions {
    Write-Host ""
    Write-Host "========================================================================"
    Write-Host "  HOW TO UPGRADE THE MODULE"
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "METHOD 1: Via Odoo UI (EASIEST - RECOMMENDED)" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------------------------"
    Write-Host ""
    Write-Host "1. Login to Odoo as Administrator"
    Write-Host ""
    Write-Host "2. Enable Developer Mode:"
    Write-Host "   - Go to Settings -> Activate Developer Mode"
    Write-Host "   - Or add ?debug=1 to URL"
    Write-Host ""
    Write-Host "3. Update Apps List:"
    Write-Host "   - Go to Apps menu"
    Write-Host "   - Click 'Update Apps List' (top menu)"
    Write-Host "   - Confirm the action"
    Write-Host ""
    Write-Host "4. Upgrade Module:"
    Write-Host "   - In Apps menu, remove 'Apps' filter"
    Write-Host "   - Search for 'rental_management'"
    Write-Host "   - Click the module card"
    Write-Host "   - Click 'Upgrade' button"
    Write-Host "   - Wait 30-60 seconds"
    Write-Host ""
    Write-Host "5. Clear Browser Cache:"
    Write-Host "   - Press Ctrl + Shift + R (hard refresh)"
    Write-Host "   - Or clear all browser cache"
    Write-Host ""
    Write-Host "6. Verify:"
    Write-Host "   - Open any Sales Contract"
    Write-Host "   - Check for smart buttons at top right"
    Write-Host "   - Check for payment dashboard below header"


📌 METHOD 2: Via PowerShell (ADVANCED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run these commands:

# Stop Odoo service
Stop-Service -Name "Odoo"

# Upgrade module (replace YOUR_DB with your database name)
& "C:\Program Files\Odoo 17.0\python\python.exe" `
  "C:\Program Files\Odoo 17.0\server\odoo-bin" `
  -d YOUR_DB `
  -u rental_management `
  --stop-after-init

# Start Odoo service
Start-Service -Name "Odoo"


📌 METHOD 3: Via Python Script (DEVELOPER)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

python check_module_status.py

Then follow the on-screen instructions.


╔════════════════════════════════════════════════════════════════════╗
║  WHAT YOU'LL SEE AFTER UPGRADE                                     ║
╚════════════════════════════════════════════════════════════════════╝

When you open a Sales Contract (PS/2025/12/0079), you should see:

┌──────────────────────────────────────────────────────────────────┐
│ Sales Contract: Property Name              [Smart Buttons →→→]   │
│ Reference: PS/2025/12/0079                                        │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 💰 Payment Progress Overview                                 │ │
│ │                                                              │ │
│ │ Overall Progress: [████████░░░░] 65%                        │ │
│ │ Paid: 325,000 AED / Total: 500,000 AED                      │ │
│ │                                                              │ │
│ │ Installment Progress: [██████░░░░░] 50%                     │ │
│ │ Outstanding: 175,000 AED                                     │ │
│ │                                                              │ │
│ │  Total: 15  │  Created: 15  │  Paid: 10  │  Pending: 5     │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ [Rest of form...]                                                  │
└────────────────────────────────────────────────────────────────────┘

Smart Buttons (top right corner):
  📋 Booking (3)     💰 Installments (12)    📄 All (15)
  📚 Created (15)    ✅ Paid (10)            🔧 Maintenance (2)


╔════════════════════════════════════════════════════════════════════╗
║  TROUBLESHOOTING                                                   ║
╚════════════════════════════════════════════════════════════════════╝

❓ Smart buttons still not showing?
   → Clear browser cache (Ctrl + Shift + Delete)
   → Hard refresh (Ctrl + Shift + R)
   → Close and reopen the form

❓ "Field not found" error?
   → Module didn't upgrade properly
   → Check Odoo logs for errors
   → Try upgrading again

❓ Old view still showing?
   → Go to Settings → Technical → Views
   → Search: "property.vendor.form.view"
   → Delete the view
   → Upgrade module again

❓ Changes not taking effect?
   → Restart Odoo service
   → Clear Odoo asset cache
   → Verify module version in Apps

╔════════════════════════════════════════════════════════════════════╗
║  NEED MORE HELP?                                                   ║
╚════════════════════════════════════════════════════════════════════╝

📖 Read the documentation:
   • MODULE_UPGRADE_GUIDE.md
   • INVOICE_TRACKING_QUICK_START.md
   • TROUBLESHOOTING_GUIDE.md
   • README.md

🔧 Run the diagnostic:
   python check_module_status.py

📝 Check Odoo logs:
   Get-Content "C:\Program Files\Odoo 17.0\server\odoo.log" -Tail 50

🌐 Open Odoo in debug mode:
   http://your-odoo-site.com/web?debug=1

"@
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

Write-ColorOutput "`n╔════════════════════════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║  RENTAL MANAGEMENT MODULE - UPGRADE SCRIPT v1.0                    ║" "Cyan"
Write-ColorOutput "╚════════════════════════════════════════════════════════════════════╝`n" "Cyan"

if ($Help) {
    Show-Help
    exit 0
}

# Get module version
$moduleVersion = Get-ModuleInfo

if (-not $moduleVersion) {
    Write-Error "Could not determine module version"
    exit 1
}

if ($CheckOnly) {
    Write-ColorOutput "`n✓ Check complete. Module version: $moduleVersion" "Green"
    Write-Warning "`nTo upgrade, run: .\upgrade_rental_module.ps1 -Database 'your_db_name'"
    exit 0
}

# Show instructions
Write-ColorOutput "`n📖 Follow the instructions below to upgrade the module:" "Yellow"
Show-UpgradeInstructions

Write-ColorOutput "`n════════════════════════════════════════════════════════════════════" "Cyan"
Write-ColorOutput "Script completed. Follow the instructions above to upgrade." "Green"
Write-ColorOutput "════════════════════════════════════════════════════════════════════`n" "Cyan"
