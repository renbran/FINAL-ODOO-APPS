# CLOUDPEPPER EMERGENCY DEPLOYMENT - PowerShell Script
# For deploying the Monetary field fix from Windows to CloudPepper server

param(
    [string]$ServerIP = "vultr", # Replace with actual CloudPepper server IP
    [string]$Username = "root"
)

Write-Host "🚨 CLOUDPEPPER EMERGENCY DEPLOYMENT: Monetary @ Operator Fix" -ForegroundColor Red

# Check if scripts exist
$bashScript = "CLOUDPEPPER_MONETARY_FIELD_EMERGENCY_FIX.sh"
$pythonScript = "cloudpepper_monetary_emergency_fix.py"

if (-not (Test-Path $bashScript)) {
    Write-Host "❌ ERROR: $bashScript not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $pythonScript)) {
    Write-Host "❌ ERROR: $pythonScript not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Scripts found, proceeding with deployment..." -ForegroundColor Green

# Upload scripts using SCP (requires OpenSSH client)
Write-Host "📤 Uploading emergency fix scripts to CloudPepper..." -ForegroundColor Yellow

try {
    # Upload bash script
    scp $bashScript "${Username}@${ServerIP}:/tmp/"
    if ($LASTEXITCODE -ne 0) { throw "Failed to upload bash script" }
    
    # Upload python script
    scp $pythonScript "${Username}@${ServerIP}:/tmp/"
    if ($LASTEXITCODE -ne 0) { throw "Failed to upload python script" }
    
    Write-Host "✅ Scripts uploaded successfully" -ForegroundColor Green
    
    # Execute the fix
    Write-Host "🔧 Executing emergency fix on CloudPepper..." -ForegroundColor Yellow
    
    # SSH and execute the bash script
    $sshCommand = "chmod +x /tmp/$bashScript && sudo /tmp/$bashScript"
    ssh "${Username}@${ServerIP}" $sshCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ EMERGENCY FIX DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "🎯 CloudPepper Monetary @ Operator TypeError RESOLVED" -ForegroundColor Cyan
        
        # Test the deployment
        Write-Host "🧪 Testing CloudPepper accessibility..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "https://stagingtry.cloudpepper.site/" -UseBasicParsing -TimeoutSec 30
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ CloudPepper is accessible!" -ForegroundColor Green
            } else {
                Write-Host "⚠️  CloudPepper returned status: $($response.StatusCode)" -ForegroundColor Orange
            }
        } catch {
            Write-Host "⚠️  Could not test CloudPepper accessibility: $($_.Exception.Message)" -ForegroundColor Orange
        }
        
    } else {
        Write-Host "❌ Emergency fix failed, trying Python alternative..." -ForegroundColor Red
        
        # Try python script as fallback
        $sshCommand2 = "sudo python3 /tmp/$pythonScript"
        ssh "${Username}@${ServerIP}" $sshCommand2
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python emergency fix succeeded!" -ForegroundColor Green
        } else {
            Write-Host "❌ Both emergency fixes failed - manual intervention required" -ForegroundColor Red
            Write-Host "📋 Manual fix instructions in CLOUDPEPPER_MONETARY_EMERGENCY_DEPLOYMENT.md" -ForegroundColor Yellow
            exit 1
        }
    }
    
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔄 Try manual deployment using SSH" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n🏁 EMERGENCY DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "🔗 CloudPepper: https://stagingtry.cloudpepper.site/" -ForegroundColor Blue
Write-Host "👤 Login: salescompliance@osusproperties.com" -ForegroundColor Blue

# Show next steps
Write-Host "`n📋 POST-DEPLOYMENT CHECKLIST:" -ForegroundColor Yellow
Write-Host "1. ✅ Verify CloudPepper loads without errors"
Write-Host "2. ✅ Test order_status_override module functionality"
Write-Host "3. ✅ Check Odoo logs for any remaining issues"
Write-Host "4. ✅ Validate sales order creation and status changes"
