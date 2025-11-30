# Automated SSH Key Setup for CloudPepper Server
# Target: root@139.84.163.11

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerIP = "139.84.163.11",
    
    [Parameter(Mandatory=$false)]
    [string]$ServerUser = "root",
    
    [Parameter(Mandatory=$false)]
    [string]$KeyName = "cloudpepper_key"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSH KEY SETUP FOR CLOUDPEPPER" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create .ssh directory
Write-Host "Step 1: Setting up SSH directory..." -ForegroundColor Green
$sshDir = "$env:USERPROFILE\.ssh"

if (!(Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Host "✅ Created: $sshDir" -ForegroundColor Green
} else {
    Write-Host "✅ Directory exists: $sshDir" -ForegroundColor Green
}

$keyPath = "$sshDir\$KeyName"

# Check if key already exists
if (Test-Path $keyPath) {
    Write-Host ""
    Write-Host "⚠️  SSH key already exists: $keyPath" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite existing key? (y/n)"
    
    if ($overwrite -ne "y") {
        Write-Host "Keeping existing key. Skipping to configuration..." -ForegroundColor Cyan
        $skipKeyGen = $true
    } else {
        Remove-Item $keyPath -Force
        Remove-Item "$keyPath.pub" -Force -ErrorAction SilentlyContinue
        $skipKeyGen = $false
    }
} else {
    $skipKeyGen = $false
}

# Step 2: Generate SSH key
if (-not $skipKeyGen) {
    Write-Host ""
    Write-Host "Step 2: Generating SSH key pair..." -ForegroundColor Green
    Write-Host "Location: $keyPath" -ForegroundColor Gray
    
    # Generate ed25519 key (more secure and faster than RSA)
    $keyComment = "cloudpepper-$(Get-Date -Format 'yyyyMMdd')"
    
    & ssh-keygen -t ed25519 -C $keyComment -f $keyPath -N '""'
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH key pair generated successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Key generation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Step 2: Using existing SSH key" -ForegroundColor Green
}

# Step 3: Display and copy public key
Write-Host ""
Write-Host "Step 3: Preparing public key..." -ForegroundColor Green

if (!(Test-Path "$keyPath.pub")) {
    Write-Host "❌ Public key not found: $keyPath.pub" -ForegroundColor Red
    exit 1
}

$publicKey = Get-Content "$keyPath.pub" -Raw
$publicKey = $publicKey.Trim()

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YOUR PUBLIC KEY:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host $publicKey -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

# Copy to clipboard
try {
    $publicKey | Set-Clipboard
    Write-Host "✅ Public key copied to clipboard!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not copy to clipboard automatically" -ForegroundColor Yellow
}

# Step 4: Add key to server
Write-Host ""
Write-Host "Step 4: Adding public key to server..." -ForegroundColor Green
Write-Host "Server: ${ServerUser}@${ServerIP}" -ForegroundColor Gray
Write-Host ""
Write-Host "You will be prompted for the server password." -ForegroundColor Yellow
Write-Host ""

# Escape special characters in public key for bash
$escapedKey = $publicKey -replace '"', '\"'

$sshCommand = @"
mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$escapedKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SSH key added successfully!'
"@

try {
    ssh "${ServerUser}@${ServerIP}" $sshCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Public key added to server!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Failed to add key automatically" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Manual steps:" -ForegroundColor Cyan
        Write-Host "1. SSH to server: ssh ${ServerUser}@${ServerIP}" -ForegroundColor White
        Write-Host "2. Run: mkdir -p ~/.ssh && chmod 700 ~/.ssh" -ForegroundColor White
        Write-Host "3. Run: nano ~/.ssh/authorized_keys" -ForegroundColor White
        Write-Host "4. Paste your public key (already in clipboard)" -ForegroundColor White
        Write-Host "5. Save and exit: Ctrl+O, Enter, Ctrl+X" -ForegroundColor White
        Write-Host "6. Run: chmod 600 ~/.ssh/authorized_keys" -ForegroundColor White
        Write-Host ""
        
        $manual = Read-Host "Press Enter after manually adding the key, or 'q' to quit"
        if ($manual -eq 'q') {
            exit 1
        }
    }
} catch {
    Write-Host "❌ Error connecting to server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please add the key manually (it's in your clipboard)" -ForegroundColor Yellow
    exit 1
}

# Step 5: Configure SSH client
Write-Host ""
Write-Host "Step 5: Configuring SSH client..." -ForegroundColor Green

