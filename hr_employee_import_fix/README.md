# Employee Import Fix Module

This Odoo 17 module resolves foreign key constraint violations when importing employees, specifically addressing the common error:

```
Error at row X: insert or update on table hr_employee violates foreign key constraint "hr_employee_resource_id_fkey"
```

## Features

### 1. Automatic Resource Creation
- **Auto-creates missing `resource.resource` records** during employee creation
- **Handles invalid resource_id references** gracefully
- **Prevents foreign key constraint violations** during import

### 2. Safe Import Methods
- **Enhanced employee creation** with constraint handling
- **Bulk import utilities** for processing multiple employees
- **Error prevention and logging** for troubleshooting

### 3. UI Enhancements
- **Safe Import Wizard** in HR menu
- **Fix Orphaned Employees** utility
- **Enhanced employee form** showing resource information

## Installation

1. Copy the `hr_employee_import_fix` folder to your Odoo addons directory
2. Restart Odoo server
3. Go to Apps menu and install "Employee Import Fix"

## Usage

### Method 1: Use the Safe Import Wizard
1. Go to **HR → Import Employees (Safe)**
2. Upload your CSV/Excel file
3. Enable "Skip Errors" to continue with valid records
4. Click "Import Employees"

### Method 2: Fix Existing Issues
1. Go to **HR → Configuration → Fix Orphaned Employees**
2. Click to automatically fix employees with missing resource records

### Method 3: Programmatic Import
```python
# Use the safe bulk create method
employee_data = [
    {'name': 'John Doe', 'resource_id': 999},  # Even if 999 doesn't exist
    {'name': 'Jane Smith'},  # Without resource_id
]

results = self.env['hr.employee'].safe_bulk_create(employee_data)
```

## Technical Details

### Enhanced hr.employee Model
- **create() method override**: Handles missing resource records automatically
- **safe_bulk_create()**: Bulk import with error handling
- **fix_orphaned_employees()**: Repair existing invalid records
- **_clean_employee_data()**: Data validation and cleaning

### Error Handling
The module handles these common constraint violations:
- Missing `resource.resource` records
- Invalid `company_id` references
- Missing `department_id` records
- Invalid `job_id` references
- Missing `user_id` records

### Auto-Creation Logic
When a resource_id is provided but doesn't exist:
1. Create new `resource.resource` record with appropriate values
2. Link the employee to the new resource
3. Log the operation for audit trail

### Fallback Strategy
If resource creation fails:
1. Remove invalid `resource_id` from data
2. Let Odoo auto-create the resource record
3. Continue with employee creation

## Configuration

### Enable Debug Mode
To see resource_id field in employee form:
1. Enable Developer mode
2. Go to employee form
3. Resource ID field will be visible

### Log Monitoring
Check Odoo logs for:
- Resource creation messages
- Constraint violation warnings
- Import progress information

## Common Use Cases

### CSV Import Issues
**Before**: CSV imports fail with foreign key errors
**After**: Auto-creates missing resources and continues import

### Bulk Employee Creation
**Before**: Manual resource creation required
**After**: Automatic resource handling during creation

### Data Migration
**Before**: Complex data cleanup scripts needed
**After**: Built-in constraint handling and error recovery

## Troubleshooting

### Import Still Failing?
1. Check the error logs for specific constraint violations
2. Use the "Fix Orphaned Employees" utility
3. Ensure CSV data has valid format

### Performance Issues?
- The module processes employees individually for safety
- For very large imports (1000+ records), consider batch processing
- Monitor resource creation in database

### Custom Resource Fields?
- Extend the `_clean_employee_data()` method
- Add custom field validation logic
- Handle additional foreign key constraints

## Development

### Extending the Module
```python
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def _clean_employee_data(self, data):
        # Call parent method
        cleaned_data = super()._clean_employee_data(data)
        
        # Add custom cleaning logic
        # ...
        
        return cleaned_data
```

### Adding New Constraints
1. Identify the foreign key field
2. Add validation to `_clean_employee_data()`
3. Add auto-creation logic if needed

## Support

For issues or questions:
1. Check Odoo logs for detailed error messages
2. Use the built-in error reporting in safe import methods
3. Review the module's logging output

## Changelog

### Version 17.0.1.0.0
- Initial release
- Basic resource constraint handling
- Safe import wizard
- Orphaned employee repair utility
