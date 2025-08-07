#!/usr/bin/env python3
"""
FINAL CLEANUP: Fix duplicate key constraint for payment_account_enhanced
This targets the specific ir_model_data constraint violation
"""

def create_constraint_fix_sql():
    """Create SQL to fix the specific constraint violation"""
    
    sql_commands = """
-- FINAL FIX for duplicate key constraint on payment_account_enhanced
-- Target: Key (module, name)=(base, module_payment_account_enhanced) already exists

-- 1. Find the problematic record
SELECT * FROM ir_model_data 
WHERE module = 'base' AND name = 'module_payment_account_enhanced';

-- 2. Delete the duplicate record causing constraint violation
DELETE FROM ir_model_data 
WHERE module = 'base' AND name = 'module_payment_account_enhanced';

-- 3. Also remove any other variations
DELETE FROM ir_model_data 
WHERE name = 'module_payment_account_enhanced';

-- 4. Remove any remaining payment_account_enhanced entries
DELETE FROM ir_model_data 
WHERE module = 'payment_account_enhanced';

-- 5. Clean up ir_module_module table entries
DELETE FROM ir_module_module 
WHERE name = 'payment_account_enhanced';

-- 6. Verify cleanup
SELECT 'Constraint violation fixed' as status;
SELECT COUNT(*) as remaining_base_records 
FROM ir_model_data 
WHERE module = 'base' AND name LIKE '%payment_account_enhanced%';

SELECT COUNT(*) as remaining_module_records 
FROM ir_model_data 
WHERE module = 'payment_account_enhanced';
"""
    
    with open('fix_constraint_violation.sql', 'w', encoding='utf-8') as f:
        f.write(sql_commands)
    
    print("✅ Created fix_constraint_violation.sql")

def create_python_constraint_fix():
    """Create Python script to fix constraint in Odoo shell"""
    
    python_script = """
# Fix duplicate key constraint for payment_account_enhanced
# Run in Odoo shell: python odoo-bin shell -d your_database

print("🔍 Searching for problematic ir_model_data records...")

# Find the specific problematic record
problematic_records = env['ir.model.data'].search([
    ('module', '=', 'base'),
    ('name', '=', 'module_payment_account_enhanced')
])

if problematic_records:
    print(f"Found {len(problematic_records)} problematic records in 'base' module")
    for record in problematic_records:
        print(f"   - ID: {record.id}, Module: {record.module}, Name: {record.name}")
        record.unlink()
    print("✅ Deleted problematic 'base' module records")
else:
    print("ℹ️ No problematic records found in 'base' module")

# Clean up any remaining payment_account_enhanced records
all_payment_records = env['ir.model.data'].search([
    '|',
    ('module', '=', 'payment_account_enhanced'),
    ('name', 'like', '%payment_account_enhanced%')
])

if all_payment_records:
    print(f"Found {len(all_payment_records)} additional payment_account_enhanced records")
    all_payment_records.unlink()
    print("✅ Deleted all payment_account_enhanced records")

# Remove from module registry
payment_modules = env['ir.module.module'].search([
    ('name', '=', 'payment_account_enhanced')
])

if payment_modules:
    print(f"Found {len(payment_modules)} module registry entries")
    payment_modules.unlink()
    print("✅ Deleted module registry entries")

# Commit changes
env.cr.commit()

print("🎉 CONSTRAINT VIOLATION FIXED!")
print("📋 Now try installing the module again")
"""
    
    with open('fix_constraint_violation.py', 'w', encoding='utf-8') as f:
        f.write(python_script)
    
    print("✅ Created fix_constraint_violation.py")

def main():
    print("🔧 Creating targeted fix for duplicate key constraint...")
    
    create_constraint_fix_sql()
    create_python_constraint_fix()
    
    print("\n🎯 CONSTRAINT VIOLATION FIX READY!")
    print("\n📋 IMMEDIATE ACTION REQUIRED:")
    print("   The error shows: Key (module, name)=(base, module_payment_account_enhanced) already exists")
    print("   This means there's a leftover record in ir_model_data that's blocking installation")
    print("\n🔧 CHOOSE ONE METHOD:")
    print("\n   METHOD A: Direct SQL (Fastest)")
    print("   1. Connect to PostgreSQL: psql -U odoo -d your_database")
    print("   2. Run: \\i fix_constraint_violation.sql")
    print("   3. Restart Odoo service")
    print("   4. Try installing module again")
    print("\n   METHOD B: Odoo Shell (Safer)")
    print("   1. Stop Odoo service")
    print("   2. Run: python odoo-bin shell -d your_database")
    print("   3. Copy and paste contents of fix_constraint_violation.py")
    print("   4. Restart Odoo service")
    print("   5. Try installing module again")
    print("\n✅ After running either method, the constraint violation will be resolved!")

if __name__ == "__main__":
    main()
