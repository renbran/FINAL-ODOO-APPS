#!/usr/bin/env python3
"""
CloudPepper Manifest Diagnostic Tool
Diagnoses and fixes manifest file issues that cause SyntaxError in Odoo
"""

import os
import ast
import json
import sys
from pathlib import Path

def check_manifest_syntax(manifest_path):
    """Check manifest file for syntax issues."""
    print(f"\n🔍 Checking: {manifest_path}")
    print("=" * 60)
    
    try:
        # Read the file
        with open(manifest_path, 'rb') as f:
            raw_content = f.read()
        
        # Check encoding
        print(f"📄 File size: {len(raw_content)} bytes")
        
        # Check for BOM
        if raw_content.startswith(b'\xef\xbb\xbf'):
            print("⚠️  UTF-8 BOM detected - this can cause issues!")
            return False
        elif raw_content.startswith((b'\xff\xfe', b'\xfe\xff')):
            print("⚠️  UTF-16 BOM detected - this can cause issues!")
            return False
        else:
            print("✅ No BOM detected")
        
        # Check line endings
        if b'\r\n' in raw_content:
            print("⚠️  Windows line endings (\\r\\n) detected")
        elif b'\r' in raw_content:
            print("⚠️  Mac line endings (\\r) detected")
        else:
            print("✅ Unix line endings (\\n)")
        
        # Decode content
        try:
            content = raw_content.decode('utf-8')
        except UnicodeDecodeError as e:
            print(f"❌ Unicode decode error: {e}")
            return False
        
        # Check for invisible characters at start
        if content != content.lstrip():
            print("⚠️  Leading whitespace detected")
        
        # Check if it starts with '{'
        stripped = content.strip()
        if not stripped.startswith('{'):
            print(f"❌ File doesn't start with '{{' - starts with: {repr(stripped[:10])}")
            return False
        else:
            print("✅ File starts with '{'")
        
        # Check if it ends with '}'
        if not stripped.endswith('}'):
            print(f"❌ File doesn't end with '}}' - ends with: {repr(stripped[-10:])}")
            return False
        else:
            print("✅ File ends with '}'")
        
        # Try AST parsing
        try:
            parsed = ast.literal_eval(content)
            print("✅ AST parsing successful")
            
            # Check if it's a valid dict
            if not isinstance(parsed, dict):
                print(f"❌ Content is not a dict: {type(parsed)}")
                return False
            
            # Check required keys
            required_keys = ['name', 'version', 'depends', 'installable']
            missing_keys = [key for key in required_keys if key not in parsed]
            if missing_keys:
                print(f"⚠️  Missing required keys: {missing_keys}")
            else:
                print("✅ All required keys present")
            
            print(f"📊 Module name: {parsed.get('name', 'Unknown')}")
            print(f"📊 Version: {parsed.get('version', 'Unknown')}")
            print(f"📊 Dependencies: {parsed.get('depends', [])}")
            
            return True
            
        except SyntaxError as e:
            print(f"❌ AST SyntaxError: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            return False
        except ValueError as e:
            print(f"❌ AST ValueError: {e}")
            return False
        except Exception as e:
            print(f"❌ AST unexpected error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return False

def fix_manifest_file(manifest_path):
    """Fix common manifest file issues."""
    print(f"\n🔧 Fixing: {manifest_path}")
    print("=" * 60)
    
    try:
        # Read the original file
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        backup_path = manifest_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📝 Backup created: {backup_path}")
        
        # Fix line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove any BOM
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Strip and ensure proper ending
        content = content.strip()
        if not content.endswith('\n'):
            content += '\n'
        
        # Write the fixed file
        with open(manifest_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print("✅ File fixed and saved")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix file: {e}")
        return False

def main():
    """Main diagnostic function."""
    print("🚀 CloudPepper Manifest Diagnostic Tool")
    print("=" * 80)
    
    # Check our specific module
    manifest_path = "order_status_override/__manifest__.py"
    
    if not os.path.exists(manifest_path):
        print(f"❌ Manifest file not found: {manifest_path}")
        sys.exit(1)
    
    # Check syntax
    is_valid = check_manifest_syntax(manifest_path)
    
    if not is_valid:
        print("\n🔧 Attempting to fix issues...")
        if fix_manifest_file(manifest_path):
            print("\n🔍 Re-checking after fix...")
            is_valid = check_manifest_syntax(manifest_path)
    
    # Final result
    print("\n" + "="*80)
    if is_valid:
        print("✅ MANIFEST FILE IS VALID - Ready for CloudPepper!")
    else:
        print("❌ MANIFEST FILE HAS ISSUES - Please review and fix manually")
    
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main())
