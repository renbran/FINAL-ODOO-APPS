#!/usr/bin/env python3
"""
Direct database cleanup script for removing problematic views
Run this using: python fix_view_conflicts.py
"""

import psycopg2
import sys

def cleanup_problematic_views():
    """Remove problematic views directly from database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            database="odoo17_final",
            user="odoo",  # Adjust as needed
            password="odoo"  # Adjust as needed
        )
        
        cur = conn.cursor()
        
        print("Cleaning up problematic views...")
        
        # Delete problematic views
        queries = [
            "DELETE FROM ir_ui_view WHERE name = 'account.move.form.inherit.sale.order.type';",
            "DELETE FROM ir_ui_view WHERE model = 'account.move' AND name ILIKE '%sale.order.type%';",
            "DELETE FROM ir_model_data WHERE name = 'view_move_form_inherit_sale_order_type';",
            "DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND name ILIKE '%sale_order_type%';",
        ]
        
        for query in queries:
            try:
                cur.execute(query)
                print(f"Executed: {query}")
            except Exception as e:
                print(f"Warning: {query} failed: {e}")
        
        # Clear view cache
        cur.execute("UPDATE ir_ui_view SET arch_db = arch_db WHERE id > 0;")
        
        conn.commit()
        print("✅ Database cleanup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please check your database connection settings")
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    cleanup_problematic_views()
