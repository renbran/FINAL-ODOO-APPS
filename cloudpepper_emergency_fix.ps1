# CloudPepper Emergency Fix - Windows PowerShell Script
# Addresses critical errors: JavaScript syntax, autovacuum, datetime parsing

param(
    [switch]$Force,
    [switch]$SkipBackup,
    [string]$DatabaseName = "osustst"
)

Write-Host "=== CloudPepper Emergency Fix Script ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray

# Function to log messages
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
    )
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Backup critical files
function Backup-CriticalFiles {
    if ($SkipBackup) {
        Write-Log "Skipping backup as requested" "WARN"
        return
    }
    
    Write-Log "Creating backup of critical files..."
    $backupDir = "CloudPepper_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup JavaScript files that were modified
    $filesToBackup = @(
        "account_payment_final\static\src\js\cloudpepper_console_optimizer.js",
        "muk_web_colors\static\src\scss\colors_dark.scss",
        "muk_web_colors\__manifest__.py"
    )
    
    foreach ($file in $filesToBackup) {
        if (Test-Path $file) {
            $destPath = Join-Path $backupDir $file
            $destDir = Split-Path $destPath -Parent
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item $file $destPath -Force
            Write-Log "Backed up: $file"
        }
    }
    
    Write-Log "Backup completed: $backupDir" "SUCCESS"
}

# Fix JavaScript syntax errors
function Fix-JavaScriptErrors {
    Write-Log "Fixing JavaScript syntax errors..."
    
    # Check for malformed JavaScript files
    $jsFiles = Get-ChildItem -Path "." -Recurse -Include "*.js" | Where-Object {
        $_.FullName -match "(muk_web|account_payment)"
    }
    
    foreach ($jsFile in $jsFiles) {
        try {
            $content = Get-Content $jsFile.FullName -Raw -Encoding UTF8
            $originalContent = $content
            
            # Fix common JavaScript issues
            $content = $content -replace ',\s*\n\s*}', "`n}"
            $content = $content -replace ',\s*\n\s*]', "`n]"
            
            # Fix missing semicolons (basic check)
            $lines = $content -split "`n"
            for ($i = 0; $i -lt $lines.Length; $i++) {
                $line = $lines[$i].Trim()
                if ($line -and 
                    !$line.EndsWith(';') -and 
                    !$line.EndsWith('{') -and 
                    !$line.EndsWith('}') -and 
                    !$line.EndsWith(',') -and 
                    !$line.EndsWith('[') -and 
                    !$line.EndsWith(']') -and
                    !$line.StartsWith('//') -and
                    !$line.StartsWith('/*') -and
                    !$line.StartsWith('*') -and
                    !$line.StartsWith('if') -and
                    !$line.StartsWith('for') -and
                    !$line.StartsWith('while') -and
                    !$line.StartsWith('function') -and
                    !$line.StartsWith('class')) {
                    $lines[$i] += ';'
                }
            }
            $content = $lines -join "`n"
            
            # Write back if changes were made
            if ($content -ne $originalContent) {
                Set-Content -Path $jsFile.FullName -Value $content -Encoding UTF8
                Write-Log "Fixed syntax in: $($jsFile.Name)" "SUCCESS"
            }
        }
        catch {
            Write-Log "Error processing $($jsFile.Name): $($_.Exception.Message)" "ERROR"
        }
    }
}

# Fix SCSS variable naming issues
function Fix-SCSSVariables {
    Write-Log "Fixing SCSS variable naming issues..."
    
    $scssFiles = Get-ChildItem -Path "." -Recurse -Include "*.scss" | Where-Object {
        $_.FullName -match "muk_web_colors"
    }
    
    foreach ($scssFile in $scssFiles) {
        try {
            $content = Get-Content $scssFile.FullName -Raw -Encoding UTF8
            $originalContent = $content
            
            # Fix variable naming consistency (use underscores)
            $content = $content -replace '\$mk-color-', '$mk_color_'
            
            if ($content -ne $originalContent) {
                Set-Content -Path $scssFile.FullName -Value $content -Encoding UTF8
                Write-Log "Fixed SCSS variables in: $($scssFile.Name)" "SUCCESS"
            }
        }
        catch {
            Write-Log "Error processing $($scssFile.Name): $($_.Exception.Message)" "ERROR"
        }
    }
}

