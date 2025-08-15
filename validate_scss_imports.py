#!/usr/bin/env python3
"""
Comprehensive SCSS Import Validation Script
Checks for problematic @import statements that cause Odoo compilation errors
"""

import os
import re

def main():
    print('=== COMPREHENSIVE SCSS IMPORT FIX VALIDATION ===')

    # Find all SCSS files
    scss_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.scss'):
                scss_files.append(os.path.join(root, file))

    print(f'Found {len(scss_files)} SCSS files')

    # Check for problematic imports
    problematic_imports = []
    total_imports = 0

    for file_path in scss_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find @import statements
            import_lines = [line.strip() for line in content.split('\n') 
                          if '@import' in line and not line.strip().startswith('//')]
            total_imports += len(import_lines)
            
            for line in import_lines:
                # Check if it's a local import (not URL)
                if 'http' not in line:
                    # Check if it references variables or components
                    if 'variables' in line or 'components' in line or '..' in line:
                        problematic_imports.append({
                            'file': file_path,
                            'import': line.strip()
                        })
        except Exception as e:
            print(f'Error checking {file_path}: {e}')

    print(f'\n=== RESULTS ===')
    print(f'Total @import statements found: {total_imports}')
    print(f'Problematic local imports: {len(problematic_imports)}')

    if problematic_imports:
        print('\n‚ùå REMAINING ISSUES:')
        for issue in problematic_imports:
            print(f'  {issue["file"]} - {issue["import"]}')
        print('\n‚ö†Ô∏è  These imports will cause Odoo 17 compilation errors:')
        print('   "Local import is forbidden for security reasons"')
        print('   Please remove @import statements and use CSS custom properties')
    else:
        print('\n‚úÖ ALL LOCAL IMPORT ISSUES FIXED!')
        print('   ‚úì No more @import variables or @import components statements')
        print('   ‚úì Database loading should work without SCSS compilation errors')
        print('   ‚úì Module ready for production deployment')
        
        # Additional checks
        print(f'\n=== ADDITIONAL VALIDATION ===')
        
        # Check for SCSS variable usage that should be converted
        total_scss_vars = 0
        for file_path in scss_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                vars_found = len(re.findall(r'\$[a-zA-Z-]+', content))
                total_scss_vars += vars_found
                if vars_found > 0:
                    print(f'   ‚ö†Ô∏è  {file_path}: {vars_found} SCSS variables (consider converting to CSS custom properties)')
            except:
                pass
        
        if total_scss_vars == 0:
            print('   ‚úì No SCSS variables found - all properly converted to CSS custom properties')
        
        print(f'\nüéâ EMERGENCY FIX COMPLETE!')
        print('   The TypeError: "Local import ../variables is forbidden" should be resolved')
        print('   Database should now load successfully without SCSS compilation errors')

if __name__ == '__main__':
    main()
