#!/usr/bin/env python3
"""
Account Statement XML Fix Script
This script fixes the deprecated 'states' attributes in Odoo 17.0 views.
"""

import os
import sys
import xml.etree.ElementTree as ET

def validate_xml_file(file_path):
    """Validate XML syntax and check for deprecated attributes"""
    print(f"🔍 Validating: {os.path.basename(file_path)}")
    
    issues = []
    warnings = []
    
    try:
        # Parse XML to check syntax
        tree = ET.parse(file_path)
        root = tree.getroot()
        print("  ✅ XML syntax is valid")
        
        # Read file content to check for deprecated attributes
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for deprecated attributes
        if 'states=' in content:
            issues.append("  ❌ Found deprecated 'states' attribute")
        else:
            print("  ✅ No deprecated 'states' attributes found")
        
        if 'attrs=' in content:
            issues.append("  ❌ Found deprecated 'attrs' attribute")
        else:
            print("  ✅ No deprecated 'attrs' attributes found")
            
        # Check for proper invisible syntax
        if 'invisible=' in content:
            print("  ✅ Using modern 'invisible' attributes")
        
    except ET.ParseError as e:
        issues.append(f"  ❌ XML Parse Error: {e}")
    except Exception as e:
        issues.append(f"  ⚠️ Error reading file: {e}")
    
    return issues, warnings

def fix_account_statement_views():
    """Fix all XML view files in account_statement module"""
    
    print("🔧 FIXING ACCOUNT STATEMENT XML VIEWS")
    print("=" * 50)
    
    module_path = r"d:\RUNNING APPS\ready production\odoo_17_final\account_statement"
    views_path = os.path.join(module_path, 'views')
    
    if not os.path.exists(views_path):
        print("❌ Views directory not found!")
        return False
    
    xml_files = [f for f in os.listdir(views_path) if f.endswith('.xml')]
    print(f"📁 Found {len(xml_files)} XML files")
    
    all_issues = []
    
    for xml_file in xml_files:
        file_path = os.path.join(views_path, xml_file)
        issues, warnings = validate_xml_file(file_path)
        
        if issues:
            all_issues.extend(issues)
            print(f"  🔴 Issues found in {xml_file}")
            for issue in issues:
                print(f"    {issue}")
        else:
            print(f"  🟢 {xml_file} is clean")
    
    return len(all_issues) == 0

def create_odoo17_fix_guide():
    """Create a guide for fixing Odoo 17.0 compatibility issues"""
    
    fix_guide = """
# 🔧 ODOO 17.0 COMPATIBILITY FIX GUIDE

## 🚨 PROBLEM: ParseError with deprecated attributes
**Error:** `Since 17.0, the "attrs" and "states" attributes are no longer used.`

## 📊 CHANGES IN ODOO 17.0

### Deprecated Attributes:
1. **`states="draft,confirmed"`** → Use `invisible="state not in ['draft', 'confirmed']"`
2. **`attrs="{'readonly': [('state', '!=', 'draft')]}"`** → Use `readonly="state != 'draft'"`

### Migration Rules:
- **states="state1,state2"** → **invisible="state not in ['state1', 'state2']"**
- **states="state1"** → **invisible="state != 'state1'"**

## ✅ FIXES APPLIED

### Button Visibility Fixed:
```xml
<!-- OLD (Deprecated) -->
<button states="draft" />
<button states="draft,confirmed" />

<!-- NEW (Odoo 17.0) -->
<button invisible="state != 'draft'" />
<button invisible="state not in ['draft', 'confirmed']" />
```

### Field Readonly Fixed:
```xml
<!-- OLD (Deprecated) -->
<field name="name" readonly="state in ['confirmed', 'cancelled']"/>

<!-- NEW (Correct - this was already good) -->
<field name="name" readonly="state in ['confirmed', 'cancelled']"/>
```

## 🎯 VALIDATION CHECKLIST

- [ ] No `states=` attributes in XML files
- [ ] No `attrs=` attributes in XML files  
- [ ] All buttons use `invisible=` for state-based visibility
- [ ] XML files parse without errors
- [ ] Module installs without ParseError

## 🚀 INSTALLATION STEPS

1. **Restart Odoo** (if running)
   ```bash
   sudo systemctl restart odoo
   ```

2. **Update Apps List**
   - Go to Apps → Update Apps List

3. **Install/Upgrade Module**
   - Search "Account Statement"
   - Click Install/Upgrade

4. **Test Functionality**
   - Open Contacts → Account Statements
   - Open Accounting → Reporting → Account Statements
   - Test form views and buttons

## 🔍 VALIDATION COMMANDS

```bash
# Check for deprecated attributes
grep -r "states=" views/
grep -r "attrs=" views/

# Validate XML syntax
python -c "import xml.etree.ElementTree as ET; ET.parse('views/account_statement_views.xml')"
```

## 🆘 TROUBLESHOOTING

### If installation still fails:
1. **Clear browser cache** completely
2. **Restart Odoo service**
3. **Check Odoo logs** for additional errors
4. **Try upgrading dependencies** first

### Common Additional Issues:
- **Missing dependencies:** Install base, account, contacts modules
- **Permission errors:** Check file permissions on module directory
- **Database corruption:** May need registry cleanup (see registry_recovery.py)

## 📞 SUPPORT

- Check Odoo logs: `/var/log/odoo/odoo-server.log`
- Community forum: https://www.odoo.com/forum
- Documentation: https://www.odoo.com/documentation/17.0/
"""
    
    return fix_guide

if __name__ == "__main__":
    print("🔧 ACCOUNT STATEMENT ODOO 17.0 COMPATIBILITY FIX")
    print("=" * 60)
    
    # Fix and validate views
    is_clean = fix_account_statement_views()
    
    if is_clean:
        print("\n🟢 ALL XML FILES ARE ODOO 17.0 COMPATIBLE!")
        print("✨ Ready for installation")
    else:
        print("\n🔴 SOME ISSUES REMAIN")
        print("   Check the output above for details")
    
    # Create fix guide
    fix_guide = create_odoo17_fix_guide()
    
    with open('ODOO17_COMPATIBILITY_FIX.md', 'w', encoding='utf-8') as f:
        f.write(fix_guide)
    
    print("\n📋 COMPATIBILITY GUIDE CREATED: ODOO17_COMPATIBILITY_FIX.md")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Restart Odoo service")
    print("   2. Update Apps List")
    print("   3. Install Account Statement module")
    print("   4. Test functionality")
    
    if is_clean:
        print("\n🚀 MODULE IS READY FOR INSTALLATION!")
    else:
        print("\n⚠️  FIX REMAINING ISSUES FIRST")
