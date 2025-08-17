# ODOO MANAGEMENT SCRIPT - OLDOSUS INSTANCE
## Documentation & Usage Guide

### Overview
This comprehensive Bash script provides administrative tools for managing the OLDOSUS Odoo instance. It includes database maintenance, contact management, payment processing, and system administration features.

### Features

#### 🔧 **Core Administration Functions**
1. **Payment Status Management** - Bulk update payment statuses from draft to posted
2. **Decimal Precision Enforcement** - Apply proper 2-decimal formatting to monetary fields
3. **Duplicate Contact Detection** - Find and report duplicate contacts using fuzzy matching
4. **Odoo Shell Access** - Direct access to Odoo Python shell
5. **Module Management** - Update all installed modules
6. **Package Installation** - Install Python packages in Odoo virtual environment
7. **Log Viewing** - Browse and view Odoo log files
8. **Database Backup** - Create PostgreSQL database backups
9. **System Status** - Display comprehensive system health information

#### 🎨 **User Interface Features**
- Colorized output with status indicators (INFO, WARNING, ERROR)
- Interactive menu system for ease of use
- Command-line interface for automation
- Progress indicators and confirmation prompts
- Comprehensive error handling

### Installation & Setup

#### Prerequisites
- Linux/Unix system with Bash
- Sudo privileges
- Odoo 17 installation at `/var/odoo/oldosus`
- PostgreSQL database
- Python 3 with pip

#### Configuration
The script uses these default paths (modify at the top of the script):
```bash
ODOO_BASE="/var/odoo/oldosus"
ODOO_SRC="$ODOO_BASE/src"
ODOO_LOGS="$ODOO_BASE/logs"
ODOO_CONFIG="$ODOO_BASE/odoo.conf"
PYTHON_INTERPRETER="$ODOO_BASE/venv/bin/python3"
ODOO_USER="odoo"
```

#### Make Script Executable
```bash
chmod +x odoo_management_oldosus.sh
```

### Usage Methods

#### Interactive Mode (Recommended for Manual Operations)
```bash
./odoo_management_oldosus.sh
```
This launches an interactive menu where you can select operations and enter parameters.

#### Command Line Mode (For Automation)
```bash
# Update payment statuses
./odoo_management_oldosus.sh update-payments draft posted

# Apply decimal precision
./odoo_management_oldosus.sh apply-precision 2

# Find duplicate contacts (80% similarity)
./odoo_management_oldosus.sh find-duplicates 80

# Open Odoo shell
./odoo_management_oldosus.sh shell

# Update all modules
./odoo_management_oldosus.sh update-modules

# Install Python package
./odoo_management_oldosus.sh install-package requests

# Backup database
./odoo_management_oldosus.sh backup

# Show system status
./odoo_management_oldosus.sh status
```

### Detailed Function Documentation

#### 1. Update Payment Status
**Purpose**: Bulk update payment records from one status to another
**Database Impact**: Modifies `account.payment` records
**Usage**: 
- Interactive: Select option 1, enter statuses
- CLI: `./script.sh update-payments [from_status] [to_status]`
**Example**: Change all draft payments to posted
**Safety**: Includes transaction rollback on errors

#### 2. Apply Decimal Precision
**Purpose**: Enforce consistent decimal formatting on monetary fields
**Database Impact**: Modifies `account.move.line` records (debit, credit, amount_currency, price_unit)
**Usage**:
- Interactive: Select option 2, enter precision (default: 2)
- CLI: `./script.sh apply-precision [decimal_places]`
**Safety**: Updates in batches with commit/rollback handling

#### 3. Find Duplicate Contacts
**Purpose**: Identify potential duplicate contacts using fuzzy string matching
**Algorithm**: Compares name, email, and phone using SequenceMatcher
**Output**: Console report + CSV file (`/tmp/odoo_duplicates.csv`)
**Usage**:
- Interactive: Select option 3, enter threshold (default: 80%)
- CLI: `./script.sh find-duplicates [threshold]`
**Safety**: Read-only operation, generates reports for manual review

#### 4. System Status Display
**Information Provided**:
- Configuration paths and their validity
- Disk usage for Odoo directory
- Recent log file activity
- Running Odoo processes
- System health indicators

### Safety Features

#### 🛡️ **Data Protection**
- **Transaction Management**: All database operations use commit/rollback
- **Backup Recommendations**: Script can create database backups before major changes
- **Validation Checks**: Path verification before operations
- **Error Handling**: Comprehensive exception catching and reporting

#### 🔒 **Security Features**
- **Permission Verification**: Checks for sudo privileges
- **User Isolation**: Runs Odoo commands as designated user
- **Temp File Management**: Cleans up temporary files after operations
- **Input Validation**: Sanitizes user inputs

### Troubleshooting

#### Common Issues

**1. Permission Denied**
```bash
# Solution: Ensure script is executable and user has sudo access
chmod +x odoo_management_oldosus.sh
sudo usermod -aG sudo $USER
```

**2. Path Not Found Errors**
```bash
# Solution: Verify Odoo installation paths
ls -la /var/odoo/oldosus/
# Update script configuration variables if needed
```

**3. Database Connection Issues**
```bash
# Solution: Check Odoo configuration and PostgreSQL status
sudo systemctl status postgresql
sudo -u odoo psql -l
```

**4. Python Environment Issues**
```bash
# Solution: Verify virtual environment
sudo -u odoo /var/odoo/oldosus/venv/bin/python3 --version
```

#### Log Analysis
The script provides log viewing capabilities. Common log locations:
- Error logs: Look for `ERROR` entries
- Performance issues: Look for `WARN` entries about slow queries
- Module issues: Look for `ModuleNotFoundError` or `ImportError`

### Best Practices

#### 🎯 **Operational Best Practices**
1. **Always backup before major operations**
2. **Test operations on development instance first**
3. **Run during maintenance windows for database modifications**
4. **Monitor system resources during batch operations**
5. **Review duplicate reports manually before merging contacts**

#### 📊 **Maintenance Schedule Recommendations**
- **Daily**: Check system status and recent logs
- **Weekly**: Run duplicate contact detection
- **Monthly**: Apply decimal precision cleanup
- **As needed**: Payment status updates, module updates

#### 🔄 **Integration with Automation**
```bash
# Example cron job for weekly duplicate detection
0 2 * * 1 /path/to/odoo_management_oldosus.sh find-duplicates 85

# Example backup before maintenance
0 1 * * * /path/to/odoo_management_oldosus.sh backup
```

### Advanced Usage

#### Custom Modifications
The script is designed to be easily customizable:
1. **Add new functions**: Follow the existing pattern with print_header, error handling, and cleanup
2. **Modify thresholds**: Adjust default values in the configuration section
3. **Extend reporting**: Add new output formats or destinations
4. **Integration**: Call from other scripts or monitoring systems

#### Performance Considerations
- **Large datasets**: Consider batch processing for operations on many records
- **Resource usage**: Monitor CPU and memory during intensive operations
- **Database locks**: Be aware of potential lock conflicts during business hours

### Support & Maintenance

#### Script Versioning
Track changes and maintain documentation for:
- Configuration modifications
- Function additions or changes
- Bug fixes and improvements
- Compatibility updates

#### Monitoring Script Health
- Test script functions regularly
- Monitor log outputs for errors
- Verify backup integrity
- Update documentation as needed

---

**Created**: August 2025
**Compatibility**: Odoo 17, PostgreSQL, Linux/Unix
**License**: Internal Use - OSUS Properties
**Maintainer**: System Administrator
