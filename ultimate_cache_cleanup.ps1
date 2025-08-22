# ULTIMATE CACHE & TRACK CLEANUP SCRIPT
# This script will permanently delete all cache, temporary files, and tracking data

Write-Host "=== ULTIMATE ODOO CACHE & TRACK CLEANUP ===" -ForegroundColor Red
Write-Host "WARNING: This will permanently delete ALL cache and temporary files!" -ForegroundColor Yellow

$startLocation = Get-Location
$totalDeleted = 0

try {
    # 1. Delete all __pycache__ directories
    Write-Host "`n1. Removing __pycache__ directories..." -ForegroundColor Cyan
    $pycacheDirs = Get-ChildItem -Path . -Recurse -Directory -Force | Where-Object { $_.Name -eq "__pycache__" }
    foreach ($dir in $pycacheDirs) {
        try {
            Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($dir.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($dir.FullName)" -ForegroundColor Red
        }
    }

    # 2. Delete all .pyc files
    Write-Host "`n2. Removing .pyc files..." -ForegroundColor Cyan
    $pycFiles = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { $_.Extension -eq ".pyc" }
    foreach ($file in $pycFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($file.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($file.FullName)" -ForegroundColor Red
        }
    }

    # 3. Delete all .log files
    Write-Host "`n3. Removing log files..." -ForegroundColor Cyan
    $logFiles = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { $_.Extension -eq ".log" }
    foreach ($file in $logFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($file.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($file.FullName)" -ForegroundColor Red
        }
    }

    # 4. Delete temporary JSON files
    Write-Host "`n4. Removing temporary JSON files..." -ForegroundColor Cyan
    $tempJsonFiles = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { 
        $_.Extension -eq ".json" -and 
        ($_.Name -like "*report*" -or $_.Name -like "*validation*" -or $_.Name -like "*test*" -or $_.Name -like "*temp*")
    }
    foreach ($file in $tempJsonFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($file.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($file.FullName)" -ForegroundColor Red
        }
    }

    # 5. Delete .DS_Store files (Mac)
    Write-Host "`n5. Removing .DS_Store files..." -ForegroundColor Cyan
    $dsFiles = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { $_.Name -eq ".DS_Store" }
    foreach ($file in $dsFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($file.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($file.FullName)" -ForegroundColor Red
        }
    }

    # 6. Delete Thumbs.db files (Windows)
    Write-Host "`n6. Removing Thumbs.db files..." -ForegroundColor Cyan
    $thumbsFiles = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { $_.Name -eq "Thumbs.db" }
    foreach ($file in $thumbsFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($file.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($file.FullName)" -ForegroundColor Red
        }
    }

    # 7. Clean git cache and reset tracking
    Write-Host "`n7. Cleaning Git cache and tracking..." -ForegroundColor Cyan
    try {
        # Remove cached files from git index
        git rm -r --cached . 2>$null
        git add . 2>$null
        Write-Host "   Git cache cleaned" -ForegroundColor Green
    } catch {
        Write-Host "   Git cache cleanup failed" -ForegroundColor Red
    }

    # 8. Delete IDE/Editor temporary files
    Write-Host "`n8. Removing IDE temporary files..." -ForegroundColor Cyan
    $ideFiles = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { 
        $_.Name -like "*.tmp" -or 
        $_.Name -like "*.swp" -or 
        $_.Name -like "*.swo" -or
        $_.Name -like "*~" -or
        $_.Name -like ".#*"
    }
    foreach ($file in $ideFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            Write-Host "   Deleted: $($file.FullName)" -ForegroundColor Green
            $totalDeleted++
        } catch {
            Write-Host "   Failed: $($file.FullName)" -ForegroundColor Red
        }
    }

    # 9. Final verification
    Write-Host "`n9. Final verification..." -ForegroundColor Cyan
    $remainingCache = Get-ChildItem -Path . -Recurse -Directory -Force | Where-Object { $_.Name -eq "__pycache__" }
    $remainingPyc = Get-ChildItem -Path . -Recurse -File -Force | Where-Object { $_.Extension -eq ".pyc" }
    
    Write-Host "`n=== CLEANUP SUMMARY ===" -ForegroundColor Yellow
    Write-Host "Total items deleted: $totalDeleted" -ForegroundColor Green
    Write-Host "Remaining __pycache__ dirs: $($remainingCache.Count)" -ForegroundColor $(if($remainingCache.Count -eq 0) { "Green" } else { "Red" })
    Write-Host "Remaining .pyc files: $($remainingPyc.Count)" -ForegroundColor $(if($remainingPyc.Count -eq 0) { "Green" } else { "Red" })
    
    if ($remainingCache.Count -eq 0 -and $remainingPyc.Count -eq 0) {
        Write-Host "`n✅ CLEANUP SUCCESSFUL - ALL CACHE DELETED!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Some files may still remain - check manually" -ForegroundColor Yellow
    }

} catch {
    Write-Host "`nERROR during cleanup: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Set-Location $startLocation
}

Write-Host "`n=== CLEANUP COMPLETE ===" -ForegroundColor Red
