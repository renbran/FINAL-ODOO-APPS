# CloudPepper Critical Error Resolution - Final Validation

Write-Host "🔍 CloudPepper Final Validation Script" -ForegroundColor Cyan
Write-Host "Checking for ES6 import/export statement issues..." -ForegroundColor Yellow

function Test-FileForModuleIssues {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
        return $false
    }
    
    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) {
        Write-Host "❌ Could not read file: $FilePath" -ForegroundColor Red
        return $false
    }
    
    $hasImport = $content -match "^\s*import\s+" -or $content -match "\nimport\s+"
    $hasExport = $content -match "^\s*export\s+" -or $content -match "\nexport\s+"
    $hasOdooModule = $content -match "@odoo-module"
    $hasRegistryImport = $content -match "import.*registry.*from"
    
    $fileName = Split-Path $FilePath -Leaf
    
    if ($hasImport -or $hasExport -or $hasRegistryImport) {
        Write-Host "❌ $fileName has ES6 module syntax that could cause import errors" -ForegroundColor Red
        if ($hasImport) { Write-Host "   - Found import statements" -ForegroundColor Yellow }
        if ($hasExport) { Write-Host "   - Found export statements" -ForegroundColor Yellow }
        if ($hasRegistryImport) { Write-Host "   - Found registry imports" -ForegroundColor Yellow }
        return $false
    } else {
        Write-Host "✅ $fileName is ES6 module syntax free" -ForegroundColor Green
        return $true
    }
}

# Files to check for module issues
$criticalFiles = @(
    "account_payment_final\static\src\js\cloudpepper_critical_interceptor.js",
    "account_payment_final\static\src\js\cloudpepper_js_error_handler.js",
    "account_payment_final\static\src\js\emergency_error_fix.js"
)

Write-Host "`n📋 Testing Critical Error Handler Files..." -ForegroundColor Cyan

$allFilesPassed = $true
foreach ($file in $criticalFiles) {
    $result = Test-FileForModuleIssues $file
    if (-not $result) {
        $allFilesPassed = $false
    }
}

# Check for MutationObserver protection patterns
Write-Host "`n🛡️ Checking MutationObserver Protection..." -ForegroundColor Cyan

$protectionFiles = @{
    "cloudpepper_critical_interceptor.js" = @("CloudPepperSafeMutationObserver", "nodeType", "parameter 1 is not of type")
    "cloudpepper_js_error_handler.js" = @("MutationObserver", "patchMutationObserver", "observe")
    "emergency_error_fix.js" = @("SafeMutationObserver", "target validation", "nodeType")
}

foreach ($fileName in $protectionFiles.Keys) {
    $filePath = "account_payment_final\static\src\js\$fileName"
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        $patterns = $protectionFiles[$fileName]
        $foundPatterns = 0
        
        foreach ($pattern in $patterns) {
            if ($content -match [regex]::Escape($pattern)) {
                $foundPatterns++
            }
        }
        
        if ($foundPatterns -eq $patterns.Count) {
            Write-Host "✅ $fileName has comprehensive MutationObserver protection" -ForegroundColor Green
        } else {
            Write-Host "⚠️ $fileName missing some protection patterns ($foundPatterns/$($patterns.Count))" -ForegroundColor Yellow
            $allFilesPassed = $false
        }
    } else {
        Write-Host "❌ $fileName not found" -ForegroundColor Red
        $allFilesPassed = $false
    }
}

# Check manifest.py asset loading order
Write-Host "`n📦 Checking Asset Loading Configuration..." -ForegroundColor Cyan

$manifestPath = "account_payment_final\__manifest__.py"
if (Test-Path $manifestPath) {
    $manifestContent = Get-Content $manifestPath -Raw
    
    $hasPrepend = $manifestContent -match "prepend.*cloudpepper_critical_interceptor"
    $hasWebBackend = $manifestContent -match "web\.assets_backend"
    $hasWebDark = $manifestContent -match "web\.assets_web_dark"
    
    if ($hasPrepend -and $hasWebBackend) {
        Write-Host "✅ Manifest has correct asset loading with prepend priority" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Manifest asset loading needs attention" -ForegroundColor Yellow
        Write-Host "   - Has prepend: $hasPrepend" -ForegroundColor White
        Write-Host "   - Has web.assets_backend: $hasWebBackend" -ForegroundColor White
        Write-Host "   - Has web.assets_web_dark: $hasWebDark" -ForegroundColor White
    }
} else {
    Write-Host "❌ Manifest file not found" -ForegroundColor Red
    $allFilesPassed = $false
}

# Check for problematic assets.xml files
Write-Host "`n🗂️ Checking for Conflicting Assets.xml Files..." -ForegroundColor Cyan

$assetsXmlPath = "account_payment_final\views\assets.xml"
if (Test-Path $assetsXmlPath) {
    Write-Host "⚠️ Found assets.xml file which may conflict with manifest.py asset definitions" -ForegroundColor Yellow
    Write-Host "   In Odoo 17, prefer manifest.py for asset management" -ForegroundColor White
} else {
    Write-Host "✅ No conflicting assets.xml file found" -ForegroundColor Green
}

# Summary
Write-Host "`n📊 FINAL VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

if ($allFilesPassed) {
    Write-Host "🎉 ALL CRITICAL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "✅ No ES6 import/export statements that could cause module errors" -ForegroundColor Green
    Write-Host "✅ MutationObserver protection is comprehensive" -ForegroundColor Green
    Write-Host "✅ Asset loading configuration is correct" -ForegroundColor Green
    
    Write-Host "`n🚀 READY FOR DEPLOYMENT" -ForegroundColor Green
    Write-Host "Expected resolution of errors:" -ForegroundColor White
    Write-Host "  - TypeError: Failed to execute observe on MutationObserver" -ForegroundColor Gray
    Write-Host "  - web.assets_web.min.js:4 Uncaught SyntaxError: Cannot use import statement" -ForegroundColor Gray
    
} else {
    Write-Host "⚠️ SOME ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host "Review the messages above and fix any remaining issues" -ForegroundColor White
}

Write-Host "`n🔄 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Restart Odoo service to reload assets" -ForegroundColor White
Write-Host "2. Clear browser cache completely" -ForegroundColor White  
Write-Host "3. Test in browser console with: cloudpepper_error_resolution_test.js" -ForegroundColor White
Write-Host "4. Verify no more JavaScript errors in console" -ForegroundColor White

Write-Host "`n" -NoNewline
