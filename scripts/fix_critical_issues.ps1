# Critical Fixes Script - Fix HIGH PRIORITY issues
# Generated: December 3, 2025

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CRITICAL FIXES SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @(
    @{
        Module = "rental_management"
        Issue = "Wrong version format (3.5.0 instead of 17.0.3.5.0)"
        Priority = "CRITICAL"
        File = "rental_management\__manifest__.py"
        Fix = "Change version to 17.0.3.5.0"
    },
    @{
        Module = "account_payment_approval"
        Issue = "1 Python syntax error"
        Priority = "HIGH"
        File = "Check Python files in module"
        Fix = "Run Python syntax validator"
    },
    @{
        Module = "commission_ax"
        Issue = "1 Python syntax error"
        Priority = "HIGH"
        File = "Check Python files in module"
        Fix = "Run Python syntax validator"
    },
    @{
        Module = "webhook_crm"
        Issue = "3 Python syntax errors"
        Priority = "HIGH"
        File = "Check Python files in module"
        Fix = "Run Python syntax validator"
    },
    @{
        Module = "order_status_override"
        Issue = "3 XML parsing errors"
        Priority = "HIGH"
        File = "Check XML files in views/"
        Fix = "Validate XML syntax"
    },
    @{
        Module = "comprehensive_greetings"
        Issue = "7 XML parsing errors"
        Priority = "HIGH"
        File = "Check XML files in views/"
        Fix = "Validate XML syntax"
    },
    @{
        Module = "payment_approval_pro"
        Issue = "1 XML parsing error"
        Priority = "MEDIUM"
        File = "Check XML files in views/"
        Fix = "Validate XML syntax"
    },
    @{
        Module = "frontend_enhancement"
        Issue = "2 deprecated attrs in XML"
        Priority = "MEDIUM"
        File = "Check views/*.xml"
        Fix = "Replace attrs={{}} with modern syntax"
    },
    @{
        Module = "partner_statement_followup"
        Issue = "5 deprecated attrs in XML"
        Priority = "MEDIUM"
        File = "Check views/*.xml"
        Fix = "Replace attrs={{}} with modern syntax"
    }
)

Write-Host "Found $($issues.Count) critical issues to fix" -ForegroundColor Yellow
Write-Host ""

# Group by priority
$criticalIssues = $issues | Where-Object { $_.Priority -eq "CRITICAL" }
$highIssues = $issues | Where-Object { $_.Priority -eq "HIGH" }
$mediumIssues = $issues | Where-Object { $_.Priority -eq "MEDIUM" }

# Display CRITICAL issues
Write-Host "========================================" -ForegroundColor Red
Write-Host "CRITICAL ISSUES ($($criticalIssues.Count))" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
foreach ($issue in $criticalIssues) {
    Write-Host ""
    Write-Host "Module: $($issue.Module)" -ForegroundColor Yellow
    Write-Host "  Issue: $($issue.Issue)" -ForegroundColor White
    Write-Host "  File: $($issue.File)" -ForegroundColor Gray
    Write-Host "  Fix: $($issue.Fix)" -ForegroundColor Green
}

# Display HIGH priority issues
Write-Host ""
Write-Host "========================================" -ForegroundColor DarkRed
Write-Host "HIGH PRIORITY ISSUES ($($highIssues.Count))" -ForegroundColor DarkRed
Write-Host "========================================" -ForegroundColor DarkRed
foreach ($issue in $highIssues) {
    Write-Host ""
    Write-Host "Module: $($issue.Module)" -ForegroundColor Yellow
    Write-Host "  Issue: $($issue.Issue)" -ForegroundColor White
    Write-Host "  File: $($issue.File)" -ForegroundColor Gray
    Write-Host "  Fix: $($issue.Fix)" -ForegroundColor Green
}

# Display MEDIUM priority issues
Write-Host ""
Write-Host "========================================" -ForegroundColor DarkYellow
Write-Host "MEDIUM PRIORITY ISSUES ($($mediumIssues.Count))" -ForegroundColor DarkYellow
Write-Host "========================================" -ForegroundColor DarkYellow
foreach ($issue in $mediumIssues) {
    Write-Host ""
    Write-Host "Module: $($issue.Module)" -ForegroundColor Yellow
    Write-Host "  Issue: $($issue.Issue)" -ForegroundColor White
    Write-Host "  File: $($issue.File)" -ForegroundColor Gray
    Write-Host "  Fix: $($issue.Fix)" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FIX #1: rental_management Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "rental_management\__manifest__.py") {
    Write-Host "Fixing rental_management version..." -NoNewline
    
    $manifestPath = "rental_management\__manifest__.py"
    $content = Get-Content $manifestPath -Raw
    
    # Check current version
    if ($content -match "'version':\s*'3\.5\.0'") {
        $content = $content -replace "'version':\s*'3\.5\.0'", "'version': '17.0.3.5.0'"
        Set-Content -Path $manifestPath -Value $content -NoNewline
        Write-Host " ✓ Fixed!" -ForegroundColor Green
        Write-Host "  Changed: 'version': '3.5.0'" -ForegroundColor Red
        Write-Host "  To:      'version': '17.0.3.5.0'" -ForegroundColor Green
    }
    else {
        Write-Host " Already correct or different format" -ForegroundColor Yellow
    }
}
else {
    Write-Host "rental_management/__manifest__.py not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Run Python syntax validators on modules with syntax errors:" -ForegroundColor Yellow
Write-Host "   - account_payment_approval" -ForegroundColor White
Write-Host "   - commission_ax" -ForegroundColor White
Write-Host "   - webhook_crm" -ForegroundColor White
Write-Host ""
Write-Host "2. Validate and fix XML files in:" -ForegroundColor Yellow
Write-Host "   - order_status_override with 3 errors" -ForegroundColor White
Write-Host "   - comprehensive_greetings with 7 errors" -ForegroundColor White
Write-Host "   - payment_approval_pro with 1 error" -ForegroundColor White
Write-Host ""
Write-Host "3. Update deprecated attrs syntax in:" -ForegroundColor Yellow
Write-Host "   - frontend_enhancement with 2 occurrences" -ForegroundColor White
Write-Host "   - partner_statement_followup with 5 occurrences" -ForegroundColor White
Write-Host ""
Write-Host "Commands to run validators:" -ForegroundColor Cyan
Write-Host '  python -m py_compile module_name\*.py' -ForegroundColor Gray
Write-Host '  python -m xml.etree.ElementTree module_name\*.xml' -ForegroundColor Gray
Write-Host ""
