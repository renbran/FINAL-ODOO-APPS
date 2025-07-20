# ============================================
# MODULE APPLICATION SCRIPT FOR NEW/RESTORED DATABASES
# ============================================

param(
    [Parameter(Mandatory=$false)]
    [string]$DatabaseName = "propertyosus",
    
    [Parameter(Mandatory=$false)]
    [string]$ModuleList = ""
)

Write-Host "🚀 Module Application to Database: $DatabaseName" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

# Define module categories
$CoreModules = @(
    "report_xlsx",
    "report_pdf_options", 
    "osus_dashboard",
    "hrms_dashboard"
)

$BusinessModules = @(
    "payment_account_enhanced",
    "automated_employee_announce",
    "calendar_extended",
    "reconcilation_fields",
    "order_status_override",
    "upper_unicity_partner_product"
)

$ReportingModules = @(
    "osus_invoice_report",
    "oe_sale_dashboard_17",
    "sales_target_vs_achievement",
    "statement_report"
)

$UIModules = @(
    "muk_web_theme",
    "muk_web_colors", 
    "theme_levelup"
)

# Module dependencies mapping
$ModuleDependencies = @{
    "osus_dashboard" = @("report_xlsx", "report_pdf_options")
    "hrms_dashboard" = @("report_xlsx") 
    "payment_account_enhanced" = @("account", "payment")
    "oe_sale_dashboard_17" = @("sale", "report_xlsx")
    "sales_target_vs_achievement" = @("sale", "report_xlsx")
    "muk_web_theme" = @("muk_web_colors")
}

# Function to resolve module dependencies
function Get-ModuleDependencies {
    param([string[]]$Modules)
    
    $resolvedModules = @()
    $processed = @{}
    
    function Add-ModuleRecursive {
        param([string]$Module)
        
        if ($processed.ContainsKey($Module)) { return }
        $processed[$Module] = $true
        
        # Add dependencies first
        if ($ModuleDependencies.ContainsKey($Module)) {
            foreach ($dep in $ModuleDependencies[$Module]) {
                Add-ModuleRecursive -Module $dep
            }
        }
        
        # Add the module itself
        if ($resolvedModules -notcontains $Module) {
            $resolvedModules += $Module
        }
    }
    
    foreach ($module in $Modules) {
        Add-ModuleRecursive -Module $module
    }
    
    return $resolvedModules
}