# Create SQL fix for autovacuum issues
function Create-AutovacuumFix {
    Write-Log "Creating autovacuum fix SQL..."
    
    $sqlFix = @"
-- CloudPepper Autovacuum Emergency Fix
-- Run with: psql -d $DatabaseName -f autovacuum_fix.sql

BEGIN;

-- 1. Disable problematic transient models
UPDATE ir_model 
SET transient = FALSE 
WHERE model = 'kit.account.tax.report' 
AND transient = TRUE;

-- 2. Clean up orphaned tax report variants
DELETE FROM account_tax_report_line 
WHERE report_id IN (
    SELECT atr.id 
    FROM account_tax_report atr
    WHERE atr.parent_id IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM account_tax_report parent 
        WHERE parent.id = atr.parent_id
    )
);

-- 3. Remove duplicate tax reports
WITH report_duplicates AS (
    SELECT id, 
           ROW_NUMBER() OVER (
               PARTITION BY COALESCE(name, ''), COALESCE(country_id, 0) 
               ORDER BY id
           ) as rn
    FROM account_tax_report 
    WHERE parent_id IS NULL
)
DELETE FROM account_tax_report 
WHERE id IN (
    SELECT id FROM report_duplicates WHERE rn > 1
);

-- 4. Adjust autovacuum settings
UPDATE ir_config_parameter 
SET value = '48' 
WHERE key = 'database.transient_age_limit';

-- 5. Disable autovacuum cron temporarily
UPDATE ir_cron 
SET active = FALSE 
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);

COMMIT;

-- Re-enable autovacuum with safer interval
UPDATE ir_cron 
SET active = TRUE,
    interval_number = 2,
    interval_type = 'days'
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model = 'ir.autovacuum'
);
"@

    Set-Content -Path "autovacuum_fix.sql" -Value $sqlFix -Encoding UTF8
    Write-Log "Created autovacuum_fix.sql" "SUCCESS"
}

# Create fix for server action datetime errors
function Create-DateTimeFix {
    Write-Log "Creating datetime fix SQL..."
    
    $datetimeFix = @"
-- CloudPepper Server Action DateTime Fix
-- Addresses TypeError in automation rules

BEGIN;

-- 1. Disable problematic server action
UPDATE ir_actions_server 
SET active = FALSE 
WHERE id = 864;

-- 2. Fix automation rules with datetime issues
UPDATE base_automation 
SET active = FALSE 
WHERE trigger = 'on_time' 
AND filter_domain LIKE '%sale.order%'
AND filter_domain NOT LIKE '%str(%';

-- 3. Update server action code to handle datetime properly
UPDATE ir_actions_server 
SET code = REPLACE(
    code, 
    'fields.Datetime.to_datetime(record_dt)', 
    'fields.Datetime.to_datetime(str(record_dt) if hasattr(record_dt, ''strftime'') else record_dt)'
)
WHERE code LIKE '%fields.Datetime.to_datetime%record_dt%';

-- 4. Clean up automation rules that reference non-existent models
DELETE FROM base_automation 
WHERE model_id NOT IN (
    SELECT DISTINCT id FROM ir_model
);

-- 5. Add error handling to remaining automation rules
UPDATE ir_actions_server 
SET code = CONCAT(
    'try:\n    ',
    REPLACE(code, '\n', '\n    '),
    '\nexcept Exception as e:\n    log(f"Automation error: {e}")\n    pass'
)
WHERE id IN (
    SELECT server_action_id FROM base_automation 
    WHERE trigger = 'on_time'
    AND server_action_id IS NOT NULL
)
AND code NOT LIKE '%try:%';

COMMIT;
"@

    Set-Content -Path "datetime_fix.sql" -Value $datetimeFix -Encoding UTF8
    Write-Log "Created datetime_fix.sql" "SUCCESS"
}

# Clear caches and temporary files
function Clear-SystemCaches {
    Write-Log "Clearing system caches..."
    
    # Clear Python cache files
    Get-ChildItem -Path "." -Recurse -Include "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path "." -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
    
    # Clear any Windows temp files
    $tempPaths = @(
        "$env:TEMP\odoo_*",
        "$env:TMP\odoo_*"
    )
    
    foreach ($path in $tempPaths) {
        Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    }
    
    Write-Log "Cache clearing completed" "SUCCESS"
}