$sshConfigPath = "$sshDir\config"
$configExists = Test-Path $sshConfigPath

# Read existing config or create new
if ($configExists) {
    $existingConfig = Get-Content $sshConfigPath -Raw
} else {
    $existingConfig = ""
}

# Check if cloudpepper host already configured
if ($existingConfig -match "Host cloudpepper") {
    Write-Host "⚠️  'cloudpepper' host already exists in SSH config" -ForegroundColor Yellow
    $updateConfig = Read-Host "Update configuration? (y/n)"
    
    if ($updateConfig -eq "y") {
        # Remove old cloudpepper config
        $existingConfig = $existingConfig -replace "(?s)# CloudPepper Server.*?(?=Host |$)", ""
    } else {
        Write-Host "Keeping existing configuration" -ForegroundColor Cyan
        $skipConfig = $true
    }
}

if (-not $skipConfig) {
    $newConfig = @"

# CloudPepper Server - Added $(Get-Date -Format 'yyyy-MM-dd HH:mm')
Host cloudpepper
    HostName $ServerIP
    User $ServerUser
    Port 22
    IdentityFile ~/.ssh/$KeyName
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host $ServerIP
    User $ServerUser
    Port 22
    IdentityFile ~/.ssh/$KeyName
    IdentitiesOnly yes

"@

    Add-Content -Path $sshConfigPath -Value $newConfig
    Write-Host "✅ SSH config updated: $sshConfigPath" -ForegroundColor Green
}

# Step 6: Set key permissions (Windows)
Write-Host ""
Write-Host "Step 6: Setting key permissions..." -ForegroundColor Green

try {
    # Remove inheritance and set owner-only permissions
    icacls $keyPath /inheritance:r | Out-Null
    icacls $keyPath /grant:r "$env:USERNAME:(R)" | Out-Null
    Write-Host "✅ Key permissions configured" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not set permissions automatically (non-critical)" -ForegroundColor Yellow
}

# Step 7: Test connection
Write-Host ""
Write-Host "Step 7: Testing SSH key authentication..." -ForegroundColor Green
Write-Host "Attempting to connect..." -ForegroundColor Gray
Write-Host ""

Start-Sleep -Seconds 2

try {
    $testResult = ssh -i $keyPath -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" "${ServerUser}@${ServerIP}" "echo 'SUCCESS' && hostname && uptime"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✅ SSH KEY AUTHENTICATION WORKING!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Server response:" -ForegroundColor Cyan
        Write-Host $testResult -ForegroundColor White
    } else {
        Write-Host "⚠️  Connection test returned non-zero exit code" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Connection test failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Verify public key was added to server: ssh ${ServerUser}@${ServerIP} 'cat ~/.ssh/authorized_keys'" -ForegroundColor White
    Write-Host "2. Check SSH service: ssh ${ServerUser}@${ServerIP} 'systemctl status sshd'" -ForegroundColor White
    Write-Host "3. Review SSH logs: ssh ${ServerUser}@${ServerIP} 'tail -50 /var/log/auth.log'" -ForegroundColor White
}

# Final summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Key files created:" -ForegroundColor Cyan
Write-Host "  Private key: $keyPath" -ForegroundColor White
Write-Host "  Public key:  $keyPath.pub" -ForegroundColor White
Write-Host "  SSH config:  $sshConfigPath" -ForegroundColor White
Write-Host ""
Write-Host "Quick commands:" -ForegroundColor Cyan
Write-Host "  Connect:     ssh cloudpepper" -ForegroundColor White
Write-Host "  Or:          ssh ${ServerUser}@${ServerIP}" -ForegroundColor White
Write-Host "  Copy file:   scp file.txt cloudpepper:/tmp/" -ForegroundColor White
Write-Host "  Run command: ssh cloudpepper 'systemctl status odoo'" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test connection: ssh cloudpepper" -ForegroundColor White
Write-Host "2. Run asset fix: .\fix_remote_assets.ps1" -ForegroundColor White
Write-Host "3. Deploy modules: .\quick_deploy.ps1 deploy" -ForegroundColor White
Write-Host ""

# Offer to test connection now
$testNow = Read-Host "Open SSH session now to verify? (y/n)"
if ($testNow -eq "y") {
    Write-Host ""
    Write-Host "Opening SSH session..." -ForegroundColor Cyan
    ssh cloudpepper
}

Write-Host ""
Write-Host "Setup completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
