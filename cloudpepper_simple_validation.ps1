# CloudPepper Final Validation Script

Write-Host "CloudPepper Final Validation" -ForegroundColor Green
Write-Host "Checking for ES6 module issues..." -ForegroundColor Yellow

# Check critical files for ES6 import/export statements
$criticalFiles = @(
    "account_payment_final\static\src\js\cloudpepper_critical_interceptor.js",
    "account_payment_final\static\src\js\cloudpepper_js_error_handler.js", 
    "account_payment_final\static\src\js\emergency_error_fix.js"
)

$allClean = $true

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $hasImport = $content -match "^\s*import\s+" -or $content -match "\nimport\s+"
        $hasExport = $content -match "^\s*export\s+" -or $content -match "\nexport\s+"
        
        $fileName = Split-Path $file -Leaf
        
        if ($hasImport -or $hasExport) {
            Write-Host "ERROR: $fileName still has ES6 module syntax" -ForegroundColor Red
            $allClean = $false
        } else {
            Write-Host "OK: $fileName is clean" -ForegroundColor Green
        }
    } else {
        Write-Host "ERROR: $file not found" -ForegroundColor Red
        $allClean = $false
    }
}

# Check for MutationObserver protection
Write-Host "`nChecking MutationObserver protection..." -ForegroundColor Yellow

$interceptorFile = "account_payment_final\static\src\js\cloudpepper_critical_interceptor.js"
if (Test-Path $interceptorFile) {
    $content = Get-Content $interceptorFile -Raw
    if ($content -match "MutationObserver" -and $content -match "nodeType") {
        Write-Host "OK: MutationObserver protection found" -ForegroundColor Green
    } else {
        Write-Host "ERROR: MutationObserver protection missing" -ForegroundColor Red
        $allClean = $false
    }
}

# Summary
Write-Host "`nSUMMARY:" -ForegroundColor Cyan
if ($allClean) {
    Write-Host "READY FOR DEPLOYMENT" -ForegroundColor Green
    Write-Host "All files should now work without ES6 import errors" -ForegroundColor White
    Write-Host "MutationObserver protection is in place" -ForegroundColor White
    Write-Host "`nNext: Restart Odoo and test in browser" -ForegroundColor Yellow
} else {
    Write-Host "ISSUES DETECTED - Review errors above" -ForegroundColor Red
}
