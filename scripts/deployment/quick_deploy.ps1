# ============================================================================
# RENTAL MANAGEMENT v3.4.0 - QUICK START DEPLOYMENT
# ============================================================================
# Purpose: Simplified one-command deployment for scholarship module
# Usage: .\quick_deploy.ps1
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('status', 'backup', 'deploy', 'verify', 'rollback', 'help')]
    [string]$Action = 'status',
    
    [switch]$SkipConfirm
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$Config = @{
    SSHHost = "139.84.163.11"
    SSHUser = "odoo"
    SSHKey = "C:\Users\branm\.ssh\id_ed25519_scholarix"
    Database = "scholarixv2"
    ModuleName = "rental_management"
    ModuleVersion = "3.4.0"
    BackupDir = "d:\backups\deployment"
    RemoteBackupDir = "/tmp/backups"
}

$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Blue"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Title {
    param($Text)
    Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Header
    Write-Host "║ $($Text.PadRight(64)) ║" -ForegroundColor $Colors.Header
    Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor $Colors.Header
}

function Write-Step {
    param($Number, $Text)
    Write-Host "[$Number] $Text" -ForegroundColor $Colors.Info
}

function Write-Success {
    param($Text)
    Write-Host "    ✅ $Text" -ForegroundColor $Colors.Success
}

function Write-Warning {
    param($Text)
    Write-Host "    ⚠️  $Text" -ForegroundColor $Colors.Warning
}

function Write-Error {
    param($Text)
    Write-Host "    ❌ $Text" -ForegroundColor $Colors.Error
}

function Confirm-Action {
    param($Message, $DefaultYes = $false)
    
    if ($SkipConfirm) {
        return $true
    }
    
    $default = if ($DefaultYes) { "&Yes" } else { "&No" }
    $yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes"
    $no = New-Object System.Management.Automation.Host.ChoiceDescription "&No"
    $choices = [System.Management.Automation.Host.ChoiceDescription[]]($yes, $no)
    
    $result = $host.UI.PromptForChoice($Message, "", $choices, if ($DefaultYes) { 0 } else { 1 })
    return ($result -eq 0)
}

function Test-SSH {
    Write-Step "1" "Testing SSH connection..."
    try {
        $result = ssh -i $Config.SSHKey -o ConnectTimeout=5 -o BatchMode=yes `
            "$($Config.SSHUser)@$($Config.SSHHost)" "echo OK" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "SSH connection working"
            return $true
        } else {
            Write-Error "SSH authentication failed"
            return $false
        }
    } catch {
        Write-Error "SSH error: $_"
        return $false
    }
}

function Get-ModuleStatus {
    Write-Step "2" "Checking module status..."
    try {
        $query = "SELECT state, installed_version FROM ir_module_module WHERE name='$($Config.ModuleName)';"
        $psqlCmd = "PGPASSWORD=odoo psql -h localhost -U odoo -d $($Config.Database) -t -c `"$query`""
        $result = ssh -i $Config.SSHKey -o ConnectTimeout=10 "$($Config.SSHUser)@$($Config.SSHHost)" $psqlCmd 2>&1
        
        Write-Host "    Result: $result" -ForegroundColor $Colors.Info
        
        if ($result -match "installed.*3.4.0") {
            Write-Success "Module already at v3.4.0"
            return "UpToDate"
        } elseif ($result -match "installed") {
            Write-Warning "Module installed but needs upgrade"
            return "NeedsUpgrade"
        } else {
            Write-Warning "Module not yet installed"
            return "NotInstalled"
        }
    } catch {
        Write-Error "Failed to check status: $_"
        return "Unknown"
    }
}

