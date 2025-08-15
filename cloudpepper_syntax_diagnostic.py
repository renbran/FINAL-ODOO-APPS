#!/usr/bin/env python3
"""
CloudPepper Syntax Diagnostic Tool
Comprehensive error detection and fixing for Odoo modules
"""

import os
import ast
import re
import sys
from pathlib import Path

def check_field_definitions(file_path):
    """Check for problematic field definitions that could cause @ operator errors"""
    print(f"Checking field definitions in: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for Monetary field definitions
            if 'fields.Monetary(' in line:
                # Check if the line is properly terminated
                line_stripped = line.strip()
                if not line_stripped.endswith((',', ')')):
                    # Look at the next few lines to see if it's a multi-line definition
                    multiline_ok = False
                    for j in range(i, min(i+5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line.endswith(')') or next_line.endswith(','):
                            multiline_ok = True
                            break
                    
                    if not multiline_ok:
                        issues.append(f"Line {i}: Potentially incomplete Monetary field definition")
                        print(f"  WARNING Line {i}: {line.strip()}")
            
            # Check for decorator syntax issues
            if line.strip().startswith('@') and 'fields.' in line:
                issues.append(f"Line {i}: Suspicious decorator pattern with fields")
                print(f"  ERROR Line {i}: {line.strip()}")
            
            # Check for @ operator misuse
            if '@' in line and 'fields.Monetary' in line and not line.strip().startswith('#'):
                if not line.strip().startswith('@api.') and not line.strip().startswith('@'):
                    issues.append(f"Line {i}: Potential @ operator misuse with Monetary field")
                    print(f"  ERROR Line {i}: {line.strip()}")
        
        if issues:
            print(f"  Found {len(issues)} potential issues")
            return False
        else:
            print(f"  No field definition issues found")
            return True
            
    except Exception as e:
        print(f"  ERROR reading file: {e}")
        return False

def check_python_syntax(file_path):
    """Check Python syntax using AST"""
    print(f"Checking Python syntax: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        print(f"  ✓ Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"  ✗ SYNTAX ERROR Line {e.lineno}: {e.msg}")
        print(f"    Text: {e.text.strip() if e.text else 'N/A'}")
        return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def check_imports(file_path):
    """Check for problematic imports"""
    print(f"Checking imports: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        issues = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for circular imports
            if line_stripped.startswith('from .') and 'models' in line_stripped:
                print(f"  Line {i}: Relative import detected: {line.strip()}")
            
            # Check for missing imports
            if 'fields.Monetary' in line and 'from odoo import' not in content:
                issues.append(f"Line {i}: Monetary field used but odoo not imported")
        
        if issues:
            print(f"  Found {len(issues)} import issues")
            return False
        else:
            print(f"  ✓ Imports OK")
            return True
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def fix_common_issues(file_path):
    """Fix common syntax issues that could cause @ operator errors"""
    print(f"Attempting to fix common issues in: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        changes_made = False
        
        for i, line in enumerate(lines):
            fixed_line = line
            
            # Fix common field definition issues
            if 'fields.Monetary(' in line:
                # Ensure proper parentheses closure
                if line.count('(') > line.count(')'):
                    # This might be a multi-line definition, check if it needs fixing
                    if not any(')' in lines[j] for j in range(i+1, min(i+5, len(lines)))):
                        # No closing parenthesis found in next few lines
                        if not line.strip().endswith(','):
                            fixed_line = line.rstrip() + ','
                            changes_made = True
                            print(f"  Fixed Line {i+1}: Added missing comma")
            
            # Fix decorator issues
            if line.strip().startswith('@') and 'fields.Monetary' in line:
                # This is definitely wrong - @ decorator followed by field definition
                if '@api.' not in line:
                    # Remove the @ if it's not a proper decorator
                    fixed_line = line.replace('@', '')
                    changes_made = True
                    print(f"  Fixed Line {i+1}: Removed invalid @ operator")
            
            fixed_lines.append(fixed_line)
        
        if changes_made:
            # Write the fixed content back
            fixed_content = '\n'.join(fixed_lines)
            
            # Backup original
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"  Backup created: {backup_path}")
            
            # Write fixed version
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  ✓ Fixed and saved")
            
            return True
        else:
            print(f"  No fixes needed")
            return True
            
    except Exception as e:
        print(f"  ERROR during fix: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("=" * 60)
    print("CloudPepper Syntax Diagnostic Tool")
    print("=" * 60)
    
    # Get the current directory
    base_path = Path.cwd()
    print(f"Base path: {base_path}")
    
    # Find all Python model files
    python_files = []
    for pattern in ['**/models/*.py', '**/models.py']:
        python_files.extend(base_path.glob(pattern))
    
    # Remove __init__.py files
    python_files = [f for f in python_files if f.name != '__init__.py']
    
    print(f"Found {len(python_files)} Python model files to check")
    print()
    
    all_ok = True
    critical_files = []
    
    # Prioritize sale_order.py files as they were mentioned in the error
    sale_order_files = [f for f in python_files if 'sale_order.py' in str(f)]
    other_files = [f for f in python_files if 'sale_order.py' not in str(f)]
    
    files_to_check = sale_order_files + other_files[:10]  # Check sale_order files + first 10 others
    
    for file_path in files_to_check:
        print(f"\n{'='*60}")
        print(f"CHECKING: {file_path.relative_to(base_path)}")
        print(f"{'='*60}")
        
        # Check syntax first
        syntax_ok = check_python_syntax(file_path)
        
        # Check field definitions
        fields_ok = check_field_definitions(file_path)
        
        # Check imports
        imports_ok = check_imports(file_path)
        
        # If there are issues, try to fix them
        if not (syntax_ok and fields_ok and imports_ok):
            all_ok = False
            critical_files.append(str(file_path.relative_to(base_path)))
            
            print(f"\n  ATTEMPTING FIXES...")
            fix_success = fix_common_issues(file_path)
            
            if fix_success:
                # Re-check syntax after fixes
                print(f"  Re-checking syntax after fixes...")
                new_syntax_ok = check_python_syntax(file_path)
                if new_syntax_ok:
                    print(f"  ✓ File fixed successfully!")
                else:
                    print(f"  ✗ File still has issues after fix attempt")
        else:
            print(f"  ✓ All checks passed")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    if all_ok:
        print("✓ All checked files passed validation")
    else:
        print(f"✗ Issues found in {len(critical_files)} files:")
        for file in critical_files:
            print(f"  - {file}")
    
    print(f"\nDiagnostic complete.")
    
    if not all_ok:
        print("\nRecommendations:")
        print("1. Check the CloudPepper deployment for version mismatches")
        print("2. Review the .backup files for any critical changes")
        print("3. Run 'python -m py_compile <file>' on each problematic file")
        print("4. Consider restarting the Odoo service after fixes")

if __name__ == "__main__":
    main()
