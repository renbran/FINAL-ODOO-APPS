# ====================================================================
# Odoo 17 Database Migration PowerShell Script
# ====================================================================
# This script helps you run the database migration fix for NOT NULL constraint errors
# 
# REQUIREMENTS:
# - PostgreSQL client tools (psql) must be installed and in PATH
# - You need database connection credentials
# ====================================================================

param(
    [string]$DatabaseName = "",
    [string]$Username = "odoo",
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [switch]$Help
)

function Show-Help {
    Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Odoo 17 Database Migration Fix Helper                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

This script fixes NOT NULL constraint errors in Odoo 17:
- hr_employee.agent_id
- hr_employee.labour_card_number  
- hr_employee.salary_card_number
- res_bank.routing_code

USAGE:
    .\fix_database.ps1 -DatabaseName "your_db_name" -Username "your_user" -Host "localhost" -Port "5432"

PARAMETERS:
    -DatabaseName   Your Odoo database name (required)
    -Username       Database username (default: odoo)
    -Host           Database host (default: localhost)
    -Port           Database port (default: 5432)
    -Help           Show this help message

EXAMPLES:
    .\fix_database.ps1 -DatabaseName "odoo_17_prod"
    .\fix_database.ps1 -DatabaseName "odoo_17_prod" -Username "postgres" -Host "192.168.1.100"

MANUAL ALTERNATIVE:
If you prefer to run the SQL manually:
1. Open psql or pgAdmin
2. Connect to your database
3. Run the SQL script: database_migration_fix.sql

"@
}

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    # Check if psql is available
    try {
        $psqlVersion = psql --version 2>$null
        if ($psqlVersion) {
            Write-Host "✅ PostgreSQL client found: $($psqlVersion[0])" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ PostgreSQL client (psql) not found in PATH" -ForegroundColor Red
        Write-Host "Please install PostgreSQL client tools or add them to your PATH" -ForegroundColor Yellow
        return $false
    }
    
    return $false
}

function Test-DatabaseConnection {
    param([string]$dbname, [string]$user, [string]$host, [string]$port)
    
    Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
    
    try {
        $testQuery = "SELECT version();"
        $result = psql -h $host -p $port -U $user -d $dbname -t -c $testQuery 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database connection successful" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Database connection failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Database connection failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-DatabaseFix {
    param([string]$dbname, [string]$user, [string]$host, [string]$port)
    
    $sqlFile = Join-Path $PSScriptRoot "database_migration_fix.sql"
    
    if (-not (Test-Path $sqlFile)) {
        Write-Host "❌ SQL file not found: $sqlFile" -ForegroundColor Red
        Write-Host "Make sure database_migration_fix.sql is in the same directory as this script" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "🔧 Running database migration fix..." -ForegroundColor Yellow
    Write-Host "Database: $dbname" -ForegroundColor Cyan
    Write-Host "SQL File: $sqlFile" -ForegroundColor Cyan
    
    try {
        # Run the SQL script
        psql -h $host -p $port -U $user -d $dbname -f $sqlFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "🎉 Database migration completed successfully!" -ForegroundColor Green
            Write-Host "You can now start Odoo without NOT NULL constraint errors." -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Database migration failed with exit code: $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error running migration: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Show-PostMigrationInstructions {
    Write-Host @"

╔══════════════════════════════════════════════════════════════════════════════╗
║                            Post-Migration Instructions                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

✅ Database migration completed successfully!

NEXT STEPS:
1. Start your Odoo server normally
2. The NOT NULL constraint errors should be resolved
3. Monitor the Odoo logs for any remaining issues

WHAT WAS FIXED:
- hr_employee.agent_id: NULL values set to default bank
- hr_employee.labour_card_number: NULL values set to padded employee ID
- hr_employee.salary_card_number: NULL values set to padded employee ID  
- res_bank.routing_code: NULL values set to padded bank ID

TROUBLESHOOTING:
- If you still see errors, check the Odoo logs for specific details
- Ensure all custom modules are compatible with Odoo 17
- Consider updating modules to their latest versions

"@ -ForegroundColor Cyan
}

# Main script execution
if ($Help) {
    Show-Help
    exit 0
}

if (-not $DatabaseName) {
    Write-Host "❌ Database name is required!" -ForegroundColor Red
    Write-Host "Use -Help for usage information" -ForegroundColor Yellow
    exit 1
}

Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Odoo 17 Database Migration Fix                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

# Check prerequisites
if (-not (Test-Prerequisites)) {
    exit 1
}

# Test database connection
if (-not (Test-DatabaseConnection -dbname $DatabaseName -user $Username -host $Host -port $Port)) {
    Write-Host "Please check your database credentials and try again" -ForegroundColor Yellow
    exit 1
}

# Confirm before proceeding
Write-Host "`n⚠️  IMPORTANT: This will modify your database!" -ForegroundColor Yellow
Write-Host "Database: $DatabaseName" -ForegroundColor Cyan
$confirm = Read-Host "Do you want to proceed? (y/N)"

if ($confirm -ne "y" -and $confirm -ne "Y" -and $confirm -ne "yes") {
    Write-Host "❌ Operation cancelled by user" -ForegroundColor Yellow
    exit 0
}

# Run the migration
if (Invoke-DatabaseFix -dbname $DatabaseName -user $Username -host $Host -port $Port) {
    Show-PostMigrationInstructions
} else {
    Write-Host "`n❌ Migration failed. Please check the error messages above." -ForegroundColor Red
    exit 1
}
