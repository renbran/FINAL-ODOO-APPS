# =============================================================================
# ODOO MANAGEMENT SCRIPT - OLDOSUS INSTANCE (PowerShell Version)
# =============================================================================

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Param1,
    
    [Parameter(Position=2)]
    [string]$Param2,
    
    [Parameter(Position=3)]
    [string]$Param3
)

# Configuration Variables
$ODOO_BASE = "C:\odoo\oldosus"  # Adjust path for Windows
$ODOO_SRC = Join-Path $ODOO_BASE "src"
$ODOO_LOGS = Join-Path $ODOO_BASE "logs"
$ODOO_CONFIG = Join-Path $ODOO_BASE "odoo.conf"
$PYTHON_INTERPRETER = Join-Path $ODOO_BASE "venv\Scripts\python.exe"
$ODOO_USER = "odoo"

# Color codes for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Header {
    param([string]$Title)
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
}

# Function to check if user has proper permissions
function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "This script requires Administrator privileges"
        exit 1
    }
}

# Function to check if Odoo paths exist
function Test-OdooPaths {
    $pathsOk = $true
    
    if (-not (Test-Path $ODOO_BASE)) {
        Write-Error "Odoo base directory not found: $ODOO_BASE"
        $pathsOk = $false
    }
    
    if (-not (Test-Path $ODOO_SRC)) {
        Write-Error "Odoo source directory not found: $ODOO_SRC"
        $pathsOk = $false
    }
    
    if (-not (Test-Path $ODOO_LOGS)) {
        Write-Warning "Logs directory not found: $ODOO_LOGS"
        $createLogs = Read-Host "Create logs directory? (y/n)"
        if ($createLogs -eq "y" -or $createLogs -eq "Y") {
            New-Item -Path $ODOO_LOGS -ItemType Directory -Force | Out-Null
            Write-Status "Created logs directory: $ODOO_LOGS"
        }
    }
    
    if (-not (Test-Path $ODOO_CONFIG)) {
        Write-Error "Odoo config file not found: $ODOO_CONFIG"
        $pathsOk = $false
    }
    
    if (-not (Test-Path $PYTHON_INTERPRETER)) {
        Write-Error "Python interpreter not found: $PYTHON_INTERPRETER"
        $pathsOk = $false
    }
    
    if (-not $pathsOk) {
        Write-Error "Please check your Odoo installation paths"
        exit 1
    }
    
    Write-Status "All Odoo paths verified successfully"
}

# Function 1: Update payment status in Odoo
function Update-PaymentStatus {
    param(
        [string]$DefaultStatus = "draft",
        [string]$NewStatus = "posted"
    )
    
    Write-Header "UPDATING PAYMENT STATUS"
    Write-Status "Updating payment entries from '$DefaultStatus' to '$NewStatus'"
    
    # Create Python script for Odoo shell
    $pythonScript = @"
# Update payment status script
import logging

_logger = logging.getLogger(__name__)

try:
    # Search for payment entries with default status
    payments = env['account.payment'].search([('state', '=', '$DefaultStatus')])
    
    if not payments:
        print("No payments found with status '$DefaultStatus'")
    else:
        updated_count = 0
        for payment in payments:
            try:
                if payment.state == '$DefaultStatus':
                    payment.write({'state': '$NewStatus'})
                    updated_count += 1
            except Exception as e:
                print(f"Error updating payment {payment.id}: {e}")
        
        print(f"Successfully updated {updated_count} payment entries")
        env.cr.commit()
        
except Exception as e:
    print(f"Error in payment update: {e}")
    env.cr.rollback()
"@
    
    $tempScript = Join-Path $env:TEMP "update_payments.py"
    $pythonScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    # Execute via Odoo shell
    Set-Location $ODOO_BASE
    & $PYTHON_INTERPRETER "src\odoo-bin" shell -c $ODOO_CONFIG --shell-interface ipython < $tempScript
    
    # Clean up
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    Write-Status "Payment status update completed"
}

