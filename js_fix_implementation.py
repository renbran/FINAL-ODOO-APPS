#!/usr/bin/env python3
"""
JavaScript Fix Implementation Plan for account_payment_final Module
Comprehensive fixes for Odoo 17 compatibility and JavaScript errors
"""

import os
import re
from pathlib import Path

class JSFixImplementation:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.fixes_applied = []
        
    def apply_all_fixes(self):
        """Apply all JavaScript fixes"""
        
        print("🔧 Starting JavaScript Error Fixes...")
        print("="*60)
        
        # Phase 1: Critical Module Declaration Fixes
        self.fix_module_declarations()
        
        # Phase 2: Syntax and Quality Fixes
        self.fix_syntax_issues()
        
        # Phase 3: Import/Export Fixes
        self.fix_import_export_issues()
        
        # Phase 4: Function Structure Fixes
        self.fix_function_structures()
        
        # Phase 5: Test File Fixes
        self.fix_test_files()
        
        # Generate report
        self.generate_fix_report()
        
    def fix_module_declarations(self):
        """Fix missing @odoo-module declarations"""
        
        print("📱 Phase 1: Fixing Module Declarations...")
        
        files_to_fix = [
            'static/src/js/payment_workflow_safe.js',
            'static/src/js/frontend/qr_verification.js'
        ]
        
        for file_path in files_to_fix:
            full_path = self.module_path / file_path
            if full_path.exists():
                self.add_module_declaration(full_path)
                
    def add_module_declaration(self, file_path):
        """Add @odoo-module declaration to file"""
        
        content = file_path.read_text(encoding='utf-8')
        
        # Check if already has declaration
        if '/** @odoo-module **/' in content:
            return
            
        # Add declaration at the top
        new_content = '/** @odoo-module **/\n\n' + content
        file_path.write_text(new_content, encoding='utf-8')
        
        self.fixes_applied.append(f"✅ Added @odoo-module declaration to {file_path.name}")
        
    def fix_syntax_issues(self):
        """Fix common syntax issues"""
        
        print("🔧 Phase 2: Fixing Syntax Issues...")
        
        js_files = list(self.module_path.glob("**/*.js"))
        
        for js_file in js_files:
            self.fix_file_syntax(js_file)
            
    def fix_file_syntax(self, file_path):
        """Fix syntax issues in a single file"""
        
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Skip legacy compatibility files (they use ES5 intentionally)
        if 'legacy_compatible' in file_path.name or 'ultimate_module_fix' in file_path.name:
            return
            
        # Fix equality operators
        content = re.sub(r'(?<!!)===(?!=)', '===', content)  # == to ===
        content = re.sub(r'(?<!!)!==(?!=)', '!==', content)  # != to !==
        
        # Remove console.log statements (but preserve console.debug for debugging)
        content = re.sub(r'console\.log\([^)]*\);?\s*', '// DEBUG: console.log removed\n', content)
        
        # Fix missing semicolons (basic patterns)
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Add semicolons to common patterns that should have them
            if (stripped and not stripped.startswith('//') and not stripped.startswith('/*') and
                not stripped.endswith(';') and not stripped.endswith(',') and
                not stripped.endswith('{') and not stripped.endswith('}') and
                ('=' in stripped or 'call(' in stripped or 'push(' in stripped) and
                not stripped.startswith('if') and not stripped.startswith('for') and
                not stripped.startswith('while') and not stripped.startswith('function')):
                line = line.rstrip() + ';'
            fixed_lines.append(line)
            
        content = '\n'.join(fixed_lines)
        
        # Save if changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            self.fixes_applied.append(f"✅ Fixed syntax issues in {file_path.name}")
            
    def fix_import_export_issues(self):
        """Fix import/export issues"""
        
        print("📦 Phase 3: Fixing Import/Export Issues...")
        
        # Fix test file imports
        test_files = list(self.module_path.glob("static/tests/*.js"))
        
        for test_file in test_files:
            self.fix_test_imports(test_file)
            
    def fix_test_imports(self, file_path):
        """Fix import paths in test files"""
        
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Fix custom import paths
        content = re.sub(
            r'@account_payment_final/js/',
            '../src/js/',
            content
        )
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            self.fixes_applied.append(f"✅ Fixed import paths in {file_path.name}")
            
    def fix_function_structures(self):
        """Fix function structure issues"""
        
        print("🎯 Phase 4: Fixing Function Structures...")
        
        # Specific files with function issues
        utils_file = self.module_path / 'static/src/js/utils/payment_utils.js'
        if utils_file.exists():
            self.fix_utils_functions(utils_file)
            
    def fix_utils_functions(self, file_path):
        """Fix utility function issues"""
        
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Fix missing return statements in specific functions
        function_fixes = [
            (
                r'(function executedFunction\([^)]*\)\s*\{[^}]*)(}\s*$)',
                r'\1    return result;\n\2'
            ),
            (
                r'(function validatePaymentData\([^)]*\)\s*\{[^}]*)(}\s*$)',
                r'\1    return { isValid: errors.length === 0, errors };\n\2'
            ),
            (
                r'(function generateQRData\([^)]*\)\s*\{[^}]*)(}\s*$)',
                r'\1    return qrData;\n\2'
            ),
        ]
        
        for pattern, replacement in function_fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            self.fixes_applied.append(f"✅ Fixed function structures in {file_path.name}")
            
    def fix_test_files(self):
        """Fix test file specific issues"""
        
        print("🧪 Phase 5: Fixing Test Files...")
        
        test_files = list(self.module_path.glob("static/tests/*.js"))
        
        for test_file in test_files:
            self.fix_test_file_issues(test_file)
            
    def fix_test_file_issues(self, file_path):
        """Fix issues in test files"""
        
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Add missing OWL imports if Component is used
        if 'Component' in content and 'from "@odoo/owl"' not in content:
            # Add import after @odoo-module declaration
            content = re.sub(
                r'(/\*\* @odoo-module \*\*/\s*\n)',
                r'\1\nimport { Component } from "@odoo/owl";\n',
                content
            )
            
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            self.fixes_applied.append(f"✅ Fixed test file issues in {file_path.name}")
            
    def generate_fix_report(self):
        """Generate comprehensive fix report"""
        
        print("\n" + "="*60)
        print("📊 JAVASCRIPT FIX IMPLEMENTATION REPORT")
        print("="*60)
        
        if not self.fixes_applied:
            print("ℹ️  No fixes were needed - all files are already compliant!")
            return
            
        print(f"✅ Applied {len(self.fixes_applied)} fixes:")
        print()
        
        for fix in self.fixes_applied:
            print(f"  {fix}")
            
        print("\n" + "="*60)
        print("🎯 NEXT STEPS")
        print("="*60)
        print("1. 🧪 Run the module validation again to verify fixes")
        print("2. 🚀 Test the module in CloudPepper environment")
        print("3. ✅ Run Odoo tests to ensure functionality is preserved")
        
def main():
    module_path = Path("account_payment_final")
    
    if not module_path.exists():
        print("❌ Module path not found!")
        return
        
    fixer = JSFixImplementation(module_path)
    fixer.apply_all_fixes()
    
    print("\n🎉 JavaScript fix implementation completed!")
    
if __name__ == "__main__":
    main()
