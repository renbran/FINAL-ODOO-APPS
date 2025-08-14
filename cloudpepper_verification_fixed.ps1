# CloudPepper Deployment Verification
# Run after applying fixes

Write-Host "=== CloudPepper Deployment Verification ===" -ForegroundColor Cyan

# Check 1: JavaScript syntax validation
Write-Host "`nChecking JavaScript files..." -ForegroundColor Yellow
$jsErrors = 0
Get-ChildItem -Recurse -Include "*.js" | ForEach-Object {
    try {
        # Basic syntax check - looking for common issues
        $content = Get-Content $_.FullName -Raw
        if ($content -match '^\s*]' -or $content -match ',\s*\n\s*}' -or $content -match ',\s*\n\s*]') {
            Write-Host "Potential syntax issue in: $($_.Name)" -ForegroundColor Red
            $jsErrors++
        }
    }
    catch {
        Write-Host "Error reading: $($_.Name)" -ForegroundColor Red
        $jsErrors++
    }
}

if ($jsErrors -eq 0) {
    Write-Host "Check mark No JavaScript syntax issues detected" -ForegroundColor Green
} else {
    Write-Host "X Found $jsErrors potential JavaScript issues" -ForegroundColor Red
}

# Check 2: SCSS variable consistency
Write-Host "`nChecking SCSS variables..." -ForegroundColor Yellow
$scssErrors = 0
Get-ChildItem -Recurse -Include "*.scss" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match '\$mk-color-' -and $content -match '\$mk_color_') {
        Write-Host "Inconsistent variable naming in: $($_.Name)" -ForegroundColor Red
        $scssErrors++
    }
}

if ($scssErrors -eq 0) {
    Write-Host "Check mark SCSS variables are consistent" -ForegroundColor Green
} else {
    Write-Host "X Found $scssErrors SCSS variable inconsistencies" -ForegroundColor Red
}

# Check 3: Required SQL fix files
Write-Host "`nChecking fix files..." -ForegroundColor Yellow
$requiredFiles = @("autovacuum_fix.sql", "datetime_fix.sql")
$missingFiles = 0

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "Check mark Found: $file" -ForegroundColor Green
    } else {
        Write-Host "X Missing: $file" -ForegroundColor Red
        $missingFiles++
    }
}

# Summary
Write-Host "`n=== Verification Summary ===" -ForegroundColor Cyan
if ($jsErrors -eq 0 -and $scssErrors -eq 0 -and $missingFiles -eq 0) {
    Write-Host "Check mark All checks passed - Ready for deployment" -ForegroundColor Green
    exit 0
} else {
    Write-Host "X Issues found - Review before deployment" -ForegroundColor Red
    exit 1
}
