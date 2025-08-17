# ODOO MANAGEMENT SCRIPT USAGE EXAMPLES

## Quick Start Guide

### Prerequisites Setup
Before using the scripts, ensure you have:

1. **Odoo Installation** - Properly installed Odoo instance
2. **Administrative Rights** - Run PowerShell as Administrator (Windows) or use sudo (Linux)
3. **Python Environment** - Working Python virtual environment for Odoo
4. **Database Access** - PostgreSQL database connectivity

### Usage Examples

#### Windows PowerShell Version
```powershell
# Run interactively
.\odoo_management_oldosus.ps1

# Command line usage
.\odoo_management_oldosus.ps1 status
.\odoo_management_oldosus.ps1 update-payments draft posted
.\odoo_management_oldosus.ps1 find-duplicates 85
.\odoo_management_oldosus.ps1 apply-precision 2
```

#### Linux Bash Version
```bash
# Make executable (first time only)
chmod +x odoo_management_oldosus.sh

# Run interactively
./odoo_management_oldosus.sh

# Command line usage
./odoo_management_oldosus.sh status
./odoo_management_oldosus.sh update-payments draft posted
./odoo_management_oldosus.sh find-duplicates 85
./odoo_management_oldosus.sh apply-precision 2
```

### Common Operations

#### 1. System Health Check
```powershell
# Check system status
.\odoo_management_oldosus.ps1 status
```
This displays:
- Installation paths verification
- Disk usage information
- Recent log activity
- Running Odoo processes

#### 2. Payment Management
```powershell
# Update all draft payments to posted
.\odoo_management_oldosus.ps1 update-payments draft posted

# Update pending payments to confirmed
.\odoo_management_oldosus.ps1 update-payments pending confirmed
```

#### 3. Data Quality Maintenance
```powershell
# Apply 2 decimal precision to all monetary fields
.\odoo_management_oldosus.ps1 apply-precision 2

# Find duplicate contacts with 80% similarity
.\odoo_management_oldosus.ps1 find-duplicates 80

# More aggressive duplicate detection (90% threshold)
.\odoo_management_oldosus.ps1 find-duplicates 90
```

#### 4. Module Management
```powershell
# Update all installed modules
.\odoo_management_oldosus.ps1 update-modules

# Install Python package in Odoo environment
.\odoo_management_oldosus.ps1 install-package requests
```

#### 5. Database Operations
```powershell
# Create database backup
.\odoo_management_oldosus.ps1 backup

# Open Odoo shell for manual operations
.\odoo_management_oldosus.ps1 shell
```

### Configuration Customization

#### Windows PowerShell Configuration
Edit the PowerShell script to match your installation:
```powershell
$ODOO_BASE = "C:\odoo\oldosus"  # Your Odoo installation path
$PYTHON_INTERPRETER = Join-Path $ODOO_BASE "venv\Scripts\python.exe"
```

#### Linux Bash Configuration
Edit the Bash script to match your installation:
```bash
ODOO_BASE="/var/odoo/oldosus"  # Your Odoo installation path
PYTHON_INTERPRETER="$ODOO_BASE/venv/bin/python3"
```

### Safety Features

#### Automated Backups
```powershell
# Always backup before major operations
.\odoo_management_oldosus.ps1 backup

# Then perform operations
.\odoo_management_oldosus.ps1 update-payments draft posted
```

#### Error Handling
- All database operations include transaction rollback on errors
- Path validation before execution
- Permission checks before starting operations
- Comprehensive error logging

### Automation Examples

#### Scheduled Tasks (Windows)
```powershell
# Create scheduled task for weekly duplicate detection
schtasks /create /tn "Odoo Duplicate Check" /tr "PowerShell.exe -File 'C:\path\to\odoo_management_oldosus.ps1' find-duplicates 85" /sc weekly /d MON /st 02:00
```

#### Cron Jobs (Linux)
```bash
# Add to crontab for weekly duplicate detection
0 2 * * 1 /path/to/odoo_management_oldosus.sh find-duplicates 85

# Daily backup
0 1 * * * /path/to/odoo_management_oldosus.sh backup
```

### Troubleshooting

#### Common Issues
1. **Permission Denied**
   - Windows: Run PowerShell as Administrator
   - Linux: Use sudo or add user to appropriate groups

2. **Path Not Found**
   - Verify Odoo installation paths in script configuration
   - Check Python virtual environment path

3. **Database Connection Issues**
   - Verify PostgreSQL service is running
   - Check Odoo configuration file
   - Ensure database user has proper permissions

#### Log Analysis
```powershell
# View recent logs for troubleshooting
.\odoo_management_oldosus.ps1 7  # Interactive mode option 7
```

### Best Practices

1. **Always test on development first**
2. **Create backups before major operations**
3. **Run system status checks regularly**
4. **Monitor log files for errors**
5. **Keep scripts updated with your environment changes**

### Support Information

For issues or questions:
- Check the documentation: ODOO_MANAGEMENT_OLDOSUS_DOCUMENTATION.md
- Review log files for error details
- Verify system requirements and paths
- Test operations on development environment first
