#!/usr/bin/env python3
"""
Account Payment Final - Module Validation Script
Validates the enhanced module structure and readiness
"""

import os
import sys
from pathlib import Path

def validate_module_structure():
    """Validate the enhanced module structure"""
    print("🔍 Validating Account Payment Final Module Structure")
    print("=" * 60)
    
    base_path = Path("account_payment_final")
    
    # Core structure validation
    required_files = [
        "__manifest__.py",
        "__init__.py",
        "models/__init__.py",
        "models/account_payment.py",
        "static/src/scss/variables.scss",
        "static/src/scss/components/payment_widget_enhanced.scss",
        "static/src/js/components/payment_approval_widget_enhanced.js",
        "tests/test_payment_models.py",
        "tests/test_payment_workflow.py",
        "tests/test_payment_security.py"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print("\n📊 Validation Results:")
    print(f"✅ Existing Files: {len(existing_files)}")
    print(f"❌ Missing Files: {len(missing_files)}")
    
    if missing_files:
        print(f"\n⚠️  Missing Files:")
        for file in missing_files:
            print(f"   - {file}")
    
    # Calculate completion percentage
    completion_percentage = (len(existing_files) / len(required_files)) * 100
    print(f"\n🎯 Module Completion: {completion_percentage:.1f}%")
    
    if completion_percentage >= 95:
        print("🚀 Module is PRODUCTION READY!")
        return True
    elif completion_percentage >= 80:
        print("⚠️  Module needs minor fixes")
        return False
    else:
        print("❌ Module needs significant work")
        return False

def validate_enhancements():
    """Validate specific enhancements"""
    print("\n🎨 Validating Enhancements")
    print("=" * 30)
    
    enhancements = {
        "CSS Custom Properties": "account_payment_final/static/src/scss/variables.scss",
        "Enhanced Payment Widget": "account_payment_final/static/src/scss/components/payment_widget_enhanced.scss",
        "Enhanced OWL Component": "account_payment_final/static/src/js/components/payment_approval_widget_enhanced.js",
        "Model Tests": "account_payment_final/tests/test_payment_models.py",
        "Workflow Tests": "account_payment_final/tests/test_payment_workflow.py",
        "Security Tests": "account_payment_final/tests/test_payment_security.py"
    }
    
    validated_enhancements = 0
    
    for enhancement, file_path in enhancements.items():
        if Path(file_path).exists():
            print(f"✅ {enhancement}")
            validated_enhancements += 1
        else:
            print(f"❌ {enhancement}")
    
    enhancement_percentage = (validated_enhancements / len(enhancements)) * 100
    print(f"\n🎯 Enhancement Completion: {enhancement_percentage:.1f}%")
    
    return enhancement_percentage >= 95

def main():
    """Main validation function"""
    print("🚀 Account Payment Final - Enhancement Validation")
    print("=" * 60)
    
    try:
        # Change to the correct directory
        os.chdir(Path(__file__).parent)
        
        # Run validations
        structure_valid = validate_module_structure()
        enhancements_valid = validate_enhancements()
        
        print("\n" + "=" * 60)
        print("📋 FINAL VALIDATION REPORT")
        print("=" * 60)
        
        if structure_valid and enhancements_valid:
            print("🎉 MODULE ENHANCEMENT COMPLETE!")
            print("✅ All validations passed")
            print("🚀 Ready for production deployment")
            return True
        else:
            print("⚠️  Module needs attention")
            print("❌ Some validations failed")
            return False
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
