# CloudPepper Odoo Restart - Windows

Write-Host "=== CloudPepper Odoo Restart ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray

# Clear local caches
Write-Host "Clearing local caches..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Recurse -Include "*.pyc" | Remove-Item -Force
Get-ChildItem -Path "." -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force

# Clear Windows temp files
$tempPaths = @("$env:TEMP\odoo_*", "$env:TMP\odoo_*")
foreach ($path in $tempPaths) {
    Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
}

Write-Host "Local cleanup complete!" -ForegroundColor Green
Write-Host "Please restart your Odoo service manually and monitor for JavaScript errors" -ForegroundColor Yellow
Write-Host "Check browser console (F12) for any remaining syntax errors" -ForegroundColor Yellow