# Function 2: Apply decimal precision to monetary fields
function Set-DecimalPrecision {
    param(
        [int]$Precision = 2
    )
    
    Write-Header "APPLYING DECIMAL PRECISION"
    Write-Status "Applying $Precision decimal precision to monetary fields"
    
    # Create Python script for decimal precision
    $pythonScript = @"
# Decimal precision enforcement script
import logging

_logger = logging.getLogger(__name__)

try:
    # Update account move lines
    move_lines = env['account.move.line'].search([])
    updated_count = 0
    
    for line in move_lines:
        updates = {}
        
        # Round debit and credit to specified precision
        if line.debit:
            new_debit = round(line.debit, $Precision)
            if new_debit != line.debit:
                updates['debit'] = new_debit
        
        if line.credit:
            new_credit = round(line.credit, $Precision)
            if new_credit != line.credit:
                updates['credit'] = new_credit
        
        if line.amount_currency:
            new_amount = round(line.amount_currency, $Precision)
            if new_amount != line.amount_currency:
                updates['amount_currency'] = new_amount
        
        if updates:
            line.write(updates)
            updated_count += 1
    
    print(f"Updated {updated_count} account move lines with proper decimal precision")
    
    # Update invoice lines
    invoice_lines = env['account.move.line'].search([('move_id.move_type', 'in', ['out_invoice', 'in_invoice'])])
    invoice_updated = 0
    
    for line in invoice_lines:
        if line.price_unit:
            new_price = round(line.price_unit, $Precision)
            if new_price != line.price_unit:
                line.write({'price_unit': new_price})
                invoice_updated += 1
    
    print(f"Updated {invoice_updated} invoice lines with proper decimal precision")
    env.cr.commit()
    
except Exception as e:
    print(f"Error applying decimal precision: {e}")
    env.cr.rollback()
"@
    
    $tempScript = Join-Path $env:TEMP "decimal_precision.py"
    $pythonScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    # Execute via Odoo shell
    Set-Location $ODOO_BASE
    & $PYTHON_INTERPRETER "src\odoo-bin" shell -c $ODOO_CONFIG --shell-interface ipython < $tempScript
    
    # Clean up
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    Write-Status "Decimal precision applied successfully"
}

# Function 3: Find and merge duplicate contacts
function Find-DuplicateContacts {
    param(
        [int]$Threshold = 80
    )
    
    Write-Header "FINDING DUPLICATE CONTACTS"
    Write-Status "Searching for duplicate contacts with $Threshold% similarity threshold"
    
    # Create Python script for finding duplicates
    $pythonScript = @"
# Find duplicate contacts script
import logging
from difflib import SequenceMatcher

_logger = logging.getLogger(__name__)

def similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

try:
    partners = env['res.partner'].search([('is_company', '=', False)])
    duplicates = []
    
    print(f"Analyzing {len(partners)} contacts for duplicates...")
    
    for i, partner1 in enumerate(partners):
        for partner2 in partners[i+1:]:
            name_sim = similarity(partner1.name or '', partner2.name or '')
            email_sim = similarity(partner1.email or '', partner2.email or '')
            phone_sim = similarity(partner1.phone or '', partner2.phone or '')
            
            # Consider duplicate if name similarity is high OR email/phone match
            if (name_sim >= $Threshold or 
                (email_sim >= 90 and partner1.email and partner2.email) or
                (phone_sim >= 90 and partner1.phone and partner2.phone)):
                
                duplicates.append({
                    'partner1': partner1,
                    'partner2': partner2,
                    'name_similarity': round(name_sim, 2),
                    'email_similarity': round(email_sim, 2),
                    'phone_similarity': round(phone_sim, 2)
                })
    
    if duplicates:
        print(f"\\nFound {len(duplicates)} potential duplicate pairs:")
        print("-" * 80)
        
        for i, dup in enumerate(duplicates):
            print(f"\\nDuplicate Pair {i+1}:")
            print(f"Contact 1 (ID: {dup['partner1'].id}): {dup['partner1'].name}")
            print(f"  Email: {dup['partner1'].email or 'N/A'}")
            print(f"  Phone: {dup['partner1'].phone or 'N/A'}")
            print(f"Contact 2 (ID: {dup['partner2'].id}): {dup['partner2'].name}")
            print(f"  Email: {dup['partner2'].email or 'N/A'}")
            print(f"  Phone: {dup['partner2'].phone or 'N/A'}")
            print(f"Similarities - Name: {dup['name_similarity']}% | Email: {dup['email_similarity']}% | Phone: {dup['phone_similarity']}%")
            print("-" * 40)
            
            # Save duplicate info to a CSV file for review
            import os
            csv_file = os.path.join(os.environ['TEMP'], 'odoo_duplicates.csv')
            with open(csv_file, 'a', encoding='utf-8') as f:
                if i == 0:  # Write header only once
                    f.write("ID1,Name1,Email1,Phone1,ID2,Name2,Email2,Phone2,NameSim,EmailSim,PhoneSim\\n")
                f.write(f"{dup['partner1'].id},\"{dup['partner1'].name or ''}\",\"{dup['partner1'].email or ''}\",\"{dup['partner1'].phone or ''}\",")
                f.write(f"{dup['partner2'].id},\"{dup['partner2'].name or ''}\",\"{dup['partner2'].email or ''}\",\"{dup['partner2'].phone or ''}\",")
                f.write(f"{dup['name_similarity']},{dup['email_similarity']},{dup['phone_similarity']}\\n")
        
        print(f"\\nDuplicate report saved to: {csv_file}")
    else:
        print("No duplicate contacts found!")
        
except Exception as e:
    print(f"Error finding duplicates: {e}")
"@
    
    $tempScript = Join-Path $env:TEMP "find_duplicates.py"
    $duplicatesCsv = Join-Path $env:TEMP "odoo_duplicates.csv"
    
    # Remove existing duplicate report
    Remove-Item $duplicatesCsv -Force -ErrorAction SilentlyContinue
    
    $pythonScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    # Execute via Odoo shell
    Set-Location $ODOO_BASE
    & $PYTHON_INTERPRETER "src\odoo-bin" shell -c $ODOO_CONFIG --shell-interface ipython < $tempScript
    
    # Clean up
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    
    if (Test-Path $duplicatesCsv) {
        Write-Status "Duplicate contacts report generated: $duplicatesCsv"
        Write-Host "You can review the duplicates and manually merge them through Odoo interface"
    }
}

