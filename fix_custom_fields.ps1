# Custom Fields Cleanup PowerShell Script for Odoo 17
# This script runs the SQL cleanup to fix '_unknown' object errors

param(
    [Parameter(Mandatory=$true)]
    [string]$DatabaseName,
    
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [string]$Host = "localhost",
    [int]$Port = 5432,
    [string]$Password
)

Write-Host "=====================================" -ForegroundColor Green
Write-Host "Custom Fields Cleanup for Odoo 17" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Get password if not provided
if (-not $Password) {
    $SecurePassword = Read-Host "Enter PostgreSQL password for user '$Username'" -AsSecureString
    $Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword))
}

# Set PostgreSQL password environment variable
$env:PGPASSWORD = $Password

Write-Host "Connecting to database: $DatabaseName" -ForegroundColor Yellow
Write-Host "Host: $Host" -ForegroundColor Yellow
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Yellow
Write-Host ""

# Check if psql is available
try {
    $null = Get-Command psql -ErrorAction Stop
    Write-Host "✓ PostgreSQL client (psql) found" -ForegroundColor Green
} catch {
    Write-Host "✗ PostgreSQL client (psql) not found in PATH" -ForegroundColor Red
    Write-Host "Please install PostgreSQL client tools or add them to your PATH" -ForegroundColor Red
    exit 1
}

# Test connection
Write-Host "Testing database connection..." -ForegroundColor Yellow
try {
    $testResult = & psql -h $Host -p $Port -U $Username -d $DatabaseName -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database connection successful" -ForegroundColor Green
    } else {
        Write-Host "✗ Database connection failed" -ForegroundColor Red
        Write-Host "Error: $testResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Database connection failed" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running custom fields cleanup..." -ForegroundColor Yellow

# Run the cleanup SQL script
$sqlScriptPath = Join-Path $PSScriptRoot "custom_fields_cleanup.sql"

if (-not (Test-Path $sqlScriptPath)) {
    Write-Host "✗ SQL script not found: $sqlScriptPath" -ForegroundColor Red
    exit 1
}

try {
    $result = & psql -h $Host -p $Port -U $Username -d $DatabaseName -f $sqlScriptPath 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Custom fields cleanup completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Output:" -ForegroundColor Cyan
        Write-Host $result -ForegroundColor White
    } else {
        Write-Host "✗ Custom fields cleanup failed" -ForegroundColor Red
        Write-Host "Error: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Error running cleanup script" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} finally {
    # Clear the password environment variable
    $env:PGPASSWORD = $null
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Cleanup Summary" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "The following fixes have been applied:" -ForegroundColor Yellow
Write-Host "• Fixed orphaned sale_order_type_id references" -ForegroundColor White
Write-Host "• Fixed orphaned project/project_id references" -ForegroundColor White
Write-Host "• Fixed orphaned unit/unit_id references" -ForegroundColor White
Write-Host "• Fixed orphaned buyer/buyer_id references" -ForegroundColor White
Write-Host "• Cleaned up duplicate field definitions" -ForegroundColor White
Write-Host "• Cleaned up orphaned ir_model_data entries" -ForegroundColor White
Write-Host "• Updated database statistics" -ForegroundColor White
Write-Host ""
Write-Host "You can now restart Odoo. The '_unknown' object error should be resolved." -ForegroundColor Green
Write-Host ""

# Pause to allow user to read the output
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
