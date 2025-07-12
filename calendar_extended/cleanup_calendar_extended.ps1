# Calendar Extended Module Cleanup Script for Windows
# Run this PowerShell script as Administrator

param(
    [switch]$CleanOnly,
    [switch]$Help
)

# Configuration
$ODOO_PATH = "/var/odoo/osuspro"
$MODULE_NAME = "calendar_extended"
$LOCAL_MODULE_PATH = "d:\RUNNING APPS\ready production\osus-main\odoo17_final\calendar_extended"

function Write-Status($Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success($Message) {
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning($Message) {
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Message($Message) {
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host "Calendar Extended Module Cleanup Script"
    Write-Host ""
    Write-Host "Usage: .\cleanup_calendar_extended.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -CleanOnly    Only clean local files and cache"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "This script will:"
    Write-Host "  1. Clean old problematic files from local module directory"
    Write-Host "  2. Remove Python cache files"
    Write-Host "  3. Validate XML syntax"
    Write-Host "  4. Prepare module for clean deployment"
}

function Clean-LocalFiles {
    Write-Status "Cleaning old problematic files from local module..."
    
    if (Test-Path $LOCAL_MODULE_PATH) {
        # Remove old model files that are no longer needed
        $oldFiles = @(
            "$LOCAL_MODULE_PATH\models\calendar_recurrence.py",
            "$LOCAL_MODULE_PATH\models\calendar_event.py",
            "$LOCAL_MODULE_PATH\models\calendar_event_type.py",
            "$LOCAL_MODULE_PATH\models\calendar_resource.py",
            "$LOCAL_MODULE_PATH\models\calendar_template.py",
            "$LOCAL_MODULE_PATH\models\calendar_reminder.py",
            "$LOCAL_MODULE_PATH\models\res_partner.py",
            "$LOCAL_MODULE_PATH\models\calendar_internal_meeting.py",
            "$LOCAL_MODULE_PATH\models\calendar_meeting_attendee.py"
        )
        
        foreach ($file in $oldFiles) {
            if (Test-Path $file) {
                Remove-Item $file -Force -ErrorAction SilentlyContinue
                Write-Success "Removed: $file"
            }
        }
        
        # Remove old view files
        $oldViews = @(
            "$LOCAL_MODULE_PATH\views\calendar_department_group_views.xml",
            "$LOCAL_MODULE_PATH\views\calendar_event_type_views.xml",
            "$LOCAL_MODULE_PATH\views\calendar_resource_views.xml",
            "$LOCAL_MODULE_PATH\views\calendar_template_views.xml",
            "$LOCAL_MODULE_PATH\views\calendar_meeting_wizard_views.xml",
            "$LOCAL_MODULE_PATH\views\calendar_internal_meeting_views.xml"
        )
        
        foreach ($view in $oldViews) {
            if (Test-Path $view) {
                Remove-Item $view -Force -ErrorAction SilentlyContinue
                Write-Success "Removed: $view"
            }
        }
        
        # Remove old wizard directory
        if (Test-Path "$LOCAL_MODULE_PATH\wizards") {
            Remove-Item "$LOCAL_MODULE_PATH\wizards" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Success "Removed old wizards directory"
        }
        
        # Remove old data files
        $oldData = @(
            "$LOCAL_MODULE_PATH\data\calendar_data.xml",
            "$LOCAL_MODULE_PATH\data\email_templates.xml"
        )
        
        foreach ($data in $oldData) {
            if (Test-Path $data) {
                Remove-Item $data -Force -ErrorAction SilentlyContinue
                Write-Success "Removed: $data"
            }
        }
        
        # Remove old security files
        if (Test-Path "$LOCAL_MODULE_PATH\security\calendar_extended_security.xml") {
            Remove-Item "$LOCAL_MODULE_PATH\security\calendar_extended_security.xml" -Force -ErrorAction SilentlyContinue
            Write-Success "Removed old security file"
        }
        
        Write-Success "Local file cleanup completed"
    } else {
        Write-Warning "Module path not found: $LOCAL_MODULE_PATH"
    }
}

function Clean-PythonCache {
    Write-Status "Cleaning Python cache files..."
    
    if (Test-Path $LOCAL_MODULE_PATH) {
        # Remove __pycache__ directories
        Get-ChildItem -Path $LOCAL_MODULE_PATH -Recurse -Directory -Name "__pycache__" | 
        ForEach-Object { 
            $path = Join-Path $LOCAL_MODULE_PATH $_
            Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        # Remove .pyc files
        Get-ChildItem -Path $LOCAL_MODULE_PATH -Recurse -Filter "*.pyc" | 
        Remove-Item -Force -ErrorAction SilentlyContinue
        
        # Remove .pyo files
        Get-ChildItem -Path $LOCAL_MODULE_PATH -Recurse -Filter "*.pyo" | 
        Remove-Item -Force -ErrorAction SilentlyContinue
        
        Write-Success "Python cache cleaned"
    }
}

function Test-XmlFiles {
    Write-Status "Validating XML files..."
    
    $xmlErrors = 0
    
    if (Test-Path $LOCAL_MODULE_PATH) {
        $xmlFiles = Get-ChildItem -Path $LOCAL_MODULE_PATH -Recurse -Filter "*.xml"
        
        foreach ($xmlFile in $xmlFiles) {
            try {
                $xml = [xml](Get-Content $xmlFile.FullName)
                Write-Success "Valid XML: $($xmlFile.Name)"
            }
            catch {
                Write-Error-Message "XML syntax error in: $($xmlFile.Name)"
                Write-Error-Message "Error: $($_.Exception.Message)"
                $xmlErrors++
            }
        }
        
        if ($xmlErrors -eq 0) {
            Write-Success "All XML files are valid"
            return $true
        } else {
            Write-Error-Message "Found $xmlErrors XML files with errors"
            return $false
        }
    }
    
    return $true
}

function Show-DeploymentInstructions {
    Write-Status "=== DEPLOYMENT INSTRUCTIONS ==="
    Write-Host ""
    Write-Success "Local cleanup completed. Now deploy to server:"
    Write-Host ""
    Write-Host "1. Copy the cleaned module to your server:" -ForegroundColor Cyan
    Write-Host "   scp -r '$LOCAL_MODULE_PATH' user@server:$ODOO_PATH/src/addons/" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Run the server cleanup script:" -ForegroundColor Cyan
    Write-Host "   sudo bash $ODOO_PATH/src/addons/calendar_extended/cleanup_and_update.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Or manually execute these commands on the server:" -ForegroundColor Cyan
    Write-Host "   sudo systemctl stop odoo" -ForegroundColor White
    Write-Host "   sudo -u odoo $ODOO_PATH/venv/bin/python3 $ODOO_PATH/src/odoo-bin -c $ODOO_PATH/odoo.conf --no-http --stop-after-init --uninstall calendar_extended" -ForegroundColor White
    Write-Host "   sudo systemctl start odoo" -ForegroundColor White
    Write-Host "   sudo -u odoo $ODOO_PATH/venv/bin/python3 $ODOO_PATH/src/odoo-bin -c $ODOO_PATH/odoo.conf --no-http --stop-after-init --install calendar_extended" -ForegroundColor White
    Write-Host ""
}

# Main execution
function Main {
    Write-Host "=============================================" -ForegroundColor Magenta
    Write-Host "Calendar Extended Module Cleanup (Windows)" -ForegroundColor Magenta  
    Write-Host "=============================================" -ForegroundColor Magenta
    Write-Host ""
    
    # Step 1: Clean local files
    Clean-LocalFiles
    
    # Step 2: Clean Python cache
    Clean-PythonCache
    
    # Step 3: Validate XML files
    $xmlValid = Test-XmlFiles
    
    if (-not $xmlValid) {
        Write-Error-Message "XML validation failed. Please fix XML errors before deployment."
        exit 1
    }
    
    Write-Success "Local cleanup completed successfully!"
    
    if (-not $CleanOnly) {
        Show-DeploymentInstructions
    }
}

# Parse arguments and run
if ($Help) {
    Show-Help
    exit 0
}

if ($CleanOnly) {
    Write-Status "Running cleanup only..."
    Clean-LocalFiles
    Clean-PythonCache
    $xmlValid = Test-XmlFiles
    Write-Success "Cleanup completed!"
    exit 0
}

Main
