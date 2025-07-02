"""
Simple Custom Fields Cleanup for Odoo Shell
Save this as cleanup_simple.py and run with:

python3 odoo-bin shell -d your_database_name --no-http -c /path/to/odoo.conf

Then in the shell:
exec(open('cleanup_simple.py').read())
"""

print("=== Starting Custom Fields Cleanup ===")

# Get database cursor
cr = env.cr

try:
    # 1. Fix sale_order_type_id references
    print("1. Fixing sale_order_type_id references...")
    cr.execute("""
        UPDATE account_move 
        SET sale_order_type_id = NULL 
        WHERE sale_order_type_id IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM sale_order_type 
            WHERE id = account_move.sale_order_type_id
        );
    """)
    print(f"   Fixed {cr.rowcount} orphaned sale_order_type_id references")

    # 2. Fix project references
    print("2. Fixing project references...")
    cr.execute("""
        UPDATE account_move 
        SET project = NULL 
        WHERE project IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM product_template 
            WHERE id = account_move.project
        );
    """)
    print(f"   Fixed {cr.rowcount} orphaned project references")

    # 3. Fix unit references
    print("3. Fixing unit references...")
    cr.execute("""
        UPDATE account_move 
        SET unit = NULL 
        WHERE unit IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM product_product 
            WHERE id = account_move.unit
        );
    """)
    print(f"   Fixed {cr.rowcount} orphaned unit references")

    # 4. Fix buyer references
    print("4. Fixing buyer references...")
    cr.execute("""
        UPDATE account_move 
        SET buyer = NULL 
        WHERE buyer IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM res_partner 
            WHERE id = account_move.buyer
        );
    """)
    print(f"   Fixed {cr.rowcount} orphaned buyer references")

    # 5. Fix alternative field names if they exist
    alt_fields = [
        ('project_id', 'product_template'),
        ('unit_id', 'product_product'),
        ('buyer_id', 'res_partner')
    ]

    for field_name, ref_table in alt_fields:
        print(f"5. Fixing {field_name} references...")
        try:
            cr.execute(f"""
                UPDATE account_move 
                SET {field_name} = NULL 
                WHERE {field_name} IS NOT NULL 
                AND NOT EXISTS (
                    SELECT 1 FROM {ref_table} 
                    WHERE id = account_move.{field_name}
                );
            """)
            print(f"   Fixed {cr.rowcount} orphaned {field_name} references")
        except Exception as e:
            print(f"   Column {field_name} doesn't exist or error: {e}")

    # 6. Remove duplicate field definitions
    print("6. Removing duplicate field definitions...")
    field_names = ['sale_order_type_id', 'project', 'unit', 'buyer', 'project_id', 'unit_id', 'buyer_id']
    total_removed = 0

    for field_name in field_names:
        duplicates = env['ir.model.fields'].search([
            ('model', '=', 'account.move'),
            ('name', '=', field_name)
        ])
        if len(duplicates) > 1:
            fields_to_remove = duplicates[1:]
            print(f"   Removing {len(fields_to_remove)} duplicate definitions for {field_name}")
            fields_to_remove.unlink()
            total_removed += len(fields_to_remove)

    print(f"   Removed {total_removed} duplicate field definitions")

    # Commit changes
    cr.commit()
    
    print("\n✅ Cleanup completed successfully!")
    print("You can now restart Odoo. The '_unknown' object error should be resolved.")

except Exception as e:
    print(f"\n❌ Error during cleanup: {e}")
    cr.rollback()
    raise
