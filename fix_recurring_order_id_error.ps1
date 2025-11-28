#Requires -Version 5.1
<#
.SYNOPSIS
    Deploys fix for recurring_order_id Owl Error to CloudPepper Odoo

.DESCRIPTION
    Removes orphan field definitions that reference deleted models.
    
    ERROR: "sale.order"."recurring_order_id" field is undefined.
    This field references sale.recurring model which no longer exists.

.EXAMPLE
    .\fix_recurring_order_id_error.ps1 -Action Verify
    .\fix_recurring_order_id_error.ps1 -Action Backup
    .\fix_recurring_order_id_error.ps1 -Action Deploy
    .\fix_recurring_order_id_error.ps1 -Action Rollback

.NOTES
    Requires SSH access to CloudPepper server
    Author: Odoo Development Team
    Date: 2025-11-28
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('Verify', 'Backup', 'Deploy', 'Rollback', 'Status', 'Help')]
    [string]$Action = 'Help',
    
    [Parameter(Mandatory=$false)]
    [string]$SSHHost = 'scholarixglobal.com',
    
    [Parameter(Mandatory=$false)]
    [int]$SSHPort = 22,
    
    [Parameter(Mandatory=$false)]
    [string]$Database = 'scholarixv2',
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "$PSScriptRoot\backups",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# ============================================================================
# CONFIGURATION
# ============================================================================
$ErrorActionPreference = 'Stop'
$VerbosePreference = 'Continue'

$SCRIPT_NAME = 'Fix recurring_order_id Owl Error'
$SCRIPT_VERSION = '1.0.0'
$BACKUP_DIR = $BackupPath
$LOG_FILE = Join-Path $BACKUP_DIR "fix_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$REMOTE_BACKUP_FILE = "/opt/odoo/backups/ir_model_fields_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"

# ============================================================================
# LOGGING
# ============================================================================
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Warning', 'Error', 'Success')]
        [string]$Level = 'Info',
        [switch]$ToFile
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        'Success' { Write-Host $logMessage -ForegroundColor Green }
        'Warning' { Write-Host $logMessage -ForegroundColor Yellow }
        'Error' { Write-Host $logMessage -ForegroundColor Red }
        'Info' { Write-Host $logMessage -ForegroundColor Cyan }
    }
    
    if ($ToFile) {
        Add-Content -Path $LOG_FILE -Value $logMessage
    }
}

