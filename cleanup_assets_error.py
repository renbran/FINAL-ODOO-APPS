#!/usr/bin/env python3
"""
Emergency cleanup script to remove leftover payment_account_enhanced references
that are causing web.assets_backend errors
"""

import subprocess
import sys

def run_sql_cleanup():
    """Run SQL commands to clean up leftover payment_account_enhanced references"""
    
    cleanup_commands = [
        # Remove any views that reference payment_account_enhanced and web.assets_backend
        "DELETE FROM ir_ui_view WHERE arch_db LIKE '%payment_account_enhanced%' AND arch_db LIKE '%inherit_id=\"web.assets_backend\"%';",
        
        # Remove any leftover model data references
        "DELETE FROM ir_model_data WHERE module = 'payment_account_enhanced';",
        
        # Remove any leftover attachment references
        "DELETE FROM ir_attachment WHERE name LIKE '%payment_account_enhanced%';",
        
        # Remove any asset bundle references
        "DELETE FROM ir_asset WHERE path LIKE '%payment_account_enhanced%';",
        
        # Clean up any leftover template references
        "DELETE FROM ir_ui_view WHERE name LIKE '%payment_account_enhanced%';",
        
        # Remove any QWeb template references
        "DELETE FROM ir_qweb WHERE arch_db LIKE '%payment_account_enhanced%';",
    ]
    
    print("🧹 Starting emergency cleanup of payment_account_enhanced references...")
    
    for i, cmd in enumerate(cleanup_commands, 1):
        print(f"\n{i}. Executing: {cmd}")
        try:
            result = subprocess.run([
                'docker-compose', 'exec', 'db', 'psql', 
                '-U', 'odoo', '-d', 'odoo', '-c', cmd
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                print(f"   ✅ Output: {result.stdout.strip()}")
            else:
                print("   ✅ Command executed successfully")
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error: {e}")
            if e.stderr:
                print(f"   Error details: {e.stderr}")

def restart_odoo():
    """Restart Odoo service to clear cache"""
    print("\n🔄 Restarting Odoo to clear cache...")
    try:
        subprocess.run(['docker-compose', 'restart', 'odoo'], check=True)
        print("✅ Odoo restarted successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restart Odoo: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚨 EMERGENCY CLEANUP: payment_account_enhanced references")
    print("=" * 60)
    
    run_sql_cleanup()
    restart_odoo()
    
    print("\n" + "=" * 60)
    print("✅ Cleanup completed!")
    print("You can now try installing account_payment_final module again.")
    print("=" * 60)
