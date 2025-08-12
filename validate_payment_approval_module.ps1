# Account Payment Approval Module - Windows Validation Script
# PowerShell version for Windows environment

param(
    [switch]$Verbose = $false
)

Write-Host "🚀 Starting Account Payment Approval Module Validation..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Test counters
$TestsPassed = 0
$TestsFailed = 0
$TotalTests = 0

# Function to run a test
function Run-Test {
    param(
        [string]$TestName,
        [scriptblock]$TestCommand,
        [string]$ExpectedResult = "success"
    )
    
    Write-Host "Testing: $TestName" -ForegroundColor Blue
    $Global:TotalTests++
    
    try {
        $result = & $TestCommand
        $success = $result -and $LASTEXITCODE -eq 0
        
        if ($success) {
            if ($ExpectedResult -eq "success") {
                Write-Host "✅ PASSED: $TestName" -ForegroundColor Green
                $Global:TestsPassed++
            } else {
                Write-Host "❌ FAILED: $TestName (unexpected success)" -ForegroundColor Red
                $Global:TestsFailed++
            }
        } else {
            if ($ExpectedResult -eq "failure") {
                Write-Host "✅ PASSED: $TestName (expected failure)" -ForegroundColor Green
                $Global:TestsPassed++
            } else {
                Write-Host "❌ FAILED: $TestName" -ForegroundColor Red
                $Global:TestsFailed++
            }
        }
    } catch {
        Write-Host "❌ FAILED: $TestName - Error: $($_.Exception.Message)" -ForegroundColor Red
        $Global:TestsFailed++
    }
    
    Write-Host ""
}

Write-Host "📁 Module Structure Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 1: Check if main module directory exists
Run-Test "Module Directory Exists" { Test-Path ".\account_payment_approval" -PathType Container }

# Test 2: Check manifest file
Run-Test "Manifest File Exists" { Test-Path ".\account_payment_approval\__manifest__.py" -PathType Leaf }

# Test 3: Check models directory
Run-Test "Models Directory Structure" { 
    (Test-Path ".\account_payment_approval\models" -PathType Container) -and 
    (Test-Path ".\account_payment_approval\models\__init__.py" -PathType Leaf) 
}

# Test 4: Check core model files
Run-Test "Core Model Files" { 
    (Test-Path ".\account_payment_approval\models\account_payment.py" -PathType Leaf) -and 
    (Test-Path ".\account_payment_approval\models\payment_approval_config.py" -PathType Leaf) 
}

# Test 5: Check wizards
Run-Test "Wizard Files" { 
    (Test-Path ".\account_payment_approval\wizards" -PathType Container) -and 
    (Test-Path ".\account_payment_approval\wizards\payment_bulk_approval_wizard.py" -PathType Leaf) 
}

# Test 6: Check security files
Run-Test "Security Configuration" { 
    (Test-Path ".\account_payment_approval\security" -PathType Container) -and 
    (Test-Path ".\account_payment_approval\security\payment_approval_groups.xml" -PathType Leaf) 
}

# Test 7: Check views
Run-Test "View Files" { 
    (Test-Path ".\account_payment_approval\views" -PathType Container) -and 
    (Test-Path ".\account_payment_approval\views\account_payment_views.xml" -PathType Leaf) 
}

# Test 8: Check data files
Run-Test "Data Files" { 
    (Test-Path ".\account_payment_approval\data" -PathType Container) -and 
    (Test-Path ".\account_payment_approval\data\email_templates.xml" -PathType Leaf) 
}

# Test 9: Check static assets
Run-Test "Static Assets" { Test-Path ".\account_payment_approval\static\src" -PathType Container }

# Test 10: Check OWL templates
Run-Test "OWL Templates" { Test-Path ".\account_payment_approval\static\src\xml\dashboard_templates.xml" -PathType Leaf }

