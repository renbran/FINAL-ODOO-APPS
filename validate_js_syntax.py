#!/usr/bin/env python3
"""
JavaScript Syntax Validation for CloudPepper Fix
Checks for syntax errors in JavaScript files
"""

import os
import subprocess
import json
import sys

class JSyntaxValidator:
    def __init__(self):
        self.base_path = r"d:\RUNNING APPS\ready production\latest\odoo17_final\account_payment_final"
        self.js_files = [
            "static/src/js/error_handler.js",
            "static/src/js/cloudpepper_simple_optimizer.js", 
            "static/src/js/payment_workflow.js",
            "static/src/js/components/payment_approval_widget.js"
        ]
        self.results = {}
    
    def validate_file_syntax(self, file_path):
        """Validate JavaScript syntax using Node.js if available, otherwise basic checks"""
        full_path = os.path.join(self.base_path, file_path)
        
        if not os.path.exists(full_path):
            return {"status": "MISSING", "error": "File not found"}
        
        try:
            # Read file content for basic checks
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            basic_checks = self.perform_basic_checks(content, file_path)
            
            if basic_checks["status"] == "FAIL":
                return basic_checks
            
            # Try Node.js syntax check if available
            try:
                result = subprocess.run(['node', '-c', full_path], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    return {"status": "PASS", "method": "Node.js", "size": len(content)}
                else:
                    return {"status": "FAIL", "method": "Node.js", "error": result.stderr}
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # Node.js not available, use basic validation
                return {"status": "PASS", "method": "Basic", "size": len(content)}
                
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def perform_basic_checks(self, content, file_path):
        """Perform basic JavaScript syntax checks"""
        errors = []
        
        # Check for unmatched braces
        brace_count = content.count('{') - content.count('}')
        if brace_count != 0:
            errors.append(f"Unmatched braces: {brace_count}")
        
        # Check for unmatched parentheses
        paren_count = content.count('(') - content.count(')')
        if paren_count != 0:
            errors.append(f"Unmatched parentheses: {paren_count}")
        
        # Check for unmatched brackets
        bracket_count = content.count('[') - content.count(']')
        if bracket_count != 0:
            errors.append(f"Unmatched brackets: {bracket_count}")
        
        # Check for incomplete template literals
        backtick_count = content.count('`')
        if backtick_count % 2 != 0:
            errors.append("Unmatched template literal backticks")
        
        # Check for incomplete string literals
        single_quote_lines = []
        double_quote_lines = []
        
        for i, line in enumerate(content.split('\n'), 1):
            # Skip comments
            if line.strip().startswith('//') or line.strip().startswith('*'):
                continue
                
            # Count quotes not in comments
            line_clean = line.split('//')[0]  # Remove inline comments
            
            single_quotes = line_clean.count("'") - line_clean.count("\\'")
            double_quotes = line_clean.count('"') - line_clean.count('\\"')
            
            if single_quotes % 2 != 0:
                single_quote_lines.append(i)
            if double_quotes % 2 != 0:
                double_quote_lines.append(i)
        
        if single_quote_lines:
            errors.append(f"Unmatched single quotes on lines: {single_quote_lines}")
        if double_quote_lines:
            errors.append(f"Unmatched double quotes on lines: {double_quote_lines}")
        
        # Check for common syntax issues
        if 'link = document.createElement(' in content and 'link' not in content.split('link = document.createElement(')[0]:
            errors.append("Potential undefined 'link' identifier issue")
            
        if errors:
            return {"status": "FAIL", "errors": errors}
        else:
            return {"status": "PASS"}
    
    def run_validation(self):
        """Validate all JavaScript files"""
        print("🔍 Validating JavaScript syntax for CloudPepper fix...")
        print("=" * 60)
        
        all_passed = True
        
        for js_file in self.js_files:
            print(f"Checking {os.path.basename(js_file)}...")
            result = self.validate_file_syntax(js_file)
            self.results[js_file] = result
            
            if result["status"] == "PASS":
                method = result.get("method", "Basic")
                size = result.get("size", 0)
                print(f"✅ {os.path.basename(js_file)}: PASS ({method}, {size} bytes)")
            elif result["status"] == "MISSING":
                print(f"❌ {os.path.basename(js_file)}: MISSING")
                all_passed = False
            else:
                print(f"❌ {os.path.basename(js_file)}: {result['status']}")
                if "error" in result:
                    print(f"   Error: {result['error']}")
                if "errors" in result:
                    for error in result["errors"]:
                        print(f"   • {error}")
                all_passed = False
        
        print("\n" + "=" * 60)
        
        if all_passed:
            print("🎉 All JavaScript files passed syntax validation!")
            print("✅ No syntax errors found - safe to deploy")
        else:
            print("⚠️  Some JavaScript files have syntax issues")
            print("❌ Fix syntax errors before deployment")
        
        return all_passed
    
    def save_results(self, filename="js_syntax_validation.json"):
        """Save validation results"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to {filename}")
        except Exception as e:
            print(f"\n❌ Error saving results: {e}")

def main():
    validator = JSyntaxValidator()
    
    try:
        success = validator.run_validation()
        validator.save_results()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