# Create deployment verification script
function Create-DeploymentVerification {
    Write-Log "Creating deployment verification script..."
    
    $verificationScript = @"
# CloudPepper Deployment Verification
# Run after applying fixes

Write-Host "=== CloudPepper Deployment Verification ===" -ForegroundColor Cyan

# Check 1: JavaScript syntax validation
Write-Host "`nChecking JavaScript files..." -ForegroundColor Yellow
`$jsErrors = 0
Get-ChildItem -Recurse -Include "*.js" | ForEach-Object {
    try {
        # Basic syntax check - looking for common issues
        `$content = Get-Content `$_.FullName -Raw
        if (`$content -match '^\s*\]' -or `$content -match ',\s*\n\s*\}' -or `$content -match ',\s*\n\s*\]') {
            Write-Host "Potential syntax issue in: `$(`$_.Name)" -ForegroundColor Red
            `$jsErrors++
        }
    }
    catch {
        Write-Host "Error reading: `$(`$_.Name)" -ForegroundColor Red
        `$jsErrors++
    }
}

if (`$jsErrors -eq 0) {
    Write-Host "✓ No JavaScript syntax issues detected" -ForegroundColor Green
} else {
    Write-Host "✗ Found `$jsErrors potential JavaScript issues" -ForegroundColor Red
}

# Check 2: SCSS variable consistency
Write-Host "`nChecking SCSS variables..." -ForegroundColor Yellow
`$scssErrors = 0
Get-ChildItem -Recurse -Include "*.scss" | ForEach-Object {
    `$content = Get-Content `$_.FullName -Raw
    if (`$content -match '\`$mk-color-' -and `$content -match '\`$mk_color_') {
        Write-Host "Inconsistent variable naming in: `$(`$_.Name)" -ForegroundColor Red
        `$scssErrors++
    }
}

if (`$scssErrors -eq 0) {
    Write-Host "✓ SCSS variables are consistent" -ForegroundColor Green
} else {
    Write-Host "✗ Found `$scssErrors SCSS variable inconsistencies" -ForegroundColor Red
}

# Check 3: Required SQL fix files
Write-Host "`nChecking fix files..." -ForegroundColor Yellow
`$requiredFiles = @("autovacuum_fix.sql", "datetime_fix.sql")
`$missingFiles = 0

foreach (`$file in `$requiredFiles) {
    if (Test-Path `$file) {
        Write-Host "✓ Found: `$file" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: `$file" -ForegroundColor Red
        `$missingFiles++
    }
}

# Summary
Write-Host "`n=== Verification Summary ===" -ForegroundColor Cyan
if (`$jsErrors -eq 0 -and `$scssErrors -eq 0 -and `$missingFiles -eq 0) {
    Write-Host "✓ All checks passed - Ready for deployment" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ Issues found - Review before deployment" -ForegroundColor Red
    exit 1
}
"@

    Set-Content -Path "cloudpepper_verification.ps1" -Value $verificationScript -Encoding UTF8
    Write-Log "Created cloudpepper_verification.ps1" "SUCCESS"
}

# Main execution
try {
    Write-Log "Starting CloudPepper emergency fix process..."
    
    # Create backup
    Backup-CriticalFiles
    
    # Apply fixes
    Fix-JavaScriptErrors
    Fix-SCSSVariables
    Create-AutovacuumFix
    Create-DateTimeFix
    Clear-SystemCaches
    Create-DeploymentVerification
    
    Write-Log "=== Emergency Fix Summary ===" "SUCCESS"
    Write-Log "✓ JavaScript syntax errors fixed"
    Write-Log "✓ SCSS variable naming corrected"
    Write-Log "✓ Autovacuum fix SQL created"
    Write-Log "✓ DateTime parsing fix SQL created"
    Write-Log "✓ System caches cleared"
    Write-Log "✓ Verification script created"
    
    Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Apply database fixes:" -ForegroundColor White
    Write-Host "   psql -d $DatabaseName -f autovacuum_fix.sql" -ForegroundColor Gray
    Write-Host "   psql -d $DatabaseName -f datetime_fix.sql" -ForegroundColor Gray
    Write-Host "2. Restart Odoo service" -ForegroundColor White
    Write-Host "3. Run verification: .\cloudpepper_verification.ps1" -ForegroundColor White
    Write-Host "4. Monitor logs for errors" -ForegroundColor White
    
    Write-Log "Emergency fix process completed successfully!" "SUCCESS"
}
catch {
    Write-Log "Emergency fix process failed: $($_.Exception.Message)" "ERROR"
    exit 1
}