# Odoo Management Functions
function Open-OdooShell {
    Write-Header "ODOO SHELL ACCESS"
    Write-Status "Opening Odoo shell..."
    Set-Location $ODOO_BASE
    & $PYTHON_INTERPRETER "src\odoo-bin" shell -c $ODOO_CONFIG
}

function Update-AllModules {
    Write-Header "UPDATING ALL MODULES"
    Write-Warning "This operation may take several minutes..."
    $confirm = Read-Host "Are you sure you want to update all modules? (y/n)"
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Status "Updating all Odoo modules..."
        Set-Location $ODOO_BASE
        & $PYTHON_INTERPRETER "src\odoo-bin" -c $ODOO_CONFIG --no-http --stop-after-init --update all
        Write-Status "Module update completed"
    } else {
        Write-Status "Module update cancelled"
    }
}

function Install-PythonPackage {
    param([string]$PackageName)
    
    if (-not $PackageName) {
        $PackageName = Read-Host "Enter package name to install"
    }
    
    if ($PackageName) {
        Write-Header "INSTALLING PYTHON PACKAGE"
        Write-Status "Installing package: $PackageName"
        & $PYTHON_INTERPRETER -m pip install $PackageName
        Write-Status "Package installation completed"
    } else {
        Write-Error "No package name provided"
    }
}

function Show-Logs {
    Write-Header "ODOO LOGS"
    Write-Host "Available log files in $ODOO_LOGS:"
    
    if (Test-Path $ODOO_LOGS) {
        Get-ChildItem $ODOO_LOGS -Filter "*.log" | Format-Table Name, LastWriteTime, Length
        $logFile = Read-Host "Enter log file name to view (or press Enter to view latest)"
        
        if (-not $logFile) {
            $logFile = Get-ChildItem $ODOO_LOGS -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $logPath = $logFile.FullName
        } else {
            $logPath = Join-Path $ODOO_LOGS $logFile
        }
        
        if (Test-Path $logPath) {
            Write-Status "Viewing log file: $logPath"
            Write-Host "Press Ctrl+C to quit"
            Get-Content $logPath -Tail 50 -Wait
        } else {
            Write-Error "Log file not found: $logPath"
        }
    } else {
        Write-Error "Log directory not found: $ODOO_LOGS"
    }
}

function Backup-Database {
    Write-Header "DATABASE BACKUP"
    $dbName = Read-Host "Enter database name"
    
    if ($dbName) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = Join-Path $env:TEMP "odoo_backup_${dbName}_${timestamp}.sql"
        Write-Status "Creating backup: $backupFile"
        
        try {
            # Assuming PostgreSQL is in PATH or adjust path as needed
            pg_dump $dbName | Out-File -FilePath $backupFile -Encoding UTF8
            Write-Status "Backup created successfully: $backupFile"
        } catch {
            Write-Error "Backup failed: $_"
        }
    } else {
        Write-Error "No database name provided"
    }
}

