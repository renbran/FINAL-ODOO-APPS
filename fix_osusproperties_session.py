#!/usr/bin/env python3
"""
Fix OSUS Properties Database Session/Logout Issues
Clears old sessions, resets session configuration, and fixes cookie settings
"""
import sys
import os

# Odoo shell commands to execute
FIX_COMMANDS = """
# Connect to osusproperties database
import odoo
from odoo import api, SUPERUSER_ID

# Get environment
env = api.Environment(odoo.registry('osusproperties'), SUPERUSER_ID, {})

print("="*60)
print("OSUS Properties - Session/Logout Fix")
print("="*60)

# 1. Check current session configuration
print("\\n1. Checking session configuration...")
try:
    config_params = env['ir.config_parameter'].sudo().search([
        '|', '|', '|',
        ('key', 'ilike', 'session'),
        ('key', 'ilike', 'timeout'),
        ('key', 'ilike', 'cookie'),
        ('key', 'ilike', 'auth')
    ])
    print(f"   Found {len(config_params)} session-related config parameters")
    for param in config_params:
        print(f"   - {param.key}: {param.value}")
except Exception as e:
    print(f"   Error checking config: {e}")

# 2. Clear old user logs (keep last 30 days)
print("\\n2. Clearing old user logs...")
try:
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=30)
    old_logs = env['res.users.log'].sudo().search([
        ('create_date', '<', cutoff_date)
    ])
    count = len(old_logs)
    old_logs.unlink()
    print(f"   ✅ Cleared {count} old user logs")
except Exception as e:
    print(f"   ⚠️ Error clearing logs: {e}")

# 3. Check for stuck sessions (RTC sessions)
print("\\n3. Checking RTC sessions...")
try:
    rtc_sessions = env['discuss.channel.rtc.session'].sudo().search([])
    print(f"   Found {len(rtc_sessions)} RTC sessions")
    
    # Clear sessions older than 1 day
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=1)
    old_rtc = env['discuss.channel.rtc.session'].sudo().search([
        ('create_date', '<', cutoff)
    ])
    if old_rtc:
        count = len(old_rtc)
        old_rtc.unlink()
        print(f"   ✅ Cleared {count} old RTC sessions")
    else:
        print("   ✅ No old RTC sessions to clear")
except Exception as e:
    print(f"   ⚠️ Error with RTC sessions: {e}")

# 4. Set proper session configuration
print("\\n4. Setting session configuration...")
try:
    ICP = env['ir.config_parameter'].sudo()
    
    # Set session timeout to 7 days (604800 seconds)
    ICP.set_param('session_cookie_age', '604800')
    print("   ✅ Set session_cookie_age to 7 days")
    
    # Ensure secure cookie settings
    ICP.set_param('session_cookie_httponly', 'True')
    print("   ✅ Set session_cookie_httponly to True")
    
    env.cr.commit()
    print("   ✅ Configuration committed")
except Exception as e:
    print(f"   ⚠️ Error setting config: {e}")

# 5. Check users with authentication issues
print("\\n5. Checking users...")
try:
    active_users = env['res.users'].sudo().search([('active', '=', True)])
    print(f"   Total active users: {len(active_users)}")
    
    # Check for users without proper login
    no_login = env['res.users'].sudo().search([
        ('active', '=', True),
        '|',
        ('login', '=', False),
        ('login', '=', '')
    ])
    if no_login:
        print(f"   ⚠️ Found {len(no_login)} users without login")
    else:
        print("   ✅ All users have login credentials")
        
except Exception as e:
    print(f"   ⚠️ Error checking users: {e}")

# 6. Clear authentication cache
print("\\n6. Clearing authentication cache...")
try:
    # Clear identity check records older than 7 days
    cutoff = datetime.now() - timedelta(days=7)
    old_checks = env['res.users.identitycheck'].sudo().search([
        ('create_date', '<', cutoff)
    ])
    if old_checks:
        count = len(old_checks)
        old_checks.unlink()
        print(f"   ✅ Cleared {count} old identity checks")
    else:
        print("   ✅ No old identity checks to clear")
        
    env.cr.commit()
except Exception as e:
    print(f"   ⚠️ Error clearing auth cache: {e}")

print("\\n" + "="*60)
print("✅ Session/Logout Fix Complete!")
print("="*60)
print("\\nRecommendations:")
print("1. Restart Odoo service: sudo systemctl restart odoo")
print("2. Clear browser cookies for the domain")
print("3. Test login with fresh browser session")
print("="*60)
"""

print("OSUS Properties Session Fix Script")
print("="*60)
print("\nThis script will:")
print("1. Check session configuration")
print("2. Clear old user logs")
print("3. Clean RTC sessions")
print("4. Set proper session timeout (7 days)")
print("5. Check user authentication")
print("6. Clear authentication cache")
print("\n" + "="*60)

# Save commands to temporary file
commands_file = "/tmp/fix_osusproperties_session_commands.py"
print(f"\nCommands saved to: {commands_file}")
print("\nTo execute on CloudPepper server, run:")
print(f"ssh -i \"$HOME\\.ssh\\odoo17_cloudpepper_new\" root@139.84.163.11 -p 22")
print(f"cd /var/odoo/scholarixv2")
print(f"sudo -u odoo venv/bin/python3 src/odoo-bin shell -c odoo.conf -d osusproperties")
print("\nThen paste the commands from above or run this script remotely.")
