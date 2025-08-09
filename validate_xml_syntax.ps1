# XML Validation Script for Account Payment Final (PowerShell)
# This script checks all XML files for syntax errors

Write-Host "🔍 XML Syntax Validation for Account Payment Final" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Find all XML files in the module
$xmlFiles = Get-ChildItem -Path "account_payment_final" -Filter "*.xml" -Recurse

Write-Host "📁 Found XML files:" -ForegroundColor Yellow
$xmlFiles | ForEach-Object { Write-Host "  $($_.FullName)" }
Write-Host ""

$errorCount = 0
$successCount = 0

# Validate each XML file
foreach ($file in $xmlFiles) {
    Write-Host "Checking $($file.Name)... " -NoNewline
    
    try {
        # Load XML file to validate syntax
        $xml = New-Object System.Xml.XmlDocument
        $xml.Load($file.FullName)
        
        Write-Host "✅ VALID" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "❌ INVALID" -ForegroundColor Red
        Write-Host "Error details:" -ForegroundColor Yellow
        Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        $errorCount++
    }
}

Write-Host ""
Write-Host "📊 Validation Summary:" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "✅ Valid files: $successCount" -ForegroundColor Green
Write-Host "❌ Invalid files: $errorCount" -ForegroundColor Red

if ($errorCount -eq 0) {
    Write-Host ""
    Write-Host "🎉 All XML files are valid! Module ready for installation." -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "⚠️  Found $errorCount XML syntax errors. Please fix before installing." -ForegroundColor Red
    exit 1
}
