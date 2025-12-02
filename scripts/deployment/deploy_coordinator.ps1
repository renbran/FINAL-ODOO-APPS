# ============================================================================
# RENTAL MANAGEMENT v3.4.0 - WINDOWS-BASED DEPLOYMENT COORDINATOR
# ============================================================================
# Purpose: Deploy and monitor rental_management v3.4.0 from Windows to CloudPepper
# Features: SSH monitoring, log analysis, remote command execution, rollback prep
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('check', 'backup', 'deploy', 'monitor', 'verify', 'rollback')]
    [string]$Action = 'check',
    
    [Parameter(Mandatory=$false)]
    [string]$SSHHost = '139.84.163.11',
    
    [Parameter(Mandatory=$false)]
    [string]$SSHUser = 'odoo',
    
    [Parameter(Mandatory=$false)]
    [string]$SSHKey = 'C:\Users\branm\.ssh\id_ed25519_scholarix',
    
    [Parameter(Mandatory=$false)]
    [string]$Database = 'scholarixv2',
    
    [Parameter(Mandatory=$false)]
    [int]$MonitoringDuration = 900  # 15 minutes in seconds
)

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"
$Blue = "Blue"

# Configuration
$ModuleName = "rental_management"
$ModuleVersion = "3.4.0"
$LocalModulePath = "d:\RUNNING APPS\FINAL-ODOO-APPS\rental_management"
$RemoteModulePath = "/opt/odoo/addons/rental_management"
$RemoteOdooPath = "/opt/odoo"
$BackupDir = "d:\backups\deployment"
$LogDir = "$BackupDir\logs"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-ColorOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param($Title)
    Write-ColorOutput "`n" 
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════════════" $Cyan
    Write-ColorOutput "  $Title" $Yellow
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════════════" $Cyan
    Write-ColorOutput "`n"
}

function Write-Section {
    param($Title)
    Write-ColorOutput "`n$Title`n" $Blue
}

