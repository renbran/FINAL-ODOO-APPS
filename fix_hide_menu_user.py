#!/usr/bin/env python3
"""
Script to fix the hide_menu_user module field issue
"""

import psycopg2

def fix_hide_menu_user_db():
    """Fix the database to ensure the restrict_user_ids field is properly handled"""
    
    # Database connection parameters
    conn_params = {
        'host': 'localhost',
        'port': '5432',
        'database': 'osusre',
        'user': 'odoo',
        'password': 'odoo'
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if the field exists in ir_model_fields
        cursor.execute("""
            SELECT id FROM ir_model_fields 
            WHERE model = 'ir.ui.menu' AND name = 'restrict_user_ids'
        """)
        
        field_exists = cursor.fetchone()
        
        if not field_exists:
            print("Adding restrict_user_ids field to ir_model_fields...")
            
            # Get the model ID for ir.ui.menu
            cursor.execute("SELECT id FROM ir_model WHERE model = 'ir.ui.menu'")
            model_id = cursor.fetchone()[0]
            
            # Insert the field record
            cursor.execute("""
                INSERT INTO ir_model_fields 
                (name, model, model_id, field_description, ttype, relation, relation_table, column1, column2, store)
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'restrict_user_ids',
                'ir.ui.menu', 
                model_id,
                'Restricted Users',
                'many2many',
                'res.users',
                'ir_ui_menu_res_users_rel',
                'ir_ui_menu_id',
                'res_users_id',
                True
            ))
            
            print("Field added successfully")
        else:
            print("Field already exists in ir_model_fields")
        
        # Check if the relation table exists and has correct structure
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'ir_ui_menu_res_users_rel'
        """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating relation table ir_ui_menu_res_users_rel...")
            cursor.execute("""
                CREATE TABLE ir_ui_menu_res_users_rel (
                    ir_ui_menu_id integer NOT NULL,
                    res_users_id integer NOT NULL,
                    PRIMARY KEY (ir_ui_menu_id, res_users_id)
                )
            """)
            print("Relation table created successfully")
        else:
            print("Relation table already exists")
        
        # Commit changes
        conn.commit()
        
        print("Database fixes applied successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_hide_menu_user_db()
