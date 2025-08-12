# Simple Account Payment Approval Module Validation
Write-Host "🚀 Account Payment Approval Module Validation" -ForegroundColor Cyan
Write-Host "=============================================="

$TestsPassed = 0
$TestsFailed = 0

function Test-Component {
    param($Name, $Path)
    
    Write-Host "Testing: $Name" -ForegroundColor Blue
    if (Test-Path $Path) {
        Write-Host "✅ PASSED: $Name" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ FAILED: $Name" -ForegroundColor Red  
        return $false
    }
}

Write-Host "`n📁 Module Structure" -ForegroundColor Yellow
if (Test-Component "Module Directory" ".\account_payment_approval") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Manifest File" ".\account_payment_approval\__manifest__.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Models Directory" ".\account_payment_approval\models") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Core Payment Model" ".\account_payment_approval\models\account_payment.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Configuration Model" ".\account_payment_approval\models\payment_approval_config.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Settings Model" ".\account_payment_approval\models\res_config_settings.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n🧙‍♂️ Wizards" -ForegroundColor Yellow
if (Test-Component "Wizards Directory" ".\account_payment_approval\wizards") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Bulk Approval Wizard" ".\account_payment_approval\wizards\payment_bulk_approval_wizard.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Rejection Wizard" ".\account_payment_approval\wizards\payment_rejection_wizard.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Report Wizard" ".\account_payment_approval\wizards\payment_report_wizard.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n🔒 Security" -ForegroundColor Yellow
if (Test-Component "Security Directory" ".\account_payment_approval\security") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "User Groups" ".\account_payment_approval\security\payment_approval_groups.xml") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Access Rights" ".\account_payment_approval\security\ir.model.access.csv") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n👁️ Views" -ForegroundColor Yellow
if (Test-Component "Views Directory" ".\account_payment_approval\views") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Payment Views" ".\account_payment_approval\views\account_payment_views.xml") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Menu Views" ".\account_payment_approval\views\menu_views.xml") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n📧 Email Templates" -ForegroundColor Yellow
if (Test-Component "Data Directory" ".\account_payment_approval\data") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Email Templates" ".\account_payment_approval\data\email_templates.xml") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n🎨 Frontend Assets" -ForegroundColor Yellow
if (Test-Component "Static Assets" ".\account_payment_approval\static\src") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "JavaScript Files" ".\account_payment_approval\static\src\js") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "SCSS Files" ".\account_payment_approval\static\src\scss") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "OWL Templates" ".\account_payment_approval\static\src\xml") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n🌐 Controllers" -ForegroundColor Yellow
if (Test-Component "Controllers Directory" ".\account_payment_approval\controllers") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "Main Controller" ".\account_payment_approval\controllers\main.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }
if (Test-Component "API Controller" ".\account_payment_approval\controllers\api.py") { $script:TestsPassed++ } else { $script:TestsFailed++ }

Write-Host "`n=============================================="
Write-Host "📊 VALIDATION SUMMARY" -ForegroundColor Blue
Write-Host "=============================================="
Write-Host "Tests Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $TestsFailed" -ForegroundColor Red
Write-Host "Total Tests: $($TestsPassed + $TestsFailed)"

if ($TestsFailed -eq 0) {
    Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "✅ Module structure is complete and ready for deployment" -ForegroundColor Green
    Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Test module installation in Odoo"
    Write-Host "2. Configure approval workflows" 
    Write-Host "3. Test payment approval process"
    Write-Host "4. Deploy to production"
} else {
    Write-Host "`n❌ Some components are missing" -ForegroundColor Red
    Write-Host "Please create the missing files before deployment" -ForegroundColor Yellow
}

Write-Host "`nValidation completed: $(Get-Date)" -ForegroundColor Blue