function Test-SSHConnection {
    Write-Section "[TEST] SSH Connection"
    
    Write-ColorOutput "Testing SSH connection to $SSHHost..."
    
    try {
        $result = ssh -i $SSHKey -o ConnectTimeout=5 -o BatchMode=yes -o PasswordAuthentication=no `
            "$SSHUser@$SSHHost" "echo 'SSH connection successful'" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ SSH connection established" $Green
            return $true
        } else {
            Write-ColorOutput "❌ SSH authentication failed" $Red
            Write-ColorOutput "Error: $result" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ SSH connection error: $_" $Red
        return $false
    }
}

function Get-RemoteModuleStatus {
    Write-Section "[CHECK] Remote Module Status"
    
    Write-ColorOutput "Checking module status in $Database database..."
    
    $query = @"
SELECT name, state, installed_version, latest_version 
FROM ir_module_module 
WHERE name='$ModuleName';
"@
    
    try {
        $psqlCmd = "PGPASSWORD=odoo psql -h localhost -U odoo -d $Database -t -c `"$query`""
        $result = ssh -i $SSHKey -o ConnectTimeout=10 `
            "$SSHUser@$SSHHost" $psqlCmd 2>&1
        
        Write-ColorOutput "Query Result:" $Blue
        Write-ColorOutput $result
        
        if ($result -match "rental_management") {
            if ($result -match "installed.*3.4.0") {
                Write-ColorOutput "✅ Module v3.4.0 already installed" $Green
                return @{ Status = "AlreadyInstalled"; Version = "3.4.0" }
            } elseif ($result -match "installed") {
                $version = [regex]::Match($result, "installed\s+\|\s+([\d.]+)").Groups[1].Value
                Write-ColorOutput "⏳ Module installed but older version: $version" $Yellow
                return @{ Status = "NeedsUpgrade"; Version = $version }
            } elseif ($result -match "uninstalled") {
                Write-ColorOutput "⚠️  Module not installed yet" $Yellow
                return @{ Status = "NotInstalled"; Version = "none" }
            }
        }
        
        return @{ Status = "Unknown"; Version = "unknown" }
    } catch {
        Write-ColorOutput "❌ Error checking module status: $_" $Red
        return @{ Status = "Error"; Version = "unknown" }
    }
}

function Get-RemoteModuleInfo {
    Write-Section "[INFO] Remote Module Information"
    
    try {
        $cmd = "ls -lh $RemoteModulePath && du -sh $RemoteModulePath"
        $result = ssh -i $SSHKey -o ConnectTimeout=10 "$SSHUser@$SSHHost" $cmd 2>&1
        
        Write-ColorOutput $result
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Module directory exists on server" $Green
            return $true
        } else {
            Write-ColorOutput "⚠️  Module directory not found or access denied" $Yellow
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Error: $_" $Red
        return $false
    }
}

function Backup-RemoteModule {
    Write-Section "[BACKUP] Remote Module & Database"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "${ModuleName}_${timestamp}"
    
    Write-ColorOutput "Creating backup: $backupName"
    
    try {
        # Create backup directory
        $backupCmd = @"
mkdir -p /tmp/backups && \
cd /tmp/backups && \
tar -czf ${backupName}_module.tar.gz -C /opt/odoo/addons rental_management && \
PGPASSWORD=odoo pg_dump -U odoo $Database | gzip > ${backupName}_db.sql.gz && \
ls -lh ${backupName}*
"@
        
        $result = ssh -i $SSHKey -o ConnectTimeout=30 `
            "$SSHUser@$SSHHost" $backupCmd 2>&1
        
        Write-ColorOutput "Backup completed:`n$result" $Green
        
        # Save backup info
        $backupInfo = @{
            Timestamp = $timestamp
            ModuleBackup = "/tmp/backups/${backupName}_module.tar.gz"
            DbBackup = "/tmp/backups/${backupName}_db.sql.gz"
            LocalBackupDir = "$BackupDir\$timestamp"
        }
        
        # Create local backup directory
        if (-not (Test-Path $backupInfo.LocalBackupDir)) {
            New-Item -ItemType Directory -Path $backupInfo.LocalBackupDir -Force | Out-Null
        }
        
        # Save backup info file
        $backupInfo | ConvertTo-Json | Out-File -FilePath "$($backupInfo.LocalBackupDir)\backup_info.json"
        
        Write-ColorOutput "✅ Backup information saved locally" $Green
        return $backupInfo
    } catch {
        Write-ColorOutput "❌ Backup error: $_" $Red
        return $null
    }
}

function Deploy-Module {
    Write-Section "[DEPLOY] Module Update"
    
    Write-ColorOutput "Starting module deployment..."
    Write-ColorOutput "Action: Module install/update via Odoo"
    
    try {
        $deployCmd = @"
sudo systemctl stop odoo && \
sleep 3 && \
/opt/odoo/odoo-bin -u $ModuleName -d $Database --stop-after-init 2>&1 && \
sudo systemctl start odoo && \
sleep 5
"@
        
        Write-ColorOutput "Executing deployment command (this may take 2-5 minutes)..."
        $result = ssh -i $SSHKey -o ConnectTimeout=300 `
            "$SSHUser@$SSHHost" $deployCmd 2>&1
        
        Write-ColorOutput "Deployment result:" $Blue
        Write-ColorOutput $result
        
        # Check if deployment was successful
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Module deployment completed" $Green
            return $true
        } else {
            Write-ColorOutput "⚠️  Deployment returned status: $LASTEXITCODE" $Yellow
            return $null
        }
    } catch {
        Write-ColorOutput "❌ Deployment error: $_" $Red
        return $false
    }
}

function Verify-Deployment {
    Write-Section "[VERIFY] Post-Deployment Verification"
    
    Write-ColorOutput "Verifying deployment..."
    
    try {
        # Check module status
        $query = "SELECT state, installed_version FROM ir_module_module WHERE name='$ModuleName';"
        $psqlCmd = "PGPASSWORD=odoo psql -h localhost -U odoo -d $Database -t -c `"$query`""
        $result = ssh -i $SSHKey -o ConnectTimeout=10 "$SSHUser@$SSHHost" $psqlCmd 2>&1
        
        Write-ColorOutput "Module Status: $result" $Blue
        
        if ($result -match "installed.*3.4.0") {
            Write-ColorOutput "✅ Module v3.4.0 successfully deployed!" $Green
            return $true
        } else {
            Write-ColorOutput "⚠️  Module status unclear, check logs" $Yellow
            return $null
        }
    } catch {
        Write-ColorOutput "❌ Verification error: $_" $Red
        return $false
    }
}

