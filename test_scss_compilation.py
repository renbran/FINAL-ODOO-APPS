#!/usr/bin/env python3
"""
SCSS Compilation Test for account_payment_final module
Validates that all SCSS variables are properly defined
"""

import os
import re
import sys
from pathlib import Path

def test_scss_variables():
    """Test that SCSS variables are properly defined"""
    base_path = Path(__file__).parent / "account_payment_final" / "static" / "src" / "scss"
    
    # Read variables file
    variables_file = base_path / "variables.scss"
    if not variables_file.exists():
        print("❌ Variables file not found!")
        return False
    
    with open(variables_file, 'r', encoding='utf-8') as f:
        variables_content = f.read()
    
    # Extract defined variables
    defined_vars = set()
    var_pattern = r'\$([a-zA-Z0-9_-]+):\s*([^;]+);'
    for match in re.finditer(var_pattern, variables_content):
        var_name = match.group(1)
        var_value = match.group(2).strip()
        defined_vars.add(var_name)
        print(f"✅ ${var_name}: {var_value}")
    
    # Check all SCSS files for variable usage
    scss_files = list(base_path.rglob("*.scss"))
    all_used_vars = set()
    undefined_vars = set()
    
    for scss_file in scss_files:
        if scss_file.name == "variables.scss":
            continue
            
        try:
            with open(scss_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find variable usage
            usage_pattern = r'\$([a-zA-Z0-9_-]+)'
            used_vars = set(re.findall(usage_pattern, content))
            all_used_vars.update(used_vars)
            
            # Check for undefined variables
            for var in used_vars:
                if var not in defined_vars:
                    undefined_vars.add(var)
                    print(f"❌ Undefined variable ${var} in {scss_file.relative_to(base_path)}")
        
        except Exception as e:
            print(f"⚠️  Error reading {scss_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Defined variables: {len(defined_vars)}")
    print(f"   Used variables: {len(all_used_vars)}")
    print(f"   Undefined variables: {len(undefined_vars)}")
    
    if undefined_vars:
        print(f"\n❌ Found {len(undefined_vars)} undefined variables:")
        for var in sorted(undefined_vars):
            print(f"   - ${var}")
        return False
    
    print("✅ All SCSS variables are properly defined!")
    return True

def test_scss_syntax():
    """Basic SCSS syntax validation"""
    base_path = Path(__file__).parent / "account_payment_final" / "static" / "src" / "scss"
    scss_files = list(base_path.rglob("*.scss"))
    
    print(f"\n🔍 Testing SCSS syntax in {len(scss_files)} files...")
    
    syntax_errors = []
    for scss_file in scss_files:
        try:
            with open(scss_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces != close_braces:
                syntax_errors.append(f"{scss_file.relative_to(base_path)}: Mismatched braces ({open_braces} open, {close_braces} close)")
            
            # Check for CSS var() usage in SCSS context
            if 'var(--' in content and not content.startswith('/*'):
                print(f"⚠️  CSS custom properties found in {scss_file.relative_to(base_path)} - may cause compilation issues")
            
        except Exception as e:
            syntax_errors.append(f"{scss_file.relative_to(base_path)}: {e}")
    
    if syntax_errors:
        print(f"❌ Found {len(syntax_errors)} syntax issues:")
        for error in syntax_errors:
            print(f"   - {error}")
        return False
    
    print("✅ SCSS syntax validation passed!")
    return True

def main():
    """Main test runner"""
    print("🔬 SCSS Compilation Test - account_payment_final")
    print("=" * 50)
    
    success = True
    success &= test_scss_variables()
    success &= test_scss_syntax()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All SCSS tests passed! Module should compile correctly.")
        sys.exit(0)
    else:
        print("❌ SCSS compilation issues detected. Please fix before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