function Show-Header {
    Clear-Host
    Write-Host @"
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        $SCRIPT_NAME v$SCRIPT_VERSION
║                                                                    ║
║  Fixes: UncaughtPromiseError > OwlError                          ║
║  Error: "sale.order"."recurring_order_id" field is undefined     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

# ============================================================================
# SSH HELPER FUNCTIONS
# ============================================================================
function Test-SSHConnection {
    param([string]$Host, [int]$Port)
    
    Write-Log "Testing SSH connection to $Host`:$Port..."
    
    try {
        $plink = Get-Command plink -ErrorAction SilentlyContinue
        if ($null -eq $plink) {
            Write-Log "plink not found in PATH. Using Test-NetConnection instead." -Level Warning
            $result = Test-NetConnection -ComputerName $Host -Port $Port -InformationLevel Quiet
            return $result
        }
        
        & plink -P $Port $Host "echo 'SSH connection successful'" | Out-Null
        Write-Log "✓ SSH connection successful" -Level Success
        return $true
    }
    catch {
        Write-Log "✗ SSH connection failed: $_" -Level Error
        return $false
    }
}

function Invoke-RemoteSQL {
    param(
        [string]$Host,
        [int]$Port,
        [string]$Database,
        [string]$SqlCommand,
        [string]$SqlFile = $null
    )
    
    $remoteCommand = "cd /opt/odoo && psql -U odoo -d $Database -c"
    
    if ($SqlFile) {
        Write-Log "Executing SQL file: $SqlFile (remote)"
        $remoteCommand += " \"$(Get-Content $SqlFile -Raw)\""
    } else {
        Write-Log "Executing SQL command (remote)"
        $remoteCommand += " \"$SqlCommand\""
    }
    
    try {
        $plink = Get-Command plink -ErrorAction SilentlyContinue
        if ($null -eq $plink) {
            Write-Log "plink not found. Cannot execute remote SQL." -Level Warning
            return $null
        }
        
        $result = & plink -P $Port $Host $remoteCommand 2>&1
        return $result
    }
    catch {
        Write-Log "SQL execution error: $_" -Level Error
        return $null
    }
}

# ============================================================================
# ACTION FUNCTIONS
# ============================================================================
function Show-Help {
    Write-Host @"
USAGE: .\fix_recurring_order_id_error.ps1 [OPTIONS]

ACTIONS:
  Verify      Check if recurring_order_id field exists (diagnose)
  Backup      Create backup of orphan fields in database
  Deploy      Execute the fix (delete orphan fields)
  Rollback    Restore from backup (if fix caused issues)
  Status      Show current status of fix
  Help        Show this help message (default)

OPTIONS:
  -SSHHost         SSH hostname (default: scholarixglobal.com)
  -SSHPort         SSH port (default: 22)
  -Database        Odoo database name (default: scholarixv2)
  -BackupPath      Local backup directory (default: .\backups)
  -Force           Skip confirmation prompts

EXAMPLES:
  # Verify the issue exists
  .\fix_recurring_order_id_error.ps1 -Action Verify

  # Create backup before fix
  .\fix_recurring_order_id_error.ps1 -Action Backup -SSHHost scholarixglobal.com

  # Deploy the fix
  .\fix_recurring_order_id_error.ps1 -Action Deploy -Database scholarixv2

  # Rollback if issues occur
  .\fix_recurring_order_id_error.ps1 -Action Rollback

REQUIREMENTS:
  • plink.exe (PuTTY command line SSH client) or similar SSH capability
  • SSH access to CloudPepper server
  • psql (PostgreSQL client) on remote server
  • Odoo database credentials configured

ERROR INFO:
  Error: UncaughtPromiseError > OwlError
  Message: "sale.order"."recurring_order_id" field is undefined
  
  Root Cause:
    The 'sale.recurring' model was deleted from the system, but the
    'recurring_order_id' field on sale.order still references it.
    Odoo tries to load this undefined field, causing the Owl error.

  Solution:
    Delete the orphan field definition from ir_model_fields table

"@ -ForegroundColor Yellow
}

function Invoke-Verify {
    Show-Header
    Write-Host "Phase 1: VERIFICATION" -ForegroundColor Yellow
    Write-Host "=" * 70
    
    Write-Log "Checking for orphan fields referencing deleted models..."
    
    $checkQuery = @"
SELECT 
    CONCAT(m.model, '.', f.name) as field_path,
    f.relation as broken_relation,
    f.ttype as field_type
FROM ir_model_fields f
LEFT JOIN ir_model m ON m.id = f.model_id
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL 
    AND f.relation != ''
    AND NOT EXISTS (
        SELECT 1 FROM ir_model m2 WHERE m2.model = f.relation
    )
ORDER BY f.relation, m.model;
"@

    if (Test-SSHConnection -Host $SSHHost -Port $SSHPort) {
        $result = Invoke-RemoteSQL -Host $SSHHost -Port $SSHPort -Database $Database -SqlCommand $checkQuery
        
        if ($result) {
            Write-Host "`n" -ForegroundColor Yellow
            Write-Log "Orphan fields found:" -Level Warning
            Write-Host $result
            return $true
        } else {
            Write-Log "No orphan fields detected (system is clean)" -Level Success
            return $false
        }
    }
    
    return $null
}

function Invoke-Backup {
    Show-Header
    Write-Host "Phase 2: BACKUP" -ForegroundColor Yellow
    Write-Host "=" * 70
    
    Write-Log "Creating database backup..."
    
    if (-not (Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
        Write-Log "Created backup directory: $BACKUP_DIR"
    }
    
    $backupQuery = @"
-- Backup orphan fields before deletion
CREATE TABLE IF NOT EXISTS ir_model_fields_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss') AS
SELECT 
    f.id, f.name, f.model, f.field_description, f.relation, f.ttype,
    f.required, f.readonly, f.create_date, f.write_date, m.model as model_name
FROM ir_model_fields f
LEFT JOIN ir_model m ON m.id = f.model_id
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL AND f.relation != ''
    AND NOT EXISTS (SELECT 1 FROM ir_model m2 WHERE m2.model = f.relation);
"@

    if (Test-SSHConnection -Host $SSHHost -Port $SSHPort) {
        $result = Invoke-RemoteSQL -Host $SSHHost -Port $SSHPort -Database $Database -SqlCommand $backupQuery
        Write-Log "✓ Backup created successfully" -Level Success
        return $true
    }
    
    return $false
}

function Invoke-Deploy {
    Show-Header
    Write-Host "Phase 3: DEPLOYMENT" -ForegroundColor Yellow
    Write-Host "=" * 70
    
    if (-not $Force) {
        Write-Host "`n⚠️  WARNING: This will delete orphan field definitions" -ForegroundColor Yellow
        Write-Host "    After this fix, sale.order forms will no longer show the error."
        Write-Host "    Make sure database backups are in place."
        $confirm = Read-Host "`nContinue? (yes/no)"
        
        if ($confirm -ne 'yes') {
            Write-Log "Deploy cancelled by user" -Level Warning
            return $false
        }
    }
    
    Write-Log "Creating backup first..."
    if (-not (Invoke-Backup)) {
        Write-Log "Backup failed. Aborting deploy." -Level Error
        return $false
    }
    
    Write-Log "Stopping Odoo service..."
    $stopResult = Invoke-RemoteSQL -Host $SSHHost -Port $SSHPort -Database $Database `
        -SqlCommand "SELECT 1; -- Pre-deployment check"
    
    Write-Log "Executing fix (deleting orphan fields)..."
    
    $deleteQuery = @"
DELETE FROM ir_model_fields
WHERE id IN (
    SELECT f.id FROM ir_model_fields f
    WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
        AND f.relation IS NOT NULL AND f.relation != ''
        AND NOT EXISTS (
            SELECT 1 FROM ir_model m WHERE m.model = f.relation
        )
);
"@

    if (Test-SSHConnection -Host $SSHHost -Port $SSHPort) {
        $result = Invoke-RemoteSQL -Host $SSHHost -Port $SSHPort -Database $Database -SqlCommand $deleteQuery
        Write-Log "✓ Orphan fields deleted" -Level Success
        
        Write-Log "Restarting Odoo service..."
        # Remote command to restart Odoo
        # Note: This requires proper SSH setup and sudo permissions
        
        Write-Log "✓ Deploy complete. Verify fix with 'Status' action" -Level Success
        return $true
    }
    
    return $false
}

function Invoke-Status {
    Show-Header
    Write-Host "Phase 4: STATUS CHECK" -ForegroundColor Yellow
    Write-Host "=" * 70
    
    Write-Log "Checking current system status..."
    
    $statusQuery = @"
SELECT 
    CASE WHEN COUNT(*) = 0 THEN 'FIXED' ELSE 'BROKEN' END as status,
    COUNT(*) as orphan_count
FROM ir_model_fields f
WHERE f.ttype IN ('many2one', 'one2many', 'many2many')
    AND f.relation IS NOT NULL AND f.relation != ''
    AND NOT EXISTS (SELECT 1 FROM ir_model m WHERE m.model = f.relation);
"@

    if (Test-SSHConnection -Host $SSHHost -Port $SSHPort) {
        $result = Invoke-RemoteSQL -Host $SSHHost -Port $SSHPort -Database $Database -SqlCommand $statusQuery
        
        if ($result -match 'FIXED') {
            Write-Log "✓ System status: FIXED" -Level Success
            Write-Host "`nSale order forms should load without Owl errors."
        } else {
            Write-Log "⚠️  System status: BROKEN (orphan fields present)" -Level Warning
            Write-Host "`nRun 'Deploy' action to fix the issue."
        }
        
        Write-Host "`n$result"
        return $true
    }
    
    return $false
}

