#!/usr/bin/env python3
"""
Comprehensive Database & JavaScript Compliance Audit
For OSUS Properties and Scholarix Odoo Instances
"""

import psycopg2
import json
import os
from datetime import datetime
from pathlib import Path

print('='*80)
print('COMPREHENSIVE DATABASE INTEGRITY & COMPLIANCE AUDIT')
print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*80)

def check_database_integrity(db_name):
    print(f'\n{"="*80}')
    print(f'DATABASE: {db_name}')
    print('='*80)
    
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user='odoo',
            host='localhost'
        )
        cur = conn.cursor()
        
        # 1. Database Size
        cur.execute("SELECT pg_size_pretty(pg_database_size(%s))", (db_name,))
        db_size = cur.fetchone()[0]
        print(f'\n📊 Database Size: {db_size}')
        
        # 2. Table Count
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        table_count = cur.fetchone()[0]
        print(f'📋 Total Tables: {table_count}')
        
        # 3. Installed Modules
        cur.execute("""
            SELECT name, state, latest_version 
            FROM ir_module_module 
            WHERE state = 'installed'
            ORDER BY name
        """)
        modules = cur.fetchall()
        print(f'\n🔧 Installed Modules: {len(modules)}')
        
        # OSUS/Custom Modules
        custom_modules = [m for m in modules if 'osus' in m[0].lower() or 'custom' in m[0].lower() 
                          or 'scholarix' in m[0].lower()]
        if custom_modules:
            print(f'\n🎨 OSUS/Custom Modules ({len(custom_modules)}):')
            for name, state, version in custom_modules[:20]:
                print(f'  ✓ {name} (v{version})')
        
        # 4. JavaScript Assets
        try:
            cur.execute("""
                SELECT COUNT(*) 
                FROM ir_asset 
                WHERE path LIKE '%.js'
            """)
            js_count = cur.fetchone()[0]
            print(f'\n📜 JavaScript Assets: {js_count}')
        except:
            print(f'\n📜 JavaScript Assets: (table not found)')
        
        # 5. Foreign Key Constraints
        cur.execute("""
            SELECT COUNT(*)
            FROM pg_constraint
            WHERE contype = 'f' AND convalidated = false
        """)
        invalid_fk = cur.fetchone()[0]
        if invalid_fk > 0:
            print(f'\n⚠️  Invalid Foreign Key Constraints: {invalid_fk}')
        else:
            print(f'\n✅ All Foreign Key Constraints Valid')
        
        # 6. Active Users
        cur.execute("SELECT COUNT(*) FROM res_users WHERE active = true")
        active_users = cur.fetchone()[0]
        print(f'\n👥 Active Users: {active_users}')
        
        # 7. Database Connections
        cur.execute("""
            SELECT COUNT(*) FROM pg_stat_activity 
            WHERE datname = %s
        """, (db_name,))
        connections = cur.fetchone()[0]
        print(f'🔌 Database Connections: {connections}')
        
        # 8. Check for duplicate modules
        cur.execute("""
            SELECT name, COUNT(*) as count
            FROM ir_module_module
            GROUP BY name
            HAVING COUNT(*) > 1
        """)
        duplicates = cur.fetchall()
        if duplicates:
            print(f'\n⚠️  Duplicate Modules: {len(duplicates)}')
            for name, count in duplicates[:10]:
                print(f'  - {name}: {count} entries')
        else:
            print(f'✅ No Duplicate Modules')
        
        # 9. Recent Errors
        try:
            cur.execute("""
                SELECT COUNT(*) FROM ir_logging 
                WHERE type = 'server' AND level = 'ERROR'
                AND create_date > NOW() - INTERVAL '7 days'
            """)
            errors = cur.fetchone()[0]
            print(f'\n📝 Recent Errors (7 days): {errors}')
        except:
            pass
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {str(e)}')
        return False

# Check JavaScript files for compliance
def check_javascript_compliance(base_path):
    print(f'\n{"="*80}')
    print(f'JAVASCRIPT COMPLIANCE CHECK')
    print('='*80)
    
    issues = []
    js_files = list(Path(base_path).rglob('*.js'))
    print(f'\n📂 Scanning {len(js_files)} JavaScript files...')
    
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for deprecated patterns
                if 'owl.Component' in content and '@odoo-module' not in content:
                    issues.append(f'❌ {js_file.relative_to(base_path)}: Missing @odoo-module directive')
                
                if 'onMounted(' in content and 'Component' not in content:
                    issues.append(f'⚠️  {js_file.relative_to(base_path)}: onMounted without component context')
                
                if 'useService' in content and '@web/core/utils/hooks' not in content:
                    issues.append(f'⚠️  {js_file.relative_to(base_path)}: useService without proper import')
                
        except Exception as e:
            pass
    
    if issues:
        print(f'\n⚠️  Found {len(issues)} compliance issues:')
        for issue in issues[:20]:
            print(f'  {issue}')
    else:
        print(f'\n✅ No major JavaScript compliance issues found')
    
    return len(issues)

# Run audits
for db_name in ['osusproperties', 'scholarixv2']:
    check_database_integrity(db_name)

print(f'\n{"="*80}')
print('AUDIT COMPLETE')
print('='*80)
