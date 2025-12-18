# SSH Key Setup Guide for CloudPepper Server
# Target: root@139.84.163.11 (Port 22)

## Step 1: Generate SSH Key Pair (Run in PowerShell)

```powershell
# Create .ssh directory if it doesn't exist
$sshDir = "$env:USERPROFILE\.ssh"
if (!(Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force
    Write-Host "✅ Created .ssh directory: $sshDir" -ForegroundColor Green
}

# Generate SSH key pair
$keyName = "cloudpepper_key"
$keyPath = "$sshDir\$keyName"

Write-Host "Generating SSH key pair..." -ForegroundColor Cyan
Write-Host "Key will be saved to: $keyPath" -ForegroundColor Gray

ssh-keygen -t ed25519 -C "cloudpepper-access-$(Get-Date -Format 'yyyy-MM-dd')" -f $keyPath -N '""'

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH key pair generated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Private key: $keyPath" -ForegroundColor Yellow
    Write-Host "Public key: $keyPath.pub" -ForegroundColor Yellow
} else {
    Write-Host "❌ Key generation failed!" -ForegroundColor Red
    exit 1
}
```

## Step 2: Display Public Key (Copy This)

```powershell
# Display the public key
$publicKey = Get-Content "$env:USERPROFILE\.ssh\cloudpepper_key.pub"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YOUR PUBLIC KEY (Copy this):" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host $publicKey -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Copy to clipboard automatically
$publicKey | Set-Clipboard
Write-Host "✅ Public key copied to clipboard!" -ForegroundColor Green
```

## Step 3: Add Public Key to Server (Choose One Method)

### Method A: Using Password Authentication (One-Time)

```powershell
# You'll be prompted for root password
$publicKey = Get-Content "$env:USERPROFILE\.ssh\cloudpepper_key.pub"

ssh root@139.84.163.11 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# Test the connection
ssh -i "$env:USERPROFILE\.ssh\cloudpepper_key" root@139.84.163.11 "echo 'SSH key authentication successful!'"
```

### Method B: Manual Setup (If Method A Fails)

1. Connect with password:
```powershell
ssh root@139.84.163.11
```

2. On the server, run:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Paste your public key here
# Save: Ctrl+O, Enter, Ctrl+X
chmod 600 ~/.ssh/authorized_keys
```

3. Exit and test:
```powershell
ssh -i "$env:USERPROFILE\.ssh\cloudpepper_key" root@139.84.163.11 "echo 'Success!'"
```

## Step 4: Configure SSH Client (Recommended)

```powershell
# Create/Update SSH config file
$sshConfig = "$env:USERPROFILE\.ssh\config"

$configContent = @"
# CloudPepper Server
Host cloudpepper
    HostName 139.84.163.11
    User root
    Port 22
    IdentityFile ~/.ssh/cloudpepper_key
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Alias for IP address
Host 139.84.163.11
    User root
    Port 22
    IdentityFile ~/.ssh/cloudpepper_key
    IdentitiesOnly yes
"@

Add-Content -Path $sshConfig -Value $configContent
Write-Host "✅ SSH config updated!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now connect using:" -ForegroundColor Cyan
Write-Host "  ssh cloudpepper" -ForegroundColor White
Write-Host "  ssh root@139.84.163.11" -ForegroundColor White
```

## Step 5: Test Connection

```powershell
# Test with alias
Write-Host "Testing connection..." -ForegroundColor Cyan
ssh cloudpepper "echo 'Connected successfully!' && hostname && uptime"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SSH key authentication working!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ Connection test failed. Check configuration." -ForegroundColor Yellow
}
```

## Troubleshooting

### Error: Permission Denied (publickey)

**Solution 1: Check key permissions**
```powershell
# On Windows, ensure key file has correct permissions
icacls "$env:USERPROFILE\.ssh\cloudpepper_key" /inheritance:r
icacls "$env:USERPROFILE\.ssh\cloudpepper_key" /grant:r "$env:USERNAME:(R)"
```

**Solution 2: Verify public key on server**
```bash
# SSH to server with password
ssh root@139.84.163.11

# Check authorized_keys
cat ~/.ssh/authorized_keys

# Verify permissions
ls -la ~/.ssh/
# Should show: drwx------ (700) for .ssh
# Should show: -rw------- (600) for authorized_keys
```

### Error: Connection Refused

**Check if SSH service is running:**
```bash
ssh root@139.84.163.11 "systemctl status sshd"
```

### Error: Timeout

**Check firewall/port:**
```powershell
Test-NetConnection -ComputerName 139.84.163.11 -Port 22
```

## Security Best Practices

1. ✅ **Never share your private key** (`cloudpepper_key`)
2. ✅ **Back up your private key** securely
3. ✅ **Use key-based auth** instead of passwords
4. ✅ **Set passphrase** for extra security (optional)
5. ✅ **Regularly rotate keys** (every 6-12 months)

## Quick Commands Reference

```powershell
# Connect to server
ssh cloudpepper
ssh root@139.84.163.11

# Copy files to server
scp file.txt cloudpepper:/tmp/
scp -r folder/ cloudpepper:/var/odoo/

# Copy files from server
scp cloudpepper:/var/log/odoo/odoo.log ./

# Run command without interactive shell
ssh cloudpepper "systemctl status odoo"

# Run multiple commands
ssh cloudpepper "cd /var/odoo && ls -la"
```

## Update fix_remote_assets.ps1 Script

After setting up SSH keys, you won't need to specify credentials:

```powershell
# Original (with parameters)
.\fix_remote_assets.ps1 -SSHUser "root" -SSHHost "139.84.163.11"

# New (uses SSH config)
.\fix_remote_assets.ps1
# OR
.\fix_remote_assets.ps1 -SSHHost "cloudpepper"
```

## Verification Checklist

- [ ] SSH key pair generated in `~\.ssh\`
- [ ] Public key added to server's `~/.ssh/authorized_keys`
- [ ] SSH config file created/updated
- [ ] Connection test successful: `ssh cloudpepper "echo OK"`
- [ ] Password-less authentication working
- [ ] fix_remote_assets.ps1 script can connect

## Next Steps

Once SSH keys are configured:

1. ✅ Run the asset fix script:
```powershell
cd "d:\RUNNING APPS\FINAL-ODOO-APPS"
.\fix_remote_assets.ps1
```

2. ✅ Deploy rental_management updates:
```powershell
.\quick_deploy.ps1 deploy
```

3. ✅ Monitor server logs:
```powershell
ssh cloudpepper "tail -f /var/odoo/scholarixv2/logs/odoo.log"
```

---

**Generated**: November 30, 2025
**Target Server**: root@139.84.163.11 (CloudPepper/Vultr)
**Purpose**: Secure SSH access for Odoo deployment automation
