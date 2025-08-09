#!/usr/bin/env python3
"""
CloudPepper JavaScript Error Fix - File-Based Validation
Validates all components are in place without requiring running Odoo
"""

import os
import json
from datetime import datetime

class FileBasedValidator:
    def __init__(self):
        self.base_path = r"d:\RUNNING APPS\ready production\latest\odoo17_final\account_payment_final"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "file_based",
            "tests": {},
            "overall_status": "PENDING"
        }
    
    def check_file_exists(self, file_path, description=""):
        """Check if a file exists and return status"""
        full_path = os.path.join(self.base_path, file_path)
        exists = os.path.exists(full_path)
        if exists:
            try:
                size = os.path.getsize(full_path)
                return {"exists": True, "size": size, "description": description}
            except:
                return {"exists": True, "size": 0, "description": description}
        return {"exists": False, "size": 0, "description": description}
    
    def validate_javascript_files(self):
        """Validate all JavaScript files are in place"""
        print("🔍 Validating JavaScript files...")
        
        js_files = {
            "error_handler.js": "static/src/js/error_handler.js",
            "cloudpepper_optimizer_fixed.js": "static/src/js/cloudpepper_optimizer_fixed.js", 
            "cloudpepper_optimizer.js": "static/src/js/cloudpepper_optimizer.js",
            "payment_workflow.js": "static/src/js/payment_workflow.js",
            "payment_approval_widget.js": "static/src/js/components/payment_approval_widget.js"
        }
        
        js_results = {}
        all_present = True
        
        for name, path in js_files.items():
            result = self.check_file_exists(path, f"JavaScript: {name}")
            js_results[name] = result
            if not result["exists"]:
                all_present = False
                print(f"❌ Missing: {name}")
            else:
                print(f"✅ Found: {name} ({result['size']} bytes)")
        
        self.results["tests"]["javascript_files"] = {
            "status": "PASS" if all_present else "FAIL",
            "files": js_results,
            "total_files": len(js_files),
            "found_files": sum(1 for r in js_results.values() if r["exists"])
        }
        
        return all_present
    
    def validate_manifest_assets(self):
        """Validate manifest.py has correct asset configuration"""
        print("🔍 Validating __manifest__.py assets...")
        
        manifest_path = "__manifest__.py"
        result = self.check_file_exists(manifest_path, "Module manifest")
        
        if not result["exists"]:
            self.results["tests"]["manifest_assets"] = {
                "status": "FAIL",
                "error": "Manifest file not found"
            }
            print("❌ __manifest__.py not found")
            return False
        
        try:
            full_path = os.path.join(self.base_path, manifest_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required asset entries
            required_assets = [
                "error_handler.js",
                "cloudpepper_optimizer_fixed.js", 
                "web.assets_backend"
            ]
            
            missing_assets = []
            for asset in required_assets:
                if asset not in content:
                    missing_assets.append(asset)
            
            has_all_assets = len(missing_assets) == 0
            
            self.results["tests"]["manifest_assets"] = {
                "status": "PASS" if has_all_assets else "FAIL",
                "required_assets": required_assets,
                "missing_assets": missing_assets,
                "manifest_size": len(content)
            }
            
            if has_all_assets:
                print("✅ All required assets found in manifest")
            else:
                print(f"❌ Missing assets in manifest: {', '.join(missing_assets)}")
            
            return has_all_assets
            
        except Exception as e:
            self.results["tests"]["manifest_assets"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ Error reading manifest: {e}")
            return False
    
    def validate_assets_xml(self):
        """Validate assets.xml file structure"""
        print("🔍 Validating assets.xml...")
        
        assets_path = "views/assets.xml"
        result = self.check_file_exists(assets_path, "Assets XML file")
        
        if not result["exists"]:
            self.results["tests"]["assets_xml"] = {
                "status": "FAIL",
                "error": "Assets XML file not found"
            }
            print("❌ assets.xml not found")
            return False
        
        try:
            full_path = os.path.join(self.base_path, assets_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check XML structure
            has_odoo_tag = "<odoo>" in content
            has_data_tag = "<data>" in content
            has_xml_declaration = "<?xml" in content
            
            structure_valid = has_odoo_tag and has_data_tag and has_xml_declaration
            
            self.results["tests"]["assets_xml"] = {
                "status": "PASS" if structure_valid else "FAIL",
                "has_odoo_tag": has_odoo_tag,
                "has_data_tag": has_data_tag,
                "has_xml_declaration": has_xml_declaration,
                "file_size": len(content)
            }
            
            if structure_valid:
                print("✅ Assets XML structure is valid")
            else:
                print("❌ Assets XML structure is invalid")
            
            return structure_valid
            
        except Exception as e:
            self.results["tests"]["assets_xml"] = {
                "status": "ERROR", 
                "error": str(e)
            }
            print(f"❌ Error reading assets.xml: {e}")
            return False
    
    def validate_module_structure(self):
        """Validate overall module structure"""
        print("🔍 Validating module structure...")
        
        required_dirs = {
            "static/src/js": "JavaScript source directory",
            "views": "Views directory", 
            "security": "Security directory",
            "models": "Models directory"
        }
        
        dir_results = {}
        all_dirs_present = True
        
        for dir_name, description in required_dirs.items():
            full_path = os.path.join(self.base_path, dir_name)
            exists = os.path.isdir(full_path)
            dir_results[dir_name] = {"exists": exists, "description": description}
            
            if not exists:
                all_dirs_present = False
                print(f"❌ Missing directory: {dir_name}")
            else:
                print(f"✅ Found directory: {dir_name}")
        
        self.results["tests"]["module_structure"] = {
            "status": "PASS" if all_dirs_present else "FAIL",
            "directories": dir_results,
            "total_required": len(required_dirs),
            "found_dirs": sum(1 for r in dir_results.values() if r["exists"])
        }
        
        return all_dirs_present
    
    def run_validation(self):
        """Run all file-based validations"""
        print("🚀 Starting CloudPepper JavaScript Fix - File-Based Validation...")
        print("=" * 70)
        
        # Run all validation tests
        js_valid = self.validate_javascript_files()
        manifest_valid = self.validate_manifest_assets()
        assets_valid = self.validate_assets_xml()
        structure_valid = self.validate_module_structure()
        
        # Calculate overall status
        all_passed = js_valid and manifest_valid and assets_valid and structure_valid
        
        if all_passed:
            self.results["overall_status"] = "SUCCESS"
        else:
            self.results["overall_status"] = "PARTIAL"
        
        print("\n" + "=" * 70)
        print(f"🎯 Overall Status: {self.results['overall_status']}")
        
        return self.results
    
    def save_results(self, filename="file_validation_results.json"):
        """Save validation results to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"💾 Results saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def print_summary(self):
        """Print validation summary"""
        print("\n📊 Validation Summary:")
        for test_name, test_result in self.results["tests"].items():
            status = test_result.get("status", "UNKNOWN")
            status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"  {status_emoji} {test_name.replace('_', ' ').title()}: {status}")
        
        if self.results["overall_status"] == "SUCCESS":
            print("\n🎉 All file-based validations passed!")
            print("📝 JavaScript error fix components are properly installed")
            print("\n📋 Next Steps:")
            print("  1. Restart your Odoo instance")
            print("  2. Update the account_payment_final module")
            print("  3. Check browser console for reduced errors")
        else:
            print(f"\n⚠️ Validation completed with status: {self.results['overall_status']}")
            print("📝 Some components may need attention - check details above")

def main():
    """Main execution function"""
    validator = FileBasedValidator()
    
    try:
        results = validator.run_validation()
        validator.save_results()
        validator.print_summary()
        
        if results["overall_status"] == "SUCCESS":
            exit(0)
        else:
            exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