# Show system status
function Show-Status {
    Write-Header "ODOO SYSTEM STATUS"
    
    Write-Host "`nPaths:" -ForegroundColor Blue
    Write-Host "  Base Directory: $ODOO_BASE"
    Write-Host "  Source: $ODOO_SRC"
    Write-Host "  Logs: $ODOO_LOGS"
    Write-Host "  Config: $ODOO_CONFIG"
    Write-Host "  Python: $PYTHON_INTERPRETER"
    
    Write-Host "`nDisk Usage:" -ForegroundColor Blue
    if (Test-Path $ODOO_BASE) {
        $drive = (Get-Item $ODOO_BASE).Root
        $driveInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $drive.Name.TrimEnd('\') }
        $freeGB = [math]::Round($driveInfo.FreeSpace / 1GB, 2)
        $totalGB = [math]::Round($driveInfo.Size / 1GB, 2)
        Write-Host "  Free Space: $freeGB GB / $totalGB GB"
    } else {
        Write-Host "  Cannot access $ODOO_BASE"
    }
    
    Write-Host "`nRecent Log Activity:" -ForegroundColor Blue
    if (Test-Path $ODOO_LOGS) {
        Get-ChildItem $ODOO_LOGS -Filter "*.log" | 
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } |
            Select-Object -First 5 |
            ForEach-Object { Write-Host "  $($_.Name) - $($_.LastWriteTime)" }
    } else {
        Write-Host "  No log directory found"
    }
    
    Write-Host "`nOdoo Process:" -ForegroundColor Blue
    $odooProcesses = Get-Process | Where-Object { $_.ProcessName -like "*odoo*" -or $_.ProcessName -like "*python*" }
    if ($odooProcesses) {
        $odooProcesses | Select-Object -First 3 | Format-Table ProcessName, Id, CPU, WorkingSet
    } else {
        Write-Host "  No Odoo processes running"
    }
}

# Interactive menu
function Show-Menu {
    Write-Host ""
    Write-Host "=== ODOO MANAGEMENT TOOLS - OLDOSUS ===" -ForegroundColor Magenta
    Write-Host "1.  Update payment status (draft to posted)"
    Write-Host "2.  Apply 2 decimal precision to monetary fields"
    Write-Host "3.  Find duplicate contacts with fuzzy matching"
    Write-Host "4.  Open Odoo shell"
    Write-Host "5.  Update all modules"
    Write-Host "6.  Install Python package"
    Write-Host "7.  View logs"
    Write-Host "8.  Backup database"
    Write-Host "9.  Show system status"
    Write-Host "10. Exit"
    Write-Host ""
}

# Main execution
function Main {
    Write-Header "ODOO MANAGEMENT SCRIPT INITIALIZATION"
    
    # Check prerequisites
    Test-AdminRights
    Test-OdooPaths
    
    if (-not $Command) {
        # Interactive mode
        while ($true) {
            Show-Menu
            $choice = Read-Host "Choose an option (1-10)"
            
            switch ($choice) {
                "1" {
                    $defaultStatus = Read-Host "Enter default status to change [draft]"
                    if (-not $defaultStatus) { $defaultStatus = "draft" }
                    $newStatus = Read-Host "Enter new status [posted]"
                    if (-not $newStatus) { $newStatus = "posted" }
                    Update-PaymentStatus -DefaultStatus $defaultStatus -NewStatus $newStatus
                }
                "2" {
                    $precision = Read-Host "Enter decimal precision [2]"
                    if (-not $precision) { $precision = 2 }
                    Set-DecimalPrecision -Precision $precision
                }
                "3" {
                    $threshold = Read-Host "Enter similarity threshold % [80]"
                    if (-not $threshold) { $threshold = 80 }
                    Find-DuplicateContacts -Threshold $threshold
                }
                "4" {
                    Open-OdooShell
                }
                "5" {
                    Update-AllModules
                }
                "6" {
                    Install-PythonPackage
                }
                "7" {
                    Show-Logs
                }
                "8" {
                    Backup-Database
                }
                "9" {
                    Show-Status
                }
                "10" {
                    Write-Status "Goodbye!"
                    exit 0
                }
                default {
                    Write-Error "Invalid option. Please try again."
                }
            }
        }
    } else {
        # Command line mode
        switch ($Command) {
            "update-payments" {
                Update-PaymentStatus -DefaultStatus $Param1 -NewStatus $Param2
            }
            "apply-precision" {
                Set-DecimalPrecision -Precision $Param1
            }
            "find-duplicates" {
                Find-DuplicateContacts -Threshold $Param1
            }
            "shell" {
                Open-OdooShell
            }
            "update-modules" {
                Update-AllModules
            }
            "install-package" {
                Install-PythonPackage -PackageName $Param1
            }
            "backup" {
                Backup-Database
            }
            "status" {
                Show-Status
            }
            default {
                Write-Host "Usage: .\odoo_management_oldosus.ps1 [command] [args...]"
                Write-Host ""
                Write-Host "Commands:"
                Write-Host "  update-payments [default_status] [new_status]"
                Write-Host "  apply-precision [decimal_places]"
                Write-Host "  find-duplicates [threshold]"
                Write-Host "  shell"
                Write-Host "  update-modules"
                Write-Host "  install-package [package_name]"
                Write-Host "  backup"
                Write-Host "  status"
                Write-Host ""
                Write-Host "Run without arguments for interactive mode"
            }
        }
    }
}

# Run main function
Main
