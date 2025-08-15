#!/usr/bin/env python3
"""
Find all problematic manifest files in the workspace
"""

import os
import ast
import glob

def check_all_manifests():
    """Check all manifest files for syntax issues."""
    print("🔍 Scanning all manifest files...")
    print("=" * 60)
    
    manifest_files = glob.glob("**/__manifest__.py", recursive=True)
    print(f"Found {len(manifest_files)} manifest files")
    
    problematic_files = []
    
    for manifest in manifest_files:
        try:
            with open(manifest, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse
            ast.literal_eval(content)
            print(f"✅ {manifest}")
            
        except SyntaxError as e:
            print(f"❌ {manifest}: SyntaxError at line {e.lineno}: {e.msg}")
            problematic_files.append((manifest, f"SyntaxError: {e.msg}"))
            
        except ValueError as e:
            print(f"❌ {manifest}: ValueError: {e}")
            problematic_files.append((manifest, f"ValueError: {e}"))
            
        except UnicodeDecodeError as e:
            print(f"❌ {manifest}: Unicode error: {e}")
            problematic_files.append((manifest, f"Unicode error: {e}"))
            
        except Exception as e:
            print(f"❌ {manifest}: {type(e).__name__}: {e}")
            problematic_files.append((manifest, f"{type(e).__name__}: {e}"))
    
    print("\n" + "="*60)
    if problematic_files:
        print(f"❌ Found {len(problematic_files)} problematic files:")
        for file, error in problematic_files:
            print(f"  • {file}: {error}")
    else:
        print("✅ All manifest files are valid!")
    
    return problematic_files

if __name__ == "__main__":
    problematic_files = check_all_manifests()
    
    if problematic_files:
        print(f"\n🔧 Fix these {len(problematic_files)} files to resolve CloudPepper errors")
    else:
        print("\n🎉 All manifest files are ready for deployment!")
