"""
Migration script to add missing commission_id column to account_move table
Run this on CloudPepper to fix the database schema
"""

import psycopg2
import sys

def add_commission_id_column():
    """Add commission_id column to account_move if it doesn't exist"""
    
    # Database connection parameters (update these for your environment)
    db_config = {
        'dbname': 'odoo',  # Change to your database name
        'user': 'odoo',
        'password': '',  # Add password if needed
        'host': 'localhost',
        'port': 5432
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='account_move' 
            AND column_name='commission_id';
        """)
        
        if cur.fetchone():
            print("✅ Column 'commission_id' already exists in account_move table")
        else:
            print("⚠️  Column 'commission_id' does not exist. Adding now...")
            
            # Add the column
            cur.execute("""
                ALTER TABLE account_move 
                ADD COLUMN commission_id INTEGER;
            """)
            
            # Add foreign key constraint
            cur.execute("""
                ALTER TABLE account_move 
                ADD CONSTRAINT account_move_commission_id_fkey 
                FOREIGN KEY (commission_id) 
                REFERENCES commission_ax(id) 
                ON DELETE SET NULL;
            """)
            
            # Create index for better performance
            cur.execute("""
                CREATE INDEX account_move_commission_id_index 
                ON account_move(commission_id);
            """)
            
            conn.commit()
            print("✅ Successfully added commission_id column to account_move table")
            print("✅ Added foreign key constraint")
            print("✅ Created index")
        
        # Close connection
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("="*70)
    print("Commission AX Database Migration")
    print("Adding commission_id column to account_move table")
    print("="*70)
    print()
    
    success = add_commission_id_column()
    
    print()
    print("="*70)
    if success:
        print("✅ Migration completed successfully")
        print()
        print("Next steps:")
        print("1. Restart Odoo service: sudo systemctl restart odoo")
        print("2. Test in browser: Navigate to Accounting → Vendor Bills")
        print("3. The RPC error should be resolved")
    else:
        print("❌ Migration failed")
        print("Please check the error messages above")
    print("="*70)
    
    sys.exit(0 if success else 1)
