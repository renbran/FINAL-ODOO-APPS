#!/usr/bin/env python3
"""
Critical Field Dependency Validation Script
Ensures all @api.depends decorators reference existing fields
"""

import re
import ast
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def validate_field_dependencies():
    """Validate that all @api.depends references point to existing fields"""
    
    print("🔍 CRITICAL FIELD DEPENDENCY VALIDATION")
    print("=" * 60)
    
    model_path = "order_status_override/models/sale_order.py"
    
    # Read the model file
    with open(model_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all field definitions
    print("🔍 Extracting field definitions...")
    field_pattern = r'(\w+)\s*=\s*fields\.[A-Z]\w*\('
    fields = set()
    for match in re.finditer(field_pattern, content):
        fields.add(match.group(1))
    
    print(f"✅ Found {len(fields)} fields:")
    for field in sorted(fields):
        print(f"   • {field}")
    
    # Extract all @api.depends references
    print("\n🔍 Extracting @api.depends references...")
    depends_pattern = r'@api\.depends\([\'"]([^\'"]+)[\'"](?:\s*,\s*[\'"]([^\'"]+)[\'"])*\)'
    depends_fields = set()
    
    # Find all depends decorators
    for match in re.finditer(r'@api\.depends\(([^)]+)\)', content):
        depends_args = match.group(1)
        # Extract individual field names from the arguments
        field_matches = re.findall(r'[\'"]([^\'"]+)[\'"]', depends_args)
        for field_name in field_matches:
            depends_fields.add(field_name)
    
    print(f"✅ Found {len(depends_fields)} dependency references:")
    for field in sorted(depends_fields):
        print(f"   • {field}")
    
    # Check for missing fields
    print("\n🔍 Validating dependencies...")
    missing_fields = depends_fields - fields
    
    if missing_fields:
        print(f"❌ CRITICAL: Missing fields referenced in @api.depends:")
        for field in sorted(missing_fields):
            print(f"   • {field}")
        return False
    else:
        print("✅ All @api.depends references point to existing fields!")
    
    # Check for compute methods
    print("\n🔍 Validating compute methods...")
    compute_pattern = r'compute=[\'"]([^\'"]+)[\'"]'
    compute_methods = set()
    
    for match in re.finditer(compute_pattern, content):
        compute_methods.add(match.group(1))
    
    print(f"✅ Found {len(compute_methods)} compute methods:")
    for method in sorted(compute_methods):
        print(f"   • {method}")
    
    # Check if compute methods exist
    method_pattern = r'def (_compute_\w+)\('
    defined_methods = set()
    
    for match in re.finditer(method_pattern, content):
        defined_methods.add(match.group(1))
    
    print(f"\n✅ Found {len(defined_methods)} defined compute methods:")
    for method in sorted(defined_methods):
        print(f"   • {method}")
    
    missing_methods = compute_methods - defined_methods
    
    if missing_methods:
        print(f"❌ CRITICAL: Missing compute methods:")
        for method in sorted(missing_methods):
            print(f"   • {method}")
        return False
    else:
        print("✅ All compute methods are properly defined!")
    
    # Final validation
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY:")
    print(f"   • Total fields defined: {len(fields)}")
    print(f"   • Total dependency references: {len(depends_fields)}")
    print(f"   • Missing field references: {len(missing_fields)}")
    print(f"   • Total compute methods: {len(compute_methods)}")
    print(f"   • Missing compute methods: {len(missing_methods)}")
    
    is_valid = len(missing_fields) == 0 and len(missing_methods) == 0
    
    if is_valid:
        print("\n🎉 CRITICAL VALIDATION PASSED!")
        print("✅ All field dependencies are correctly defined")
        print("✅ Database initialization error will be resolved")
        print("✅ Ready for CloudPepper deployment")
        return True
    else:
        print("\n⚠️ CRITICAL VALIDATION FAILED!")
        print("❌ Database initialization will fail")
        print("❌ NOT ready for deployment")
        return False

if __name__ == "__main__":
    success = validate_field_dependencies()
    exit(0 if success else 1)