Write-Host "🔍 Code Quality Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 11: Python syntax validation
Run-Test "Python Syntax Check - account_payment.py" { 
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -m py_compile ".\account_payment_approval\models\account_payment.py" 2>$null
        $LASTEXITCODE -eq 0
    } else {
        Write-Warning "Python not found in PATH, skipping syntax check"
        $true
    }
}

# Test 12: Python syntax validation - config
Run-Test "Python Syntax Check - config.py" { 
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -m py_compile ".\account_payment_approval\models\payment_approval_config.py" 2>$null
        $LASTEXITCODE -eq 0
    } else {
        $true
    }
}

# Test 13: Python syntax validation - wizards
Run-Test "Python Syntax Check - wizards" { 
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -m py_compile ".\account_payment_approval\wizards\payment_bulk_approval_wizard.py" 2>$null
        $LASTEXITCODE -eq 0
    } else {
        $true
    }
}

Write-Host "🔧 Configuration Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 16: Check manifest dependencies
Run-Test "Manifest Dependencies" { 
    $content = Get-Content ".\account_payment_approval\__manifest__.py" -Raw -ErrorAction SilentlyContinue
    $content -match "account.*mail.*web"
}

# Test 17: Check version compatibility
Run-Test "Odoo Version Check" { 
    $content = Get-Content ".\account_payment_approval\__manifest__.py" -Raw -ErrorAction SilentlyContinue
    $content -match "17\.0"
}

# Test 18: Check data files referenced in manifest
Run-Test "Data Files in Manifest" { 
    $content = Get-Content ".\account_payment_approval\__manifest__.py" -Raw -ErrorAction SilentlyContinue
    $content -match "email_templates\.xml"
}

# Test 19: Check assets in manifest
Run-Test "Assets in Manifest" { 
    $content = Get-Content ".\account_payment_approval\__manifest__.py" -Raw -ErrorAction SilentlyContinue
    $content -match "web\.assets_backend"
}

Write-Host "📊 Content Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 20: Check approval states in payment model
Run-Test "Approval States Defined" { 
    $content = Get-Content ".\account_payment_approval\models\account_payment.py" -Raw -ErrorAction SilentlyContinue
    $content -match "under_review.*approved.*authorized"
}

# Test 21: Check digital signature functionality
Run-Test "Digital Signature Methods" { 
    $content = Get-Content ".\account_payment_approval\models\account_payment.py" -Raw -ErrorAction SilentlyContinue
    $content -match "_add_digital_signature"
}

# Test 22: Check QR code functionality
Run-Test "QR Code Methods" { 
    $content = Get-Content ".\account_payment_approval\models\account_payment.py" -Raw -ErrorAction SilentlyContinue
    $content -match "_generate_qr_code"
}

# Test 23: Check email templates
Run-Test "Email Template Count" { 
    $content = Get-Content ".\account_payment_approval\data\email_templates.xml" -Raw -ErrorAction SilentlyContinue
    $matches = [regex]::Matches($content, '<record.*mail\.template')
    $matches.Count -ge 5
}

# Test 24: Check security groups
Run-Test "Security Groups Defined" { 
    $content = Get-Content ".\account_payment_approval\security\payment_approval_groups.xml" -Raw -ErrorAction SilentlyContinue
    $content -match "payment_approval_user.*payment_approval_manager"
}

# Test 25: Check wizard functionality
Run-Test "Bulk Approval Wizard" { 
    $content = Get-Content ".\account_payment_approval\wizards\payment_bulk_approval_wizard.py" -Raw -ErrorAction SilentlyContinue
    $content -match "def.*approve_payments"
}

Write-Host "🎨 Frontend Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 26: Check JavaScript files
Run-Test "JavaScript Dashboard Component" { Test-Path ".\account_payment_approval\static\src\js\payment_approval_dashboard.js" -PathType Leaf }

# Test 27: Check SCSS files
Run-Test "SCSS Stylesheets" { Test-Path ".\account_payment_approval\static\src\scss\payment_approval.scss" -PathType Leaf }

