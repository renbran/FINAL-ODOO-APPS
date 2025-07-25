#!/usr/bin/env python3
"""
Simple script to run payment reference fix
Run this from the project root directory
"""

import subprocess
import sys
import os

def run_fix_script():
    """Run the payment reference fix script using Odoo shell"""
    
    # Get database name from user
    db_name = input("Enter your database name: ")
    
    # Path to the script
    script_path = "/mnt/extra-addons/osus_invoice_report/scripts/fix_payment_references.py"
    
    # Odoo shell command
    shell_commands = f"""
exec(open('{script_path}').read())
fix_payment_references(env)
exit()
"""
    
    print(f"Running fix script for database: {db_name}")
    print("This will fix missing payment reference numbers...")
    
    # Write commands to temporary file
    with open("temp_fix_commands.py", "w") as f:
        f.write(shell_commands)
    
    try:
        # Run docker-compose exec with the commands
        result = subprocess.run([
            "docker-compose", "exec", "-T", "odoo", 
            "odoo", "shell", "-d", db_name, 
            "--init", "temp_fix_commands.py"
        ], capture_output=True, text=True)
        
        print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
    except Exception as e:
        print(f"Error running script: {e}")
        print("\nManual method:")
        print(f"1. Run: docker-compose exec odoo odoo shell -d {db_name}")
        print("2. In shell: exec(open('/mnt/extra-addons/osus_invoice_report/scripts/fix_payment_references.py').read())")
        print("3. In shell: fix_payment_references(env)")
    
    finally:
        # Clean up temp file
        if os.path.exists("temp_fix_commands.py"):
            os.remove("temp_fix_commands.py")

if __name__ == "__main__":
    run_fix_script()
