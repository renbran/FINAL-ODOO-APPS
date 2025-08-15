# Quick verification for CloudPepper RPC fix
Write-Host "=== CloudPepper RPC Fix Verification ===" -ForegroundColor Cyan

# Check if fix files exist
$fixFiles = @("autovacuum_fix.sql", "datetime_fix.sql")
$allFound = $true

foreach ($file in $fixFiles) {
    if (Test-Path $file) {
        Write-Host "✓ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: $file" -ForegroundColor Red
        $allFound = $false
    }
}

# Check backup directory
$backupDirs = Get-ChildItem -Directory -Filter "CloudPepper_Backup_*" | Sort-Object CreationTime -Descending
if ($backupDirs.Count -gt 0) {
    Write-Host "✓ Backup available: $($backupDirs[0].Name)" -ForegroundColor Green
} else {
    Write-Host "✗ No backup found" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Next Action Required ===" -ForegroundColor Yellow
if ($allFound) {
    Write-Host "1. Apply database fixes to CloudPepper" -ForegroundColor White
    Write-Host "2. Restart Odoo service via CloudPepper control panel" -ForegroundColor White
    Write-Host "3. Test RPC functionality" -ForegroundColor White
} else {
    Write-Host "Re-run emergency fix script first" -ForegroundColor Red
}
