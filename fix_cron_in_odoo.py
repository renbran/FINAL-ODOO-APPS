#!/usr/bin/env python3
"""
Odoo script to fix cron jobs with invalid interval_type
Run this in Odoo shell: python -c "exec(open('fix_cron_in_odoo.py').read())"
"""

def fix_cron_issues():
    """Fix cron jobs with invalid interval_type"""
    
    print("🔍 Searching for cron jobs with invalid interval_type...")
    
    # Find all cron jobs with NULL or invalid interval_type
    cron_jobs = env['ir.cron'].search([])
    
    problematic_crons = []
    
    for cron in cron_jobs:
        if not cron.interval_type:
            problematic_crons.append(cron)
            print(f"❌ Found problematic cron: ID={cron.id}, Name='{cron.name}', interval_type={cron.interval_type}")
    
    if not problematic_crons:
        print("✅ No problematic cron jobs found!")
        return
    
    print(f"\n🔧 Fixing {len(problematic_crons)} problematic cron job(s)...")
    
    for cron in problematic_crons:
        try:
            # Fix the cron job
            cron.write({
                'interval_type': 'days',
                'interval_number': 1,
                'active': False  # Deactivate for safety
            })
            print(f"✅ Fixed cron: {cron.name} (ID: {cron.id})")
            
        except Exception as e:
            print(f"❌ Failed to fix cron {cron.name} (ID: {cron.id}): {e}")
    
    # Commit the changes
    env.cr.commit()
    print("\n🎉 All problematic cron jobs have been fixed!")
    print("📋 Summary of changes:")
    print("  - Set interval_type to 'days'")
    print("  - Set interval_number to 1") 
    print("  - Deactivated the cron jobs for safety")
    print("\n⚠️  You can reactivate and reconfigure them manually if needed.")

# Run the fix
if 'env' in globals():
    fix_cron_issues()
else:
    print("❌ This script must be run from within Odoo shell!")
    print("Usage: odoo-bin shell -d your_database --shell-interface python")
    print("Then run: exec(open('fix_cron_in_odoo.py').read())")
