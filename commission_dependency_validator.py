#!/usr/bin/env python3
"""
Commission Module Dependency Validator
Checks for field dependency issues in commission_ax module
"""

import ast
import os
import re
from pathlib import Path

class CommissionDependencyValidator:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def validate_field_dependencies(self, file_path):
        """Validate @depends decorators for field existence"""
        print(f"🔍 Validating dependencies in: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all @api.depends decorators
            depends_pattern = r'@api\.depends\((.*?)\)'
            depends_matches = re.findall(depends_pattern, content, re.DOTALL)
            
            for match in depends_matches:
                # Parse the dependencies
                dependencies = []
                try:
                    # Clean up the match to make it valid Python
                    clean_match = match.strip().replace('\n', '').replace(' ', '')
                    # Split by comma and clean up quotes
                    deps = [dep.strip().strip('\'"') for dep in clean_match.split(',')]
                    dependencies.extend(deps)
                except:
                    continue
                
                # Check each dependency
                for dep in dependencies:
                    if '.' in dep:
                        model_field, target_field = dep.split('.', 1)
                        self.check_field_existence(dep, model_field, target_field, file_path)
            
        except Exception as e:
            print(f"❌ Error validating {file_path}: {e}")
    
    def check_field_existence(self, full_dep, model_field, target_field, file_path):
        """Check if target field exists in the referenced model"""
        known_issues = [
            ('origin_so_id', 'project_id'),
            ('origin_so_id', 'unit_id'),
        ]
        
        if (model_field, target_field) in known_issues:
            issue = f"Invalid dependency '{full_dep}' in {os.path.basename(file_path)}"
            self.issues_found.append(issue)
            print(f"⚠️ Found issue: {issue}")
    
    def validate_commission_models(self):
        """Validate all commission module models"""
        print("🚀 COMMISSION MODULE DEPENDENCY VALIDATOR")
        print("=" * 50)
        
        commission_path = "commission_ax"
        if not os.path.exists(commission_path):
            print("❌ Commission module not found")
            return
        
        models_path = os.path.join(commission_path, "models")
        if not os.path.exists(models_path):
            print("❌ Models directory not found")
            return
        
        # Check all Python files in models
        for file in os.listdir(models_path):
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(models_path, file)
                self.validate_field_dependencies(file_path)
        
        # Report results
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   Issues found: {len(self.issues_found)}")
        
        if self.issues_found:
            print("\n⚠️ ISSUES DETECTED:")
            for issue in self.issues_found:
                print(f"   - {issue}")
        else:
            print("✅ No dependency issues found!")
    
    def validate_specific_patterns(self):
        """Validate specific problematic patterns"""
        print("\n🔍 CHECKING FOR SPECIFIC PATTERNS...")
        
        purchase_order_file = "commission_ax/models/purchase_order.py"
        if os.path.exists(purchase_order_file):
            with open(purchase_order_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for the specific problematic pattern
            if "origin_so_id.project_id" in content:
                if "@api.depends" in content and "origin_so_id.project_id" in content:
                    print("❌ Still found 'origin_so_id.project_id' in @depends decorator")
                else:
                    print("⚠️ Found 'origin_so_id.project_id' reference (but not in @depends)")
            else:
                print("✅ No 'origin_so_id.project_id' references in @depends")
            
            if "origin_so_id.unit_id" in content:
                if "@api.depends" in content and "origin_so_id.unit_id" in content:
                    print("❌ Still found 'origin_so_id.unit_id' in @depends decorator")
                else:
                    print("⚠️ Found 'origin_so_id.unit_id' reference (but not in @depends)")
            else:
                print("✅ No 'origin_so_id.unit_id' references in @depends")

if __name__ == "__main__":
    validator = CommissionDependencyValidator()
    validator.validate_commission_models()
    validator.validate_specific_patterns()
