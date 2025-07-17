#!/usr/bin/env python3
"""
HR Employee Import Fix Script

This script helps resolve foreign key constraint violations when importing employees
by providing several solutions for the resource_resource constraint issue.
"""

import csv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmployeeImportFixer:
    """
    Helper class to fix employee import issues related to resource_resource constraints
    """
    
    def __init__(self):
        self.missing_resource_ids = []
        self.fixed_records = []
    
    def analyze_csv_file(self, csv_file_path):
        """
        Analyze the CSV file to identify potential issues
        """
        logger.info(f"Analyzing CSV file: {csv_file_path}")
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Check for resource_id column
                if 'resource_id' in reader.fieldnames:
                    logger.warning("Found 'resource_id' column in CSV - this may cause constraint violations")
                    return "resource_id_found"
                
                # Check for other potential issues
                logger.info("CSV structure looks good - no resource_id column found")
                return "clean"
                
        except Exception as e:
            logger.error(f"Error analyzing CSV: {str(e)}")
            return "error"
    
    def create_clean_csv(self, input_file, output_file):
        """
        Create a clean CSV file without resource_id references
        """
        logger.info(f"Creating clean CSV from {input_file} to {output_file}")
        
        try:
            with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                
                # Remove resource_id and other problematic fields
                clean_fieldnames = [field for field in reader.fieldnames 
                                  if field not in ['resource_id', 'id', 'resource_calendar_id']]
                
                with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=clean_fieldnames)
                    writer.writeheader()
                    
                    for row in reader:
                        # Create clean row without problematic fields
                        clean_row = {field: row.get(field, '') for field in clean_fieldnames}
                        writer.writerow(clean_row)
            
            logger.info(f"Clean CSV created successfully: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating clean CSV: {str(e)}")
            return False

def print_solution_menu():
    """
    Print available solutions for the user
    """
    print("\n" + "="*60)
    print("HR EMPLOYEE IMPORT FIX SOLUTIONS")
    print("="*60)
    print()
    print("Choose a solution based on your situation:")
    print()
    print("1. CLEAN CSV APPROACH (Recommended)")
    print("   - Remove resource_id from your CSV file")
    print("   - Let Odoo auto-generate resource records")
    print()
    print("2. DATABASE CONSTRAINT APPROACH")
    print("   - Temporarily disable constraints")
    print("   - Import data")
    print("   - Re-enable constraints")
    print()
    print("3. ODOO CONFIGURATION APPROACH")
    print("   - Use Odoo's built-in import features")
    print("   - Handle missing references gracefully")
    print()
    print("4. MANUAL RESOURCE CREATION")
    print("   - Create missing resource records first")
    print("   - Then import employees")
    print()

def solution_1_clean_csv():
    """
    Solution 1: Clean CSV approach
    """
    print("\n" + "-"*50)
    print("SOLUTION 1: CLEAN CSV APPROACH")
    print("-"*50)
    print()
    print("Steps to fix your CSV file:")
    print()
    print("1. Open your employee CSV file")
    print("2. Remove these columns if present:")
    print("   - resource_id")
    print("   - id")
    print("   - resource_calendar_id (unless you're sure it exists)")
    print()
    print("3. Required columns for basic employee import:")
    print("   - name (required)")
    print("   - work_email")
    print("   - work_phone")
    print("   - department_id (use department name)")
    print("   - job_id (use job title name)")
    print("   - manager_id (use manager's employee number)")
    print()
    print("4. Example clean CSV structure:")
    print("   name,work_email,department_id,job_id")
    print("   'John Doe',john.doe@company.com,'Sales','Sales Manager'")
    print()
    print("5. Import using Odoo interface:")
    print("   - Go to Employees menu")
    print("   - Click Import")
    print("   - Upload your clean CSV")
    print("   - Map fields properly")
    print("   - Test import with a few records first")

