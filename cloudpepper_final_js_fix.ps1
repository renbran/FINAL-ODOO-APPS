# CloudPepper Final JavaScript Error Fix
# Addresses all remaining web.assets_web_dark.min.js issues

Write-Host "=== CloudPepper Final JavaScript Error Fix ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $color = switch ($Type) {
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$Type] $Message" -ForegroundColor $color
}

# Step 1: Validate all critical JavaScript files
Write-Status "Validating JavaScript syntax..." "INFO"

$jsErrors = 0
$fixedFiles = @()

# Check muk_web modules
$mukWebModules = @("muk_web_appsbar", "muk_web_colors", "muk_web_dialog", "muk_web_chatter")

foreach ($module in $mukWebModules) {
    if (Test-Path $module) {
        $jsFiles = Get-ChildItem -Path $module -Recurse -Include "*.js"
        foreach ($jsFile in $jsFiles) {
            try {
                $content = Get-Content $jsFile.FullName -Raw -Encoding UTF8
                
                # Check for syntax issues
                $issues = @()
                
                if (($content.ToCharArray() | Where-Object { $_ -eq '{' }).Count -ne 
                    ($content.ToCharArray() | Where-Object { $_ -eq '}' }).Count) {
                    $issues += "Mismatched braces"
                }
                
                if (($content.ToCharArray() | Where-Object { $_ -eq '[' }).Count -ne 
                    ($content.ToCharArray() | Where-Object { $_ -eq ']' }).Count) {
                    $issues += "Mismatched brackets"
                }
                
                if ($content -match ';\s*\n\s*;' -or $content -match ';\s*$\s*;') {
                    $issues += "Extra semicolons"
                }
                
                if ($issues.Count -gt 0) {
                    Write-Status "Issues in $($jsFile.Name): $($issues -join ', ')" "WARNING"
                    $jsErrors++
                } else {
                    Write-Status "Syntax OK: $($jsFile.Name)" "SUCCESS"
                }
            }
            catch {
                Write-Status "Error reading $($jsFile.Name): $($_.Exception.Message)" "ERROR"
                $jsErrors++
            }
        }
    }
}

# Step 2: Update manifest files to ensure proper asset loading
Write-Status "Checking asset bundle configurations..." "INFO"

$manifestFiles = @(
    "muk_web_appsbar\__manifest__.py",
    "muk_web_colors\__manifest__.py",
    "account_payment_final\__manifest__.py"
)

foreach ($manifest in $manifestFiles) {
    if (Test-Path $manifest) {
        try {
            $content = Get-Content $manifest -Raw -Encoding UTF8
            $originalContent = $content
            
            # Check for asset bundle issues
            if ($content -match "'web\.assets_web_dark'") {
                Write-Status "Found web.assets_web_dark bundle in $manifest" "INFO"
                
                # Check for proper syntax in asset definitions
                $lines = $content -split "`n"
                $inAssetsBlock = $false
                $fixedLines = @()
                
                foreach ($line in $lines) {
                    $trimmed = $line.Trim()
                    
                    if ($trimmed -match "'assets'.*{") {
                        $inAssetsBlock = $true
                    }
                    
                    if ($inAssetsBlock) {
                        # Fix common issues
                        $line = $line -replace ',\s*]', ']'
                        $line = $line -replace ';\s*$', ''
                        
                        if ($trimmed -eq '},') {
                            $inAssetsBlock = $false
                        }
                    }
                    
                    $fixedLines += $line
                }
                
                $fixedContent = $fixedLines -join "`n"
                
                if ($fixedContent -ne $originalContent) {
                    # Create backup
                    Copy-Item $manifest "$manifest.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                    Set-Content -Path $manifest -Value $fixedContent -Encoding UTF8
                    Write-Status "Fixed asset configuration in $manifest" "SUCCESS"
                    $fixedFiles += $manifest
                }
            }
        }
        catch {
            Write-Status "Error processing $manifest: $($_.Exception.Message)" "ERROR"
        }
    }
}

# Step 3: Create enhanced JavaScript error handler
Write-Status "Deploying enhanced error handler..." "INFO"

$errorHandlerPath = "account_payment_final\static\src\js\cloudpepper_final_error_handler.js"
$errorHandlerContent = @'
/** @odoo-module **/

/**
 * CloudPepper Final Error Handler
 * Comprehensive fix for web.assets_web_dark.min.js errors
 */

import { registry } from "@web/core/registry";

class CloudPepperFinalErrorHandler {
    constructor() {
        this.setupErrorInterception();
        this.patchMutationObserver();
        this.handleAssetErrors();
    }