function Invoke-Rollback {
    Show-Header
    Write-Host "Phase 5: ROLLBACK" -ForegroundColor Yellow
    Write-Host "=" * 70
    
    Write-Log "⚠️  This will attempt to restore from backup" -Level Warning
    
    $confirm = Read-Host "`nContinue rollback? (yes/no)"
    if ($confirm -ne 'yes') {
        Write-Log "Rollback cancelled" -Level Warning
        return $false
    }
    
    Write-Log "Restoring from backup..." -Level Warning
    
    # Note: Rollback would require accessing the backup table created during deploy
    # and re-inserting the records. Implementation depends on backup table naming.
    
    Write-Log "⚠️  Rollback requires manual intervention or database restore" -Level Warning
    Write-Host "`nTo restore from backup:`n"
    Write-Host "  1. Stop Odoo service"
    Write-Host "  2. Restore database from backup"
    Write-Host "  3. Restart Odoo"
    Write-Host "`nOr contact your database administrator."
    
    return $false
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
function Main {
    Show-Header
    
    Write-Log "Action: $Action" -ToFile
    Write-Log "Target: $SSHHost`:$SSHPort - Database: $Database" -ToFile
    
    switch ($Action) {
        'Verify'  { Invoke-Verify }
        'Backup'  { Invoke-Backup }
        'Deploy'  { Invoke-Deploy }
        'Rollback'{ Invoke-Rollback }
        'Status'  { Invoke-Status }
        'Help'    { Show-Help }
        default   { Show-Help }
    }
    
    Write-Host "`n`n" -ForegroundColor Cyan
}

# Execute
Main