function Monitor-Logs {
    Write-Section "[MONITOR] Real-time Log Monitoring"
    
    $startTime = Get-Date
    $endTime = $startTime.AddSeconds($MonitoringDuration)
    
    Write-ColorOutput "Monitoring logs for $MonitoringDuration seconds..."
    Write-ColorOutput "Press Ctrl+C to stop monitoring"
    
    try {
        $logCmd = "tail -f /var/log/odoo/odoo.log | head -n 100"
        $result = ssh -i $SSHKey -o ConnectTimeout=300 "$SSHUser@$SSHHost" $logCmd 2>&1
        
        Write-ColorOutput "Recent Log Entries:" $Blue
        $result | ForEach-Object {
            if ($_ -match "ERROR|WARNING|CRITICAL") {
                Write-ColorOutput $_ $Red
            } elseif ($_ -match "INFO.*rental_management|updated") {
                Write-ColorOutput $_ $Green
            } else {
                Write-ColorOutput $_
            }
        }
    } catch {
        Write-ColorOutput "Monitoring interrupted or completed" $Yellow
    }
}

function Prepare-Rollback {
    param($BackupInfo)
    
    Write-Section "[ROLLBACK] Preparing Rollback Procedure"
    
    if ($null -eq $BackupInfo) {
        Write-ColorOutput "⚠️  No backup information available" $Yellow
        return
    }
    
    $rollbackScript = @"
#!/bin/bash
# Rollback script for rental_management deployment
# Timestamp: $($BackupInfo.Timestamp)

echo "=========================================="
echo "ROLLBACK: rental_management module"
echo "=========================================="
echo ""

echo "[1/3] Stopping Odoo service..."
sudo systemctl stop odoo
sleep 3

echo "[2/3] Restoring database from backup..."
gunzip -c $($BackupInfo.DbBackup) | PGPASSWORD=odoo psql -U odoo $Database

echo "[3/3] Restoring module from backup..."
tar -xzf $($BackupInfo.ModuleBackup) -C /opt/odoo/addons/

echo "[4/3] Starting Odoo service..."
sudo systemctl start odoo
sleep 5

if systemctl is-active --quiet odoo; then
    echo "✅ Rollback completed successfully!"
else
    echo "❌ Odoo service failed to start after rollback"
    exit 1
fi
"@
    
    $localRollbackPath = "$($BackupInfo.LocalBackupDir)\rollback.sh"
    $rollbackScript | Out-File -FilePath $localRollbackPath -Encoding UTF8
    
    Write-ColorOutput "✅ Rollback script prepared:" $Green
    Write-ColorOutput "   Location: $localRollbackPath" $Green
    Write-ColorOutput "   Remote DB Backup: $($BackupInfo.DbBackup)" $Blue
    Write-ColorOutput "   Remote Module Backup: $($BackupInfo.ModuleBackup)" $Blue
    
    Write-ColorOutput "`nTo execute rollback:"
    Write-ColorOutput "   scp -i $SSHKey $localRollbackPath $SSHUser@$SSHHost:/tmp/" $Yellow
    Write-ColorOutput "   ssh -i $SSHKey $SSHUser@$SSHHost 'bash /tmp/rollback.sh'" $Yellow
}

