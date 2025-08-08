#!/usr/bin/env python3
"""
OSUS Payment Module Production Readiness Test
Comprehensive validation for CloudPepper deployment
"""
import os
import sys
import importlib.util
from pathlib import Path

def test_manifest():
    """Test manifest file structure and content"""
    print("Testing manifest file...")
    manifest_path = Path("account_payment_final") / "__manifest__.py"
    
    if not manifest_path.exists():
        return False, "Manifest file not found"
    
    try:
        # Load manifest as a module
        spec = importlib.util.spec_from_file_location("manifest", manifest_path)
        manifest_module = importlib.util.module_from_spec(spec)
        
        # Execute the manifest file to get the dictionary
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        # Check if it's a valid Python dictionary
        manifest_dict = eval(manifest_content)
        
        # Check required keys
        required_keys = ['name', 'version', 'depends', 'data']
        for key in required_keys:
            if key not in manifest_dict:
                return False, f"Missing required key: {key}"
        
        # Check dependencies
        if not isinstance(manifest_dict['depends'], list):
            return False, "Dependencies must be a list"
        
        # Check data files exist
        for data_file in manifest_dict['data']:
            file_path = Path("account_payment_final") / data_file
            if not file_path.exists():
                return False, f"Data file not found: {data_file}"
        
        return True, "Manifest validation passed"
    
    except Exception as e:
        return False, f"Manifest error: {str(e)}"

def test_python_imports():
    """Test Python file imports and syntax"""
    print("Testing Python file imports...")
    
    python_files = [
        "account_payment_final/models/__init__.py",
        "account_payment_final/models/account_payment.py", 
        "account_payment_final/models/res_company.py",
        "account_payment_final/models/res_config_settings.py",
        "account_payment_final/__init__.py"
    ]
    
    for file_path in python_files:
        if not Path(file_path).exists():
            return False, f"Python file not found: {file_path}"
        
        try:
            # Compile the file to check syntax
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
        except Exception as e:
            return False, f"Python syntax error in {file_path}: {str(e)}"
    
    return True, "All Python files are valid"

def test_security_files():
    """Test security files exist and are properly formatted"""
    print("Testing security files...")
    
    security_files = [
        "account_payment_final/security/payment_security.xml",
        "account_payment_final/security/ir.model.access.csv"
    ]
    
    for file_path in security_files:
        if not Path(file_path).exists():
            return False, f"Security file not found: {file_path}"
    
    # Check CSV format
    csv_path = Path("account_payment_final/security/ir.model.access.csv")
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:  # At least header + one data line
                return False, "Access CSV file appears empty"
            
            # Check header format
            header = lines[0].strip()
            required_columns = ['id', 'name', 'model_id:id', 'group_id:id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink']
            for col in required_columns:
                if col not in header:
                    return False, f"Missing column in access CSV: {col}"
    
    except Exception as e:
        return False, f"CSV validation error: {str(e)}"
    
    return True, "Security files validation passed"

def test_required_dependencies():
    """Test if required external dependencies are available"""
    print("Testing external dependencies...")
    
    try:
        import qrcode
        import PIL
        return True, "External dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {str(e)}"

def test_view_references():
    """Test if view references are correct"""
    print("Testing view and template references...")
    
    # Check that report template exists
    template_path = Path("account_payment_final/reports/payment_voucher_template.xml")
    if not template_path.exists():
        return False, "Payment voucher template not found"
    
    # Check action references
    action_path = Path("account_payment_final/reports/payment_voucher_actions.xml")
    if not action_path.exists():
        return False, "Payment voucher actions not found"
    
    try:
        with open(action_path, 'r') as f:
            content = f.read()
            # Check for correct template reference
            if "report_payment_voucher_osus" not in content:
                return False, "Incorrect template reference in actions"
    
    except Exception as e:
        return False, f"View reference error: {str(e)}"
    
    return True, "View references validation passed"

def main():
    """Main test function"""
    print("OSUS Payment Module - Production Readiness Test")
    print("=" * 55)
    print()
    
    tests = [
        ("Manifest File", test_manifest),
        ("Python Files", test_python_imports), 
        ("Security Files", test_security_files),
        ("External Dependencies", test_required_dependencies),
        ("View References", test_view_references)
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            status = "✓ PASS" if passed else "✗ FAIL"
            results.append((test_name, status, message))
            
            if not passed:
                all_passed = False
        
        except Exception as e:
            results.append((test_name, "✗ ERROR", str(e)))
            all_passed = False
    
    # Print results
    print("\nTest Results:")
    print("-" * 55)
    for test_name, status, message in results:
        print(f"{status}: {test_name}")
        if "FAIL" in status or "ERROR" in status:
            print(f"    → {message}")
    
    print("-" * 55)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Module is ready for production!")
        print("\nNext steps:")
        print("1. Install/Update the module in CloudPepper")
        print("2. Test the approval workflow")
        print("3. Verify QR code generation")
        print("4. Test report generation")
    else:
        print("❌ Some tests failed - Please fix the issues before deployment")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
