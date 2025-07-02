# Comprehensive PowerShell script to fix OSUS Invoice Report installation
# This script handles both paper format issues and module installation

param(
    [string]$Database = "odoo17_final",
    [string]$OdooPath = "C:\Program Files\Odoo 17.0\server\odoo-bin",
    [string]$ConfigPath = "C:\Program Files\Odoo 17.0\server\odoo.conf",
    [string]$AddonsPath = $null,
    [switch]$SkipPaperFormatFix = $false,
    [switch]$OnlyPaperFormatFix = $false
)

function Write-ColoredMessage {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-OdooSetup {
    param([string]$OdooPath, [string]$ConfigPath)
    
    $errors = @()
    
    if (-not (Test-Path $OdooPath)) {
        $errors += "Odoo binary not found at: $OdooPath"
    }
    
    if ($ConfigPath -and -not (Test-Path $ConfigPath)) {
        Write-ColoredMessage "⚠️ Config file not found at: $ConfigPath" "Yellow"
        Write-ColoredMessage "Will run without config file" "Yellow"
        return $errors
    }
    
    return $errors
}

function Invoke-OdooShellScript {
    param([string]$ScriptPath, [string]$Description)
    
    Write-ColoredMessage "`nExecuting: $Description" "Cyan"
    
    # Build the command
    $Command = "`"$OdooPath`" shell -d $Database --addons-path=`"$AddonsPath`""
    
    if ($ConfigPath -and (Test-Path $ConfigPath)) {
        $Command += " -c `"$ConfigPath`""
    }
    
    $Command += " < `"$ScriptPath`""
    
    Write-ColoredMessage "Command: $Command" "Gray"
    
    try {
        $Output = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredMessage "✅ $Description completed successfully" "Green"
            return $true
        } else {
            Write-ColoredMessage "❌ $Description failed with exit code: $LASTEXITCODE" "Red"
            Write-ColoredMessage "Output: $Output" "Red"
            return $false
        }
    } catch {
        Write-ColoredMessage "❌ Error executing $Description" "Red"
        Write-ColoredMessage $_.Exception.Message "Red"
        return $false
    }
}

function Install-OdooModule {
    param([string]$ModuleName, [string]$Action = "install")
    
    Write-ColoredMessage "`nExecuting module $Action for: $ModuleName" "Cyan"
    
    $ActionFlag = if ($Action -eq "upgrade") { "-u" } else { "-i" }
    $Command = "`"$OdooPath`" -d $Database --addons-path=`"$AddonsPath`" $ActionFlag $ModuleName --stop-after-init"
    
    if ($ConfigPath -and (Test-Path $ConfigPath)) {
        $Command += " -c `"$ConfigPath`""
    }
    
    Write-ColoredMessage "Command: $Command" "Gray"
    
    try {
        $Output = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredMessage "✅ Module $Action completed successfully" "Green"
            return $true
        } else {
            Write-ColoredMessage "❌ Module $Action failed with exit code: $LASTEXITCODE" "Red"
            Write-ColoredMessage "Output: $Output" "Red"
            return $false
        }
    } catch {
        Write-ColoredMessage "❌ Error during module $Action" "Red"
        Write-ColoredMessage $_.Exception.Message "Red"
        return $false
    }
}

# Main execution
Write-ColoredMessage "OSUS Invoice Report Comprehensive Fix" "Cyan"
Write-ColoredMessage "====================================" "Cyan"

# Set default addons path if not provided
if (-not $AddonsPath) {
    $AddonsPath = Get-Location
}

Write-ColoredMessage "`nConfiguration:" "Yellow"
Write-ColoredMessage "  Database: $Database" "White"
Write-ColoredMessage "  Odoo Path: $OdooPath" "White"
Write-ColoredMessage "  Config Path: $ConfigPath" "White"
Write-ColoredMessage "  Addons Path: $AddonsPath" "White"

# Test Odoo setup
$setupErrors = Test-OdooSetup -OdooPath $OdooPath -ConfigPath $ConfigPath
if ($setupErrors.Count -gt 0) {
    Write-ColoredMessage "`n❌ Setup errors found:" "Red"
    foreach ($setupError in $setupErrors) {
        Write-ColoredMessage "  $setupError" "Red"
    }
    exit 1
}

# Check required scripts exist
$PaperFormatScript = Join-Path $AddonsPath "fix_paperformat_direct.py"
$ModuleScript = Join-Path $AddonsPath "fix_osus_module.py"

$missingScripts = @()
if (-not (Test-Path $PaperFormatScript)) {
    $missingScripts += $PaperFormatScript
}
if (-not (Test-Path $ModuleScript)) {
    $missingScripts += $ModuleScript
}

if ($missingScripts.Count -gt 0) {
    Write-ColoredMessage "`n❌ Required scripts not found:" "Red"
    foreach ($script in $missingScripts) {
        Write-ColoredMessage "  $script" "Red"
    }
    exit 1
}

$success = $true

# Step 1: Fix paper format (unless skipped)
if (-not $SkipPaperFormatFix) {
    Write-ColoredMessage "`n📝 Step 1: Fixing paper format external ID..." "Green"
    $paperFormatSuccess = Invoke-OdooShellScript -ScriptPath $PaperFormatScript -Description "Paper format fix"
    
    if (-not $paperFormatSuccess) {
        Write-ColoredMessage "⚠️ Paper format fix failed, but continuing..." "Yellow"
    }
}

# Stop here if only paper format fix was requested
if ($OnlyPaperFormatFix) {
    Write-ColoredMessage "`n✅ Paper format fix completed!" "Green"
    exit 0
}

# Step 2: Try module installation via shell script
Write-ColoredMessage "`n📦 Step 2: Installing/upgrading module via shell script..." "Green"
$moduleScriptSuccess = Invoke-OdooShellScript -ScriptPath $ModuleScript -Description "Module installation/upgrade"

# Step 3: Try direct module installation
if (-not $moduleScriptSuccess) {
    Write-ColoredMessage "`n📦 Step 3: Trying direct module installation..." "Green"
    $directInstallSuccess = Install-OdooModule -ModuleName "osus_invoice_report" -Action "install"
    
    if (-not $directInstallSuccess) {
        Write-ColoredMessage "`n📦 Step 4: Trying module upgrade..." "Green"
        $directUpgradeSuccess = Install-OdooModule -ModuleName "osus_invoice_report" -Action "upgrade"
        
        if (-not $directUpgradeSuccess) {
            $success = $false
        }
    }
}

# Final status
Write-ColoredMessage "`n" + "="*60 "Cyan"
if ($success) {
    Write-ColoredMessage "✅ OSUS Module Fix Process Completed!" "Green"
    Write-ColoredMessage "Next steps:" "Yellow"
    Write-ColoredMessage "1. Start your Odoo server" "White"
    Write-ColoredMessage "2. Login to Odoo and go to Apps menu" "White"
    Write-ColoredMessage "3. Search for 'OSUS Invoice Report' and verify it's installed" "White"
    Write-ColoredMessage "4. Test creating an invoice and generating the report" "White"
} else {
    Write-ColoredMessage "⚠️ Some steps failed during the fix process" "Yellow"
    Write-ColoredMessage "Manual steps to try:" "Yellow"
    Write-ColoredMessage "1. Start Odoo server and login" "White"
    Write-ColoredMessage "2. Go to Apps menu > Update Apps List" "White"
    Write-ColoredMessage "3. Search for 'OSUS Invoice Report' and install manually" "White"
    Write-ColoredMessage "4. If installation fails, check Odoo logs for specific errors" "White"
}
Write-ColoredMessage "="*60 "Cyan"

# Usage examples
Write-ColoredMessage "`nUsage Examples:" "Cyan"
Write-ColoredMessage "  Basic fix:" "White"
Write-ColoredMessage "    .\fix_osus_comprehensive.ps1" "Gray"
Write-ColoredMessage "`n  Custom database and paths:" "White"
Write-ColoredMessage "    .\fix_osus_comprehensive.ps1 -Database 'my_db' -OdooPath 'C:\Odoo\odoo-bin'" "Gray"
Write-ColoredMessage "`n  Only fix paper format:" "White"
Write-ColoredMessage "    .\fix_osus_comprehensive.ps1 -OnlyPaperFormatFix" "Gray"
Write-ColoredMessage "`n  Skip paper format fix:" "White"
Write-ColoredMessage "    .\fix_osus_comprehensive.ps1 -SkipPaperFormatFix" "Gray"