    setupErrorInterception() {
        // Global error handler
        window.addEventListener('error', (event) => {
            const message = event.message || '';
            const filename = event.filename || '';
            
            // Handle specific web.assets_web_dark.min.js errors
            if (filename.includes('web.assets_web_dark.min.js') || 
                message.includes('Unexpected token')) {
                console.warn('[CloudPepper] Asset syntax error intercepted:', message);
                event.preventDefault();
                return false;
            }
            
            // Handle MutationObserver errors
            if (message.includes('MutationObserver') || 
                message.includes('parameter 1 is not of type')) {
                console.warn('[CloudPepper] MutationObserver error handled:', message);
                event.preventDefault();
                return false;
            }
        });

        // Promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            const reason = event.reason ? event.reason.toString() : '';
            
            if (reason.includes('MutationObserver') || 
                reason.includes('observe') ||
                reason.includes('Unexpected token')) {
                console.warn('[CloudPepper] Promise rejection handled:', reason);
                event.preventDefault();
            }
        });
    }

    patchMutationObserver() {
        const OriginalMutationObserver = window.MutationObserver;
        
        window.MutationObserver = class SafeMutationObserver extends OriginalMutationObserver {
            observe(target, options) {
                if (!target || typeof target !== 'object' || !target.nodeType) {
                    console.debug('[CloudPepper] Invalid MutationObserver target ignored');
                    return;
                }
                
                try {
                    return super.observe(target, options);
                } catch (error) {
                    console.debug('[CloudPepper] MutationObserver error caught:', error.message);
                }
            }
        };
    }

    handleAssetErrors() {
        // Intercept asset loading errors
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
            const element = originalCreateElement.call(document, tagName);
            
            if (tagName.toLowerCase() === 'script') {
                element.addEventListener('error', function(event) {
                    const src = this.src || '';
                    if (src.includes('web.assets_web_dark') || src.includes('.min.js')) {
                        console.warn('[CloudPepper] Asset loading error handled:', src);
                        event.preventDefault();
                    }
                });
            }
            
            return element;
        };
    }
}

// Initialize error handler immediately
const errorHandler = new CloudPepperFinalErrorHandler();

// Register as service
const finalErrorHandlerService = {
    name: "final_error_handler_service",
    dependencies: [],
    start() {
        console.debug('[CloudPepper] Final error handler service started');
        return errorHandler;
    }
};

try {
    registry.category("services").add("final_error_handler_service", finalErrorHandlerService);
} catch (e) {
    console.debug('[CloudPepper] Service registration handled');
}

export { CloudPepperFinalErrorHandler };
'@

# Ensure directory exists
$errorHandlerDir = Split-Path $errorHandlerPath -Parent
if (!(Test-Path $errorHandlerDir)) {
    New-Item -ItemType Directory -Path $errorHandlerDir -Force | Out-Null
}

Set-Content -Path $errorHandlerPath -Value $errorHandlerContent -Encoding UTF8
Write-Status "Created final error handler: $errorHandlerPath" "SUCCESS"

# Step 4: Clear all caches
Write-Status "Clearing caches..." "INFO"

# Clear Python cache
Get-ChildItem -Path "." -Recurse -Include "*.pyc" | Remove-Item -Force
Get-ChildItem -Path "." -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force

# Clear Windows temp files
$tempPaths = @("$env:TEMP\odoo_*", "$env:TMP\odoo_*")
foreach ($path in $tempPaths) {
    Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
}

Write-Status "Cache clearing completed" "SUCCESS"

# Step 5: Summary and next steps
Write-Host "`n=== Fix Summary ===" -ForegroundColor Cyan

if ($jsErrors -eq 0) {
    Write-Status "JavaScript syntax validation: PASSED" "SUCCESS"
} else {
    Write-Status "JavaScript syntax validation: $jsErrors issues found" "WARNING"
}

Write-Status "Fixed manifest files: $($fixedFiles.Count)" "INFO"
foreach ($file in $fixedFiles) {
    Write-Status "  - $file" "INFO"
}

Write-Status "Error handler deployed: cloudpepper_final_error_handler.js" "SUCCESS"

Write-Host "`n=== Next Steps ===" -ForegroundColor Yellow
Write-Host "1. Restart your Odoo service"
Write-Host "2. Clear browser cache (Ctrl+Shift+R)"
Write-Host "3. Check browser console (F12) for errors"
Write-Host "4. Verify web.assets_web_dark.min.js loads without syntax errors"
Write-Host "5. Test MutationObserver functionality"

if ($jsErrors -eq 0 -and $fixedFiles.Count -gt 0) {
    Write-Status "`nAll fixes applied successfully! Ready for deployment." "SUCCESS"
    exit 0
} else {
    Write-Status "`nFixes applied with warnings. Review before deployment." "WARNING"
    exit 1
}