function Show-Summary {
    param($BackupInfo, $DeploymentSuccess)
    
    Write-Header "DEPLOYMENT SUMMARY"
    
    Write-ColorOutput "Module: $ModuleName" $Blue
    Write-ColorOutput "Version: $ModuleVersion" $Blue
    Write-ColorOutput "Database: $Database" $Blue
    Write-ColorOutput "Server: $SSHHost" $Blue
    
    Write-ColorOutput "`nDeployment Status:" $Blue
    if ($DeploymentSuccess -eq $true) {
        Write-ColorOutput "✅ SUCCESSFUL" $Green
    } elseif ($DeploymentSuccess -eq $false) {
        Write-ColorOutput "❌ FAILED" $Red
    } else {
        Write-ColorOutput "⚠️  UNCERTAIN (check logs)" $Yellow
    }
    
    if ($BackupInfo) {
        Write-ColorOutput "`nBackup Information:" $Blue
        Write-ColorOutput "  Timestamp: $($BackupInfo.Timestamp)" $Green
        Write-ColorOutput "  DB Backup: $($BackupInfo.DbBackup)" $Green
        Write-ColorOutput "  Module Backup: $($BackupInfo.ModuleBackup)" $Green
        Write-ColorOutput "  Local Dir: $($BackupInfo.LocalBackupDir)" $Green
    }
    
    Write-ColorOutput "`nNext Steps:" $Blue
    Write-ColorOutput "  1. Monitor Odoo logs: tail -f /var/log/odoo/odoo.log" $Yellow
    Write-ColorOutput "  2. Test SPA generation and payment plans" $Yellow
    Write-ColorOutput "  3. If issues occur, use rollback script" $Yellow
    Write-ColorOutput "`n"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    Write-Header "RENTAL MANAGEMENT v3.4.0 DEPLOYMENT COORDINATOR"
    
    # Ensure directories exist
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    # Validate SSH key
    if (-not (Test-Path $SSHKey)) {
        Write-ColorOutput "❌ SSH key not found: $SSHKey" $Red
        Write-ColorOutput "Please provide valid SSH key path" $Red
        exit 1
    }
    
    Write-ColorOutput "SSH Key: $(Split-Path -Leaf $SSHKey)" $Blue
    Write-ColorOutput "Target: $SSHUser@$SSHHost" $Blue
    Write-ColorOutput "Action: $Action`n" $Blue
    
    # Execute requested action
    switch ($Action) {
        'check' {
            if (Test-SSHConnection) {
                $status = Get-RemoteModuleStatus
                Get-RemoteModuleInfo
                
                Write-ColorOutput "`n📊 DEPLOYMENT DECISION:" $Cyan
                switch ($status.Status) {
                    "AlreadyInstalled" { 
                        Write-ColorOutput "✅ No action needed - module already at target version" $Green 
                    }
                    "NeedsUpgrade" { 
                        Write-ColorOutput "⏳ Upgrade recommended - run: .\$($MyInvocation.MyCommand.Name) -Action deploy" $Yellow 
                    }
                    "NotInstalled" { 
                        Write-ColorOutput "📦 Installation needed - run: .\$($MyInvocation.MyCommand.Name) -Action deploy" $Yellow 
                    }
                    default { 
                        Write-ColorOutput "❓ Unable to determine status" $Red 
                    }
                }
            }
        }
        
        'backup' {
            if (Test-SSHConnection) {
                $backupInfo = Backup-RemoteModule
                Show-Summary -BackupInfo $backupInfo
            }
        }
        
        'deploy' {
            if (Test-SSHConnection) {
                $status = Get-RemoteModuleStatus
                
                if ($status.Status -eq "AlreadyInstalled") {
                    Write-ColorOutput "Module is already at target version, deployment not needed" $Green
                } else {
                    $backupInfo = Backup-RemoteModule
                    $deploySuccess = Deploy-Module
                    Start-Sleep -Seconds 5
                    $verifySuccess = Verify-Deployment
                    
                    Prepare-Rollback -BackupInfo $backupInfo
                    Show-Summary -BackupInfo $backupInfo -DeploymentSuccess $deploySuccess
                }
            }
        }
        
        'monitor' {
            if (Test-SSHConnection) {
                Monitor-Logs
            }
        }
        
        'verify' {
            if (Test-SSHConnection) {
                $status = Get-RemoteModuleStatus
                Verify-Deployment | Out-Null
            }
        }
        
        'rollback' {
            Write-ColorOutput "❌ Rollback functionality requires manual execution" $Red
            Write-ColorOutput "Please use the rollback script generated during deployment" $Yellow
        }
    }
    
} catch {
    Write-ColorOutput "`n❌ Error: $_" $Red
    exit 1
}
