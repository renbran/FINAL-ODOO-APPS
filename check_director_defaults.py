#!/usr/bin/env python3
"""
Script to check commission_ax module for director commission default values.
"""

import os
import re

def check_director_defaults():
    """Check for director commission defaults in commission_ax modules."""
    base_paths = [
        "commission_ax",
        "custom/commission_ax"
    ]
    
    results = []
    
    for base_path in base_paths:
        if not os.path.exists(base_path):
            print(f"❌ Path {base_path} does not exist")
            continue
            
        print(f"🔍 Checking {base_path}...")
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check for director fields with default values > 0
                        director_default_pattern = r'director.*default\s*=\s*([0-9]+\.?[0-9]*)'
                        matches = re.finditer(director_default_pattern, content, re.IGNORECASE)
                        
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            default_value = float(match.group(1))
                            
                            if default_value > 0:
                                results.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'value': default_value,
                                    'match': match.group(0)
                                })
                                print(f"❌ Found non-zero default in {file_path}:{line_num} -> {match.group(0)}")
                            else:
                                print(f"✅ Found zero default in {file_path}:{line_num} -> {match.group(0)}")
                                
                    except Exception as e:
                        print(f"⚠️  Error reading {file_path}: {e}")
    
    print("\n" + "="*50)
    if results:
        print("❌ VALIDATION FAILED!")
        print("Non-zero director commission defaults found:")
        for result in results:
            print(f"  {result['file']}:{result['line']} -> {result['match']} (value: {result['value']})")
        return False
    else:
        print("✅ VALIDATION SUCCESSFUL!")
        print("All director commission fields have zero defaults.")
        return True

if __name__ == "__main__":
    success = check_director_defaults()
    exit(0 if success else 1)