function Create-Backup {
    Write-Step "3" "Creating backups..."
    
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupCmd = @"
mkdir -p $($Config.RemoteBackupDir) && \
cd $($Config.RemoteBackupDir) && \
tar -czf rental_management_${timestamp}_module.tar.gz -C /opt/odoo/addons rental_management && \
PGPASSWORD=odoo pg_dump -U odoo $($Config.Database) | gzip > rental_management_${timestamp}_db.sql.gz && \
ls -lh rental_management_${timestamp}*
"@
        
        $result = ssh -i $Config.SSHKey -o ConnectTimeout=60 `
            "$($Config.SSHUser)@$($Config.SSHHost)" $backupCmd 2>&1
        
        Write-Success "Backups created"
        Write-Host "    $result" -ForegroundColor $Colors.Info
        
        return @{ Timestamp = $timestamp; Success = $true }
    } catch {
        Write-Error "Backup failed: $_"
        return @{ Timestamp = ""; Success = $false }
    }
}

function Deploy-Module {
    Write-Step "4" "Deploying module..."
    
    try {
        Write-Host "    This may take 2-3 minutes..." -ForegroundColor $Colors.Warning
        
        $deployCmd = @"
sudo systemctl stop odoo && \
sleep 3 && \
/opt/odoo/odoo-bin -u $($Config.ModuleName) -d $($Config.Database) --stop-after-init 2>&1 | tail -5 && \
sudo systemctl start odoo && \
sleep 3 && \
systemctl is-active odoo
"@
        
        $result = ssh -i $Config.SSHKey -o ConnectTimeout=300 `
            "$($Config.SSHUser)@$($Config.SSHHost)" $deployCmd 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Module deployed successfully"
            return $true
        } else {
            Write-Warning "Deployment completed with status: $LASTEXITCODE"
            return $null
        }
    } catch {
        Write-Error "Deployment error: $_"
        return $false
    }
}