def solution_2_database_approach():
    """
    Solution 2: Database approach
    """
    print("\n" + "-"*50)
    print("SOLUTION 2: DATABASE CONSTRAINT APPROACH")
    print("-"*50)
    print()
    print("⚠️  WARNING: This approach requires database admin access")
    print("⚠️  Make a backup before proceeding!")
    print()
    print("SQL commands to run (in order):")
    print()
    print("-- 1. Temporarily disable the constraint")
    print("ALTER TABLE hr_employee DROP CONSTRAINT IF EXISTS hr_employee_resource_id_fkey;")
    print()
    print("-- 2. Import your data")
    print("-- (Use Odoo interface or direct SQL)")
    print()
    print("-- 3. Create missing resource records")
    print("""INSERT INTO resource_resource (name, resource_type, company_id, active, create_date, write_date, create_uid, write_uid)
SELECT 
    emp.name,
    'user',
    1, -- Default company_id, adjust as needed
    true,
    NOW(),
    NOW(),
    1, -- Admin user
    1  -- Admin user
FROM hr_employee emp 
WHERE emp.resource_id NOT IN (SELECT id FROM resource_resource)
ON CONFLICT DO NOTHING;""")
    print()
    print("-- 4. Update employee records with correct resource_ids")
    print("""UPDATE hr_employee emp 
SET resource_id = res.id 
FROM resource_resource res 
WHERE emp.name = res.name 
AND emp.resource_id IS NULL;""")
    print()
    print("-- 5. Re-enable the constraint")
    print("""ALTER TABLE hr_employee 
ADD CONSTRAINT hr_employee_resource_id_fkey 
FOREIGN KEY (resource_id) 
REFERENCES resource_resource(id) 
ON DELETE SET NULL;""")

def solution_3_odoo_approach():
    """
    Solution 3: Odoo configuration approach
    """
    print("\n" + "-"*50)
    print("SOLUTION 3: ODOO CONFIGURATION APPROACH")
    print("-"*50)
    print()
    print("Create a custom import method in Odoo:")
    print()
    print("1. Create a server action or custom module")
    print("2. Override the employee creation process")
    print("3. Auto-generate missing resources")
    print()
    print("Python code to add to your custom module:")
    print()
    print("""
@api.model
def create(self, vals):
    # If no resource_id is provided, create one
    if 'resource_id' not in vals or not vals.get('resource_id'):
        resource_vals = {
            'name': vals.get('name', 'New Employee'),
            'resource_type': 'user',
            'company_id': vals.get('company_id') or self.env.company.id,
        }
        resource = self.env['resource.resource'].create(resource_vals)
        vals['resource_id'] = resource.id
    
    return super(HrEmployee, self).create(vals)
""")

def solution_4_manual_approach():
    """
    Solution 4: Manual resource creation
    """
    print("\n" + "-"*50)
    print("SOLUTION 4: MANUAL RESOURCE CREATION")
    print("-"*50)
    print()
    print("If you must keep resource_id in your CSV:")
    print()
    print("1. First, create resource records:")
    print()
    print("CSV for resource_resource table:")
    print("id,name,resource_type,company_id,active")
    print("2697,'Employee Name','user',1,True")
    print()
    print("2. Import resource records first")
    print("3. Then import employee records")
    print()
    print("Or use SQL to create missing resources:")
    print()
    print("""INSERT INTO resource_resource (id, name, resource_type, company_id, active, create_date, write_date, create_uid, write_uid)
VALUES (2697, 'Missing Resource', 'user', 1, true, NOW(), NOW(), 1, 1)
ON CONFLICT (id) DO NOTHING;""")

def main():
    """
    Main function to run the employee import fixer
    """
    print_solution_menu()
    
    while True:
        print("\n" + "="*60)
        choice = input("Enter solution number (1-4) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("Goodbye!")
            break
        elif choice == '1':
            solution_1_clean_csv()
        elif choice == '2':
            solution_2_database_approach()
        elif choice == '3':
            solution_3_odoo_approach()
        elif choice == '4':
            solution_4_manual_approach()
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 'q'")

if __name__ == "__main__":
    main()
