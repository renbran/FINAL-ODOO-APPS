# ============================================================================
# RENTAL MANAGEMENT MODULE TRANSFER TO CLOUDPEPPER
# ============================================================================
# Purpose: Transfer upgraded rental_management module (v3.4.0) to production
# Server: 139.84.163.11 (CloudPepper)
# Destination: /opt/odoo/addons/rental_management
# ============================================================================

param(
    [string]$RemoteUser = "odoo",
    [string]$RemoteHost = "139.84.163.11",
    [string]$RemotePath = "/opt/odoo/addons",
    [string]$SshKey = "$env:USERPROFILE\.ssh\id_ed25519_139.84.163.11"
)

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TRANSFERRING RENTAL MANAGEMENT MODULE TO CLOUDPEPPER (v3.4.0)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Configuration
$LocalModule = "$PSScriptRoot\rental_management"
$ModuleName = "rental_management"
$RemoteLocation = "$RemoteUser@$RemoteHost"

Write-Host "📋 TRANSFER CONFIGURATION:" -ForegroundColor Green
Write-Host "  SSH Key:       $($SshKey | Split-Path -Leaf)"
Write-Host "  Remote User:   $RemoteUser"
Write-Host "  Remote Host:   $RemoteHost"
Write-Host "  Destination:   $RemotePath"
Write-Host "  Module:        $ModuleName (v3.4.0)"
Write-Host ""

# Verify local module exists
if (-not (Test-Path $LocalModule)) {
    Write-Host "❌ ERROR: Local module not found at: $LocalModule" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Local module verified: $LocalModule" -ForegroundColor Green
Write-Host ""

# Check SSH key exists
if (-not (Test-Path $SshKey)) {
    Write-Host "❌ ERROR: SSH key not found at: $SshKey" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available SSH keys for 139.84.163.11:" -ForegroundColor Yellow
    Get-ChildItem "$env:USERPROFILE\.ssh" | Where-Object { $_.Name -like "*ed25519*139*" -or $_.Name -like "*cloudpepper*" } | ForEach-Object {
        Write-Host "  • $($_.Name)"
    }
    exit 1
}

Write-Host "✅ SSH key verified: $($SshKey | Split-Path -Leaf)" -ForegroundColor Green
Write-Host ""

# Test SSH connection
Write-Host "🔗 Testing SSH connection..." -ForegroundColor Yellow
$testConnection = ssh -i $SshKey -o ConnectTimeout=10 -o StrictHostKeyChecking=no $RemoteLocation "echo 'Connection successful'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH Connection successful!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "❌ SSH Connection failed!" -ForegroundColor Red
    Write-Host "Error: $testConnection" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "  1. Verify SSH key is added to ~/.ssh/authorized_keys on remote server"
    Write-Host "  2. Check SSH key permissions (should be 600)"
    Write-Host "  3. Verify network connectivity to 139.84.163.11:22"
    exit 1
}

# Backup existing module on remote
Write-Host "💾 Backing up existing module on remote server..." -ForegroundColor Yellow
ssh -i $SshKey -o StrictHostKeyChecking=no $RemoteLocation "
if [ -d $RemotePath/$ModuleName ]; then
    echo 'Backing up existing module...'
    cd $RemotePath
    cp -r $ModuleName ${ModuleName}.backup.\$(date +%Y%m%d_%H%M%S)
    echo 'Backup complete'
else
    echo 'No existing module to backup'
fi
" 2>&1 | ForEach-Object { Write-Host "   $_" }

Write-Host ""

# Transfer module using SCP
Write-Host "📤 Transferring module files..." -ForegroundColor Yellow
Write-Host "   Source:      $LocalModule" -ForegroundColor Gray
Write-Host "   Destination: $RemoteLocation`:$RemotePath" -ForegroundColor Gray
Write-Host ""

scp -r -i $SshKey -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$LocalModule" "$RemoteLocation:$RemotePath/" 2>&1 | ForEach-Object {
    if ($_ -match "100%|rental_management") {
        Write-Host "   ✓ $_" -ForegroundColor Green
    } else {
        Write-Host "   $_"
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Transfer failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Module transferred successfully!" -ForegroundColor Green
Write-Host ""

# Verify module on remote
Write-Host "🔍 Verifying module on remote server..." -ForegroundColor Yellow
ssh -i $SshKey -o StrictHostKeyChecking=no $RemoteLocation "
cd $RemotePath/$ModuleName
echo 'Module Structure:'
ls -la | head -15
echo ''
echo 'Version Check:'
grep '\"version\"' __manifest__.py
" 2>&1 | ForEach-Object { Write-Host "   $_" }

Write-Host ""

# Show next steps
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ TRANSFER COMPLETE - NEXT STEPS" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "On the remote server (139.84.163.11), run these commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Update the module in Odoo" -ForegroundColor Gray
Write-Host "  ssh odoo@139.84.163.11" -ForegroundColor Cyan
Write-Host "  cd /opt/odoo" -ForegroundColor Cyan
Write-Host "  ./odoo-bin -u rental_management --stop-after-init" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # Or via sudo if needed:" -ForegroundColor Gray
Write-Host "  sudo systemctl stop odoo" -ForegroundColor Cyan
Write-Host "  sudo /opt/odoo/odoo-bin -u rental_management --stop-after-init" -ForegroundColor Cyan
Write-Host "  sudo systemctl start odoo" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # Monitor logs:" -ForegroundColor Gray
Write-Host "  tail -f /var/log/odoo/odoo.log" -ForegroundColor Cyan
Write-Host ""
Write-Host "Module Details:" -ForegroundColor Yellow
Write-Host "  • Version: 3.4.0" -ForegroundColor Gray
Write-Host "  • Changes: SPA Report with Bank Account Integration" -ForegroundColor Gray
Write-Host "  • Commits: f645114d, 25b012d6" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