function Verify-Deployment {
    Write-Step "5" "Verifying deployment..."
    
    try {
        Start-Sleep -Seconds 3
        
        $query = "SELECT state, installed_version FROM ir_module_module WHERE name='$($Config.ModuleName)';"
        $psqlCmd = "PGPASSWORD=odoo psql -h localhost -U odoo -d $($Config.Database) -t -c `"$query`""
        $result = ssh -i $Config.SSHKey -o ConnectTimeout=10 "$($Config.SSHUser)@$($Config.SSHHost)" $psqlCmd 2>&1
        
        if ($result -match "installed.*3.4.0") {
            Write-Success "✓ Module v3.4.0 successfully deployed!"
            return $true
        } else {
            Write-Warning "Module status: $result"
            return $null
        }
    } catch {
        Write-Error "Verification error: $_"
        return $false
    }
}

# ============================================================================
# MAIN ACTIONS
# ============================================================================

function Show-Help {
    Write-Title "RENTAL MANAGEMENT v3.4.0 - DEPLOYMENT HELP"
    
    Write-Host @"
USAGE:
  .\quick_deploy.ps1 [action] [options]

ACTIONS:
  status    - Check current module status (default)
  backup    - Create database and module backups only
  deploy    - Full deployment with backups and verification
  verify    - Verify deployment success
  rollback  - Show rollback instructions
  help      - Show this help message

OPTIONS:
  -SkipConfirm  - Skip confirmation prompts

EXAMPLES:
  # Check current status
  .\quick_deploy.ps1 status

  # Create backups only
  .\quick_deploy.ps1 backup

  # Full deployment (RECOMMENDED)
  .\quick_deploy.ps1 deploy

  # Full deployment without confirmations
  .\quick_deploy.ps1 deploy -SkipConfirm

  # Verify deployment success
  .\quick_deploy.ps1 verify

DEPLOYMENT TIMELINE:
  Status Check:     ~30 seconds
  Backup Creation:  ~1-2 minutes
  Module Deploy:    ~2-3 minutes
  Verification:     ~30 seconds
  ────────────────────────────────
  Total:            ~5-10 minutes

IMPORTANT:
  • Full backups are created before any deployment
  • Service downtime is ~2-3 minutes during deployment
  • No data loss - all backups preserved for rollback
  • SSH connectivity required for deployment

SUPPORT:
  For issues, see: DEPLOYMENT_GUIDE_v3.4.0.md
  For checklist: DEPLOYMENT_READY_CHECKLIST.md

"@
}

function Show-Status {
    Write-Title "RENTAL MANAGEMENT STATUS CHECK"
    
    if (-not (Test-SSH)) {
        Write-Error "Cannot proceed - SSH connection failed"
        return
    }
    
    $status = Get-ModuleStatus
    
    Write-Host "`nSUMMARY:" -ForegroundColor $Colors.Header
    Write-Host "  Server:    $($Config.SSHHost)" -ForegroundColor $Colors.Info
    Write-Host "  Database:  $($Config.Database)" -ForegroundColor $Colors.Info
    Write-Host "  Module:    $($Config.ModuleName)" -ForegroundColor $Colors.Info
    Write-Host "  Status:    $status" -ForegroundColor $Colors.Info
    
    Write-Host "`nRECOMMENDED ACTION:" -ForegroundColor $Colors.Header
    switch ($status) {
        "UpToDate" {
            Write-Host "  No action needed - module is current" -ForegroundColor $Colors.Success
        }
        "NeedsUpgrade" {
            Write-Host "  Run: .\quick_deploy.ps1 deploy" -ForegroundColor $Colors.Warning
        }
        "NotInstalled" {
            Write-Host "  Run: .\quick_deploy.ps1 deploy" -ForegroundColor $Colors.Warning
        }
        default {
            Write-Host "  Unable to determine - check logs" -ForegroundColor $Colors.Error
        }
    }
}

function Show-BackupOnly {
    Write-Title "CREATING BACKUPS ONLY"
    
    if (-not (Test-SSH)) {
        Write-Error "Cannot proceed - SSH connection failed"
        return
    }
    
    $backup = Create-Backup
    
    if ($backup.Success) {
        Write-Success "Backups created successfully"
        Write-Host "  Timestamp: $($backup.Timestamp)" -ForegroundColor $Colors.Info
        Write-Host "  Remote location: $($Config.RemoteBackupDir)/" -ForegroundColor $Colors.Info
    } else {
        Write-Error "Backup creation failed"
    }
}

function Show-Deploy {
    Write-Title "RENTAL MANAGEMENT v3.4.0 - FULL DEPLOYMENT"
    
    Write-Host "This deployment will:" -ForegroundColor $Colors.Warning
    Write-Host "  1. Create full database backup" -ForegroundColor $Colors.Warning
    Write-Host "  2. Create module file backup" -ForegroundColor $Colors.Warning
    Write-Host "  3. Stop Odoo service (~2-3 min downtime)" -ForegroundColor $Colors.Warning
    Write-Host "  4. Install/upgrade rental_management to v3.4.0" -ForegroundColor $Colors.Warning
    Write-Host "  5. Start Odoo service and verify" -ForegroundColor $Colors.Warning
    Write-Host ""
    
    if (-not (Confirm-Action "Proceed with deployment?" $false)) {
        Write-Warning "Deployment cancelled"
        return
    }
    
    if (-not (Test-SSH)) {
        Write-Error "Cannot proceed - SSH connection failed"
        return
    }
    
    $status = Get-ModuleStatus
    
    if ($status -eq "UpToDate") {
        if (Confirm-Action "Module is already v3.4.0 - Force re-deploy?" $false) {
            # Continue with deployment
        } else {
            Write-Host "Deployment cancelled" -ForegroundColor $Colors.Warning
            return
        }
    }
    
    $backup = Create-Backup
    
    if (-not $backup.Success) {
        Write-Error "Backup failed - aborting deployment"
        if (Confirm-Action "Retry deployment?" $false) {
            Show-Deploy
        }
        return
    }
    
    $deploy = Deploy-Module
    
    if ($deploy -eq $false) {
        Write-Error "Deployment failed"
        Write-Host "`nRollback instructions:" -ForegroundColor $Colors.Warning
        Write-Host "  1. Run: .\quick_deploy.ps1 rollback" -ForegroundColor $Colors.Info
        return
    }
    
    $verify = Verify-Deployment
    
    Write-Title "DEPLOYMENT COMPLETE"
    
    if ($verify -eq $true) {
        Write-Success "✓ Deployment successful!"
        Write-Host "`nNext steps:" -ForegroundColor $Colors.Header
        Write-Host "  1. Test SPA report generation" -ForegroundColor $Colors.Info
        Write-Host "  2. Test payment schedule creation" -ForegroundColor $Colors.Info
        Write-Host "  3. Monitor logs: tail -f /var/log/odoo/odoo.log" -ForegroundColor $Colors.Info
    } else {
        Write-Warning "Deployment verification unclear - check logs"
    }
    
    Write-Host "`nBackup information:" -ForegroundColor $Colors.Header
    Write-Host "  Timestamp: $($backup.Timestamp)" -ForegroundColor $Colors.Info
    Write-Host "  Backups saved at: $($Config.RemoteBackupDir)/" -ForegroundColor $Colors.Info
}

function Show-Verify {
    Write-Title "VERIFYING DEPLOYMENT"
    
    if (-not (Test-SSH)) {
        Write-Error "Cannot proceed - SSH connection failed"
        return
    }
    
    $status = Get-ModuleStatus
    Verify-Deployment | Out-Null
}

function Show-Rollback {
    Write-Title "ROLLBACK INSTRUCTIONS"
    
    Write-Host @"
If deployment had issues, rollback using these steps:

OPTION 1: Using Rollback Script (RECOMMENDED)
─────────────────────────────────────────────
1. Locate rollback script in backup directory:
   d:\backups\deployment\<timestamp>\rollback.sh

2. Copy to server:
   scp -i "C:\Users\branm\.ssh\id_ed25519_scholarix" \
     d:\backups\deployment\<timestamp>\rollback.sh \
     odoo@139.84.163.11:/tmp/

3. Execute rollback:
   ssh -i "C:\Users\branm\.ssh\id_ed25519_scholarix" \
     odoo@139.84.163.11 "bash /tmp/rollback.sh"

4. Wait for completion (~5 minutes)

5. Verify service is running:
   ssh -i "C:\Users\branm\.ssh\id_ed25519_scholarix" \
     odoo@139.84.163.11 "systemctl status odoo"

OPTION 2: Manual Rollback
──────────────────────────
1. Connect to server:
   ssh -i "C:\Users\branm\.ssh\id_ed25519_scholarix" \
     odoo@139.84.163.11

2. Stop Odoo:
   sudo systemctl stop odoo

3. Restore database backup:
   gunzip -c /tmp/backups/rental_management_*_db.sql.gz | \
     PGPASSWORD=odoo psql -U odoo $($Config.Database)

4. Restore module files:
   tar -xzf /tmp/backups/rental_management_*_module.tar.gz \
     -C /opt/odoo/addons/

5. Start Odoo:
   sudo systemctl start odoo

6. Verify:
   systemctl status odoo --no-pager

OPTION 3: Contact System Administrator
───────────────────────────────────────
If rollback scripts not available or issues persist,
contact your system administrator with:
  • Timestamp of failed deployment
  • Error messages from logs
  • Current module version

"@ -ForegroundColor $Colors.Info
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    # Validate prerequisites
    if (-not (Test-Path $Config.SSHKey)) {
        Write-Error "SSH key not found: $($Config.SSHKey)"
        exit 1
    }
    
    # Create backup directory if needed
    if (-not (Test-Path $Config.BackupDir)) {
        New-Item -ItemType Directory -Path $Config.BackupDir -Force | Out-Null
    }
    
    # Execute requested action
    switch ($Action) {
        'help' { Show-Help }
        'status' { Show-Status }
        'backup' { Show-BackupOnly }
        'deploy' { Show-Deploy }
        'verify' { Show-Verify }
        'rollback' { Show-Rollback }
        default { Show-Status }
    }
    
} catch {
    Write-Host "ERROR: $_" -ForegroundColor $Colors.Error
    exit 1
}
