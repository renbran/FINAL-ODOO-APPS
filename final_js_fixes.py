#!/usr/bin/env python3
"""
Final JavaScript Fix Implementation - Targeted Fixes for Remaining Issues
"""

import os
import re
from pathlib import Path

class FinalJSFixes:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        
    def apply_final_fixes(self):
        """Apply final targeted fixes"""
        
        print("🎯 Applying Final JavaScript Fixes...")
        print("="*50)
        
        # Fix 1: Update error prevention files to NOT be Odoo modules
        self.fix_error_prevention_files()
        
        # Fix 2: Fix === operator issues in critical files
        self.fix_critical_equality_operators()
        
        # Fix 3: Remove console.log from legacy files but keep console.debug
        self.fix_console_statements()
        
        # Fix 4: Fix function structure issues
        self.fix_function_returns()
        
        print("\n✅ Final fixes completed!")
        
    def fix_error_prevention_files(self):
        """Fix error prevention files - they should NOT be Odoo modules"""
        
        files_to_fix = [
            'static/src/js/immediate_error_prevention.js',
            'static/src/js/cloudpepper_clean_fix.js'
        ]
        
        for file_path in files_to_fix:
            full_path = self.module_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                
                # Add comment explaining why no @odoo-module
                if '/** @odoo-module **/' not in content:
                    header_comment = f"""/*
 * {full_path.name.replace('_', ' ').title()}
 * 
 * This file intentionally does NOT use /** @odoo-module **/
 * as it's a global error prevention utility loaded before
 * any Odoo modules to prevent import/loading errors.
 */

"""
                    content = header_comment + content
                    full_path.write_text(content, encoding='utf-8')
                    print(f"✅ Fixed {file_path}")
                    
    def fix_critical_equality_operators(self):
        """Fix === operators in critical files only (not legacy files)"""
        
        critical_files = [
            'static/src/js/payment_voucher.js',
            'static/src/js/components/payment_approval_widget.js',
            'static/src/js/fields/qr_code_field.js',
            'static/src/js/utils/payment_utils.js',
        ]
        
        for file_path in critical_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                original_content = content
                
                # Fix equality operators (but be careful with template strings)
                lines = content.split('\n')
                fixed_lines = []
                
                for line in lines:
                    # Skip template strings and comments
                    if ('`' in line or line.strip().startswith('//') or 
                        line.strip().startswith('/*') or '===' in line):
                        fixed_lines.append(line)
                        continue
                        
                    # Fix == to === but avoid ===== 
                    if ' == ' in line and ' === ' not in line:
                        line = line.replace(' == ', ' === ')
                    elif '!=' in line and '!==' not in line:
                        line = line.replace('!=', '!==')
                        
                    fixed_lines.append(line)
                
                content = '\n'.join(fixed_lines)
                
                if content != original_content:
                    full_path.write_text(content, encoding='utf-8')
                    print(f"✅ Fixed equality operators in {file_path}")
                    
    def fix_console_statements(self):
        """Replace console.log with console.debug in legacy files"""
        
        legacy_files = [
            'static/src/js/legacy_compatible_fix.js',
            'static/src/js/ultimate_module_fix.js'
        ]
        
        for file_path in legacy_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                
                # Replace console.log with console.debug to keep debugging info
                content = re.sub(r'console\.log\(', 'console.debug(', content)
                
                full_path.write_text(content, encoding='utf-8')
                print(f"✅ Fixed console statements in {file_path}")
                
    def fix_function_returns(self):
        """Fix missing return statements where actually needed"""
        
        # Fix the cloudpepper_clean_fix.js function
        file_path = self.module_path / 'static/src/js/cloudpepper_clean_fix.js'
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            
            # The ensureDOMContentLoaded function doesn't need a return
            # but we can add one for consistency
            content = re.sub(
                r'(function ensureDOMContentLoaded\(\) \{[^}]+)(\s*}))',
                r'\1        // Function completed successfully\2',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            file_path.write_text(content, encoding='utf-8')
            print("✅ Fixed function structure in cloudpepper_clean_fix.js")
            
def main():
    module_path = Path("account_payment_final")
    
    fixer = FinalJSFixes(module_path)
    fixer.apply_final_fixes()
    
if __name__ == "__main__":
    main()
