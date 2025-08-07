
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