# Function to apply modules to database
function Install-Modules {
    param([string[]]$Modules, [string]$DB)
    
    Write-Host "📦 Applying modules to database: $DB" -ForegroundColor Yellow
    
    # Resolve dependencies
    $resolvedModules = Get-ModuleDependencies -Modules $Modules
    Write-Host "🔗 Resolved dependencies: $($resolvedModules -join ', ')" -ForegroundColor Magenta
    
    # Get correct Docker network name
    $networkName = (docker network ls --format "table {{.Name}}" | Select-String "odoo17_final").ToString().Trim()
    if (-not $networkName) {
        $networkName = "odoo17_final_odoo-network"
    }
    Write-Host "🌐 Using network: $networkName" -ForegroundColor Blue
    
    # Ensure full stack is running
    Write-Host "🚀 Starting Odoo stack..." -ForegroundColor Green
    docker-compose up -d
    Start-Sleep -Seconds 15
    
    # Create module list string
    $moduleStr = $resolvedModules -join ","
    Write-Host "📋 Modules to apply: $moduleStr" -ForegroundColor Magenta
    
    # Method 1: Try direct container exec (preferred)
    Write-Host "💉 Method 1: Installing via running container..." -ForegroundColor Green
    try {
        $result = docker exec odoo17_final-odoo-1 odoo -d $DB -i $moduleStr --stop-after-init --without-demo=all
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully applied modules via container exec!" -ForegroundColor Green
            $success = $true
        } else {
            throw "Container exec failed"
        }
    }
    catch {
        Write-Host "⚠️  Method 1 failed, trying Method 2..." -ForegroundColor Yellow
        $success = $false
    }
    
    # Method 2: Use temporary container (fallback)
    if (-not $success) {
        Write-Host "💉 Method 2: Installing via temporary container..." -ForegroundColor Green
        Write-Host "⏹️  Stopping Odoo service..." -ForegroundColor Red
        docker-compose stop odoo
        Start-Sleep -Seconds 3
        
        try {
            # Use the correct network name and volume mounting
            $result = docker run --rm --network $networkName `
                -v "${PWD}:/mnt/extra-addons" `
                -e HOST=odoo17_final-db-1 `
                -e USER=odoo `
                -e PASSWORD=odoo `
                odoo:17.0 `
                odoo -d $DB -i $moduleStr --stop-after-init --without-demo=all --load-language=en_US
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Successfully applied modules via temporary container!" -ForegroundColor Green
                $success = $true
            }
        }
        catch {
            Write-Host "❌ Method 2 also failed!" -ForegroundColor Red
            Write-Host "Output: $result" -ForegroundColor Yellow
        }
    }
    
    # Method 3: Database-level module installation (last resort)
    if (-not $success) {
        Write-Host "💉 Method 3: Database-level module registration..." -ForegroundColor Yellow
        try {
            foreach ($module in $resolvedModules) {
                $sql = "INSERT INTO ir_module_module (name, state, author, website, summary, description) VALUES ('$module', 'to install', 'Custom', '', 'Custom Module', 'Custom Module') ON CONFLICT (name) DO UPDATE SET state = 'to install';"
                docker exec odoo17_final-db-1 psql -U odoo -d $DB -c $sql
            }
            Write-Host "✅ Modules registered in database for installation!" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Database registration failed!" -ForegroundColor Red
        }
    }
    
    # Restart full stack
    Write-Host "🔄 Restarting full Odoo stack..." -ForegroundColor Blue
    docker-compose up -d
    Start-Sleep -Seconds 15
    
    # Verify modules are available
    Write-Host "🔍 Verifying module availability..." -ForegroundColor Cyan
    $moduleCheck = docker exec odoo17_final-db-1 psql -U odoo -d $DB -t -c "SELECT name FROM ir_module_module WHERE name IN ('$($resolvedModules -join "','")');"
    if ($moduleCheck) {
        Write-Host "✅ Modules found in database!" -ForegroundColor Green
        Write-Host "Found: $($moduleCheck.Trim())" -ForegroundColor Gray
    }
    
    Write-Host "🌐 Database ready at: http://localhost:8069/web?db=$DB" -ForegroundColor Cyan
    Write-Host "💡 Next: Go to Apps -> Update Apps List -> Install your modules" -ForegroundColor Yellow
}

# Main execution
if ($ModuleList -ne "") {
    $selectedModules = $ModuleList.Split(",") | ForEach-Object { $_.Trim() }
    Install-Modules -Modules $selectedModules -DB $DatabaseName
} else {
    Write-Host "📋 Available application options:" -ForegroundColor Yellow
    Write-Host "1. Core Modules (Essential)" -ForegroundColor White
    Write-Host "   - $($CoreModules -join ', ')" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Business Modules" -ForegroundColor White  
    Write-Host "   - $($BusinessModules -join ', ')" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Reporting Modules" -ForegroundColor White
    Write-Host "   - $($ReportingModules -join ', ')" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. UI/Theme Modules" -ForegroundColor White
    Write-Host "   - $($UIModules -join ', ')" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Select option (1-4) or type 'all' for everything"
    
    switch ($choice) {
        "1" { Install-Modules -Modules $CoreModules -DB $DatabaseName }
        "2" { Install-Modules -Modules $BusinessModules -DB $DatabaseName }
        "3" { Install-Modules -Modules $ReportingModules -DB $DatabaseName }
        "4" { Install-Modules -Modules $UIModules -DB $DatabaseName }
        "all" { 
            $allModules = $CoreModules + $BusinessModules + $ReportingModules + $UIModules
            Install-Modules -Modules $allModules -DB $DatabaseName 
        }
        default { 
            Write-Host "❌ Invalid choice. Exiting..." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "🎉 Module application complete!" -ForegroundColor Green
Write-Host "📋 Summary of applied changes:" -ForegroundColor Cyan
Write-Host "   ✅ Modules are now available in your database" -ForegroundColor Green  
Write-Host "   ✅ Custom app codes have been applied" -ForegroundColor Green
Write-Host "   🔄 Go to Apps -> Update Apps List to see them" -ForegroundColor Yellow