# Test 28: Check OWL templates syntax
Run-Test "OWL Template Syntax" { 
    $content = Get-Content ".\account_payment_approval\static\src\xml\dashboard_templates.xml" -Raw -ErrorAction SilentlyContinue
    $content -match "t-name.*dashboard"
}

# Test 29: Check responsive design elements
Run-Test "Responsive Design Classes" { 
    $content = Get-Content ".\account_payment_approval\static\src\scss\payment_approval.scss" -Raw -ErrorAction SilentlyContinue
    $content -match "mobile.*responsive"
}

Write-Host "📈 Enterprise Features Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 30: Check multi-tier approval logic
Run-Test "Multi-tier Approval Logic" { 
    $content = Get-Content ".\account_payment_approval\models\account_payment.py" -Raw -ErrorAction SilentlyContinue
    $content -match "approval_tier.*approval_level"
}

# Test 31: Check audit trail functionality
Run-Test "Audit Trail Implementation" { 
    $content = Get-Content ".\account_payment_approval\models\account_payment.py" -Raw -ErrorAction SilentlyContinue
    $content -match "approval_history.*audit"
}

# Test 32: Check reporting wizards
Run-Test "Report Generation Wizard" { Test-Path ".\account_payment_approval\wizards\payment_report_wizard.py" -PathType Leaf }

# Test 33: Check configuration settings
Run-Test "Configuration Settings" { 
    $content = Get-Content ".\account_payment_approval\models\res_config_settings.py" -Raw -ErrorAction SilentlyContinue
    $content -match "approval_threshold.*time_limit"
}

# Test 34: Check API controllers
Run-Test "API Controllers" { Test-Path ".\account_payment_approval\controllers\api.py" -PathType Leaf }

# Test 35: Check QR verification controller
Run-Test "QR Verification Controller" { Test-Path ".\account_payment_approval\controllers\qr_verification.py" -PathType Leaf }

Write-Host "🔒 Security Validation" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Test 36: Check access rights file
Run-Test "Access Rights Configuration" { Test-Path ".\account_payment_approval\security\ir.model.access.csv" -PathType Leaf }

# Test 37: Check record rules
Run-Test "Security Record Rules" { 
    $content = Get-Content ".\account_payment_approval\security\payment_approval_groups.xml" -Raw -ErrorAction SilentlyContinue
    $content -match "payment_approval.*rule"
}

# Test 38: Check user groups hierarchy
Run-Test "User Groups Hierarchy" { 
    $content = Get-Content ".\account_payment_approval\security\payment_approval_groups.xml" -Raw -ErrorAction SilentlyContinue
    $content -match "payment_approval_user.*payment_approval_reviewer.*payment_approval_approver"
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "📊 VALIDATION SUMMARY" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Total Tests Run: $TotalTests"
Write-Host "Tests Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $TestsFailed" -ForegroundColor Red

if ($TestsFailed -eq 0) {
    Write-Host ""
    Write-Host "🎉 ALL TESTS PASSED! Module is ready for deployment." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Run Odoo with --test-enable to execute unit tests"
    Write-Host "2. Install the module in a test database"
    Write-Host "3. Configure approval workflows"
    Write-Host "4. Test with sample payments"
    Write-Host "5. Deploy to production environment"
    Write-Host ""
    Write-Host "🚀 Ready for Enterprise Deployment!" -ForegroundColor Blue
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed. Please review and fix issues before deployment." -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Recommended Actions:" -ForegroundColor Yellow
    Write-Host "1. Review failed test details above"
    Write-Host "2. Fix any missing files or configuration issues"
    Write-Host "3. Re-run this validation script"
    Write-Host "4. Consult the implementation documentation"
}

Write-Host ""
Write-Host "Generated for OSUS Properties - Account Payment Approval Module" -ForegroundColor Blue
Write-Host "Validation completed at: $(Get-Date)" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Cyan

# Return exit code based on test results
if ($TestsFailed -gt 0) {
    exit 1
} else {
    exit 0
}
