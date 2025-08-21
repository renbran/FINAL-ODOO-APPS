#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CloudPepper Emergency Manifest Syntax Checker
==============================================

This script checks all __manifest__.py files for syntax errors
and provides detailed error reporting for immediate CloudPepper deployment.

Usage: python cloudpepper_manifest_emergency_check.py
"""

import ast
import os
import sys
import traceback
from pathlib import Path

def check_manifest_syntax(manifest_path):
    """
    Check a single manifest file for syntax errors.
    
    Args:
        manifest_path (str): Path to the manifest file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file is empty or contains only whitespace
        if not content.strip():
            return False, "Empty manifest file"
        
        # Try to parse the Python code
        ast.parse(content)
        return True, None
        
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}, column {e.offset}"
    except UnicodeDecodeError as e:
        return False, f"UnicodeDecodeError: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def find_all_manifests(root_dir="."):
    """
    Find all __manifest__.py files in the directory tree.
    
    Args:
        root_dir (str): Root directory to search
        
    Returns:
        list: List of manifest file paths
    """
    manifests = []
    root_path = Path(root_dir)
    
    for manifest_path in root_path.glob("**/__manifest__.py"):
        manifests.append(str(manifest_path))
    
    return sorted(manifests)

def main():
    """Main function to check all manifest files."""
    print("🔍 CloudPepper Emergency Manifest Syntax Checker")
    print("=" * 50)
    
    manifests = find_all_manifests()
    
    if not manifests:
        print("❌ No __manifest__.py files found!")
        return 1
    
    print(f"📋 Found {len(manifests)} manifest files to check...")
    print()
    
    errors_found = []
    success_count = 0
    
    for manifest_path in manifests:
        print(f"Checking: {manifest_path}")
        
        is_valid, error_msg = check_manifest_syntax(manifest_path)
        
        if is_valid:
            print(f"✅ {manifest_path}")
            success_count += 1
        else:
            print(f"❌ {manifest_path}")
            print(f"   Error: {error_msg}")
            errors_found.append((manifest_path, error_msg))
            
            # Try to show the problematic content
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"   File content preview (first 10 lines):")
                    for i, line in enumerate(lines[:10], 1):
                        print(f"   {i:2}: {line.rstrip()}")
                    if len(lines) > 10:
                        print(f"   ... ({len(lines)} total lines)")
            except Exception as e:
                print(f"   Could not read file content: {e}")
        
        print()
    
    # Summary
    print("🎯 SUMMARY")
    print("=" * 20)
    print(f"✅ Valid manifests: {success_count}")
    print(f"❌ Invalid manifests: {len(errors_found)}")
    print()
    
    if errors_found:
        print("🚨 ERRORS FOUND:")
        print("-" * 20)
        for manifest_path, error_msg in errors_found:
            print(f"❌ {manifest_path}")
            print(f"   {error_msg}")
            print()
        
        print("🔧 EMERGENCY FIX RECOMMENDATIONS:")
        print("-" * 35)
        print("1. Check for missing quotes, commas, or brackets")
        print("2. Verify all string quotes are properly closed")
        print("3. Ensure no special characters in manifest")
        print("4. Check for empty or corrupted files")
        print("5. Verify UTF-8 encoding")
        print()
        
        return 1
    else:
        print("🎉 ALL MANIFEST FILES ARE VALID!")
        print("✅ No syntax errors found in any __manifest__.py files")
        print("🚀 Ready for CloudPepper deployment")
        return 0

if __name__ == "__main__":
    sys.exit(main())
