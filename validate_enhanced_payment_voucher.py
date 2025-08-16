#!/usr/bin/env python3
"""
Enhanced Payment Voucher Template Validation Script
===================================================

This script validates the enhanced payment voucher template for account_payment_final module.
It checks for:
1. Template syntax validation
2. Field references validation
3. CSS/styling validation
4. Print optimization compliance
5. Single-page layout verification

Author: OSUS Properties Development Team
Date: August 2025
"""

import os
import sys
import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def validate_xml_syntax(file_path):
    """Validate XML syntax of the enhanced template"""
    print_info(f"Validating XML syntax: {file_path}")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        print_success("XML syntax is valid")
        return True, root
    except ET.ParseError as e:
        print_error(f"XML syntax error: {e}")
        return False, None
    except Exception as e:
        print_error(f"Error parsing XML: {e}")
        return False, None

def validate_template_structure(root):
    """Validate the template structure and required elements"""
    print_info("Validating template structure...")
    
    # Check for required template ID
    templates = root.findall(".//template[@id='payment_voucher_enhanced']")
    if not templates:
        print_error("Enhanced payment voucher template not found")
        return False
    
    template = templates[0]
    print_success("Enhanced template found")
    
    # Check for required CSS styles
    styles = template.findall(".//style")
    if not styles:
        print_error("No CSS styles found in template")
        return False
    
    style_content = styles[0].text
    
    # Check for enhanced typography
    required_styles = [
        'font-size: 16px',  # Base font size increase
        'font-size: 28px',  # Header title size
        'grid-template-columns: 35% 35% 30%',  # 3-column layout
        'grid-template-columns: 1fr 1fr',  # 2x2 signature grid
        'height: 80px',  # Compact signature boxes
    ]
    
    for style in required_styles:
        if style not in style_content:
            print_warning(f"Missing required style: {style}")
        else:
            print_success(f"Found required style: {style}")
    
    # Check for responsive design
    if '@media print' in style_content:
        print_success("Print media queries found")
    else:
        print_warning("Print media queries not found")
    
    return True

def validate_field_references(root):
    """Validate that all field references exist in the model"""
    print_info("Validating field references...")
    
    # Known fields in account.payment model for account_payment_final
    valid_fields = [
        'name', 'date', 'amount', 'currency_id', 'partner_id', 'journal_id',
        'payment_type', 'state', 'memo', 'ref', 'qr_code', 'voucher_number',
        'create_uid', 'create_date', 'write_uid', 'reviewer_id', 'reviewer_date',
        'approver_id', 'approver_date', 'authorizer_id', 'authorizer_date',
        'company_id'
    ]
    
    # Extract all t-field references
    template_content = ET.tostring(root, encoding='unicode')
    field_refs = re.findall(r't-field="([^"]+)"', template_content)
    
    invalid_fields = []
    for field_ref in field_refs:
        # Extract the field name (e.g., 'o.partner_id.name' -> 'partner_id')
        if '.' in field_ref and field_ref.startswith('o.'):
            field_parts = field_ref.replace('o.', '').split('.')
            base_field = field_parts[0]
            
            if base_field not in valid_fields:
                invalid_fields.append(field_ref)
            else:
                print_success(f"Valid field reference: {field_ref}")
    
    if invalid_fields:
        for field in invalid_fields:
            print_error(f"Invalid field reference: {field}")
        return False
    else:
        print_success("All field references are valid")
        return True

def validate_single_page_optimization(root):
    """Validate single-page optimization features"""
    print_info("Validating single-page optimization...")
    
    template_content = ET.tostring(root, encoding='unicode')
    
    # Check for space optimization features
    optimizations = [
        ('Compact margins', 'margin: 15mm'),
        ('Reduced padding', 'padding: 15px'),
        ('Compact signature height', 'height: 80px'),
        ('Smaller QR code', 'width: 60px; height: 60px'),
        ('Efficient grid layout', 'grid-template-columns: 35% 35% 30%'),
        ('Optimized font sizes', 'font-size: 16px'),
    ]
    
    found_optimizations = 0
    for name, pattern in optimizations:
        if pattern in template_content:
            print_success(f"{name}: Found")
            found_optimizations += 1
        else:
            print_warning(f"{name}: Not found")
    
    if found_optimizations >= 4:
        print_success(f"Single-page optimization: {found_optimizations}/{len(optimizations)} features found")
        return True
    else:
        print_warning(f"Single-page optimization: Only {found_optimizations}/{len(optimizations)} features found")
        return False

def validate_signature_sections(root):
    """Validate the 4-signature section implementation"""
    print_info("Validating signature sections...")
    
    template_content = ET.tostring(root, encoding='unicode')
    
    # Check for 4 signature sections
    signature_sections = [
        'Prepared By',
        'Reviewed By',
        'Approved By',
        'Received By'
    ]
    
    missing_signatures = []
    for signature in signature_sections:
        if signature not in template_content:
            missing_signatures.append(signature)
        else:
            print_success(f"Found signature section: {signature}")
    
    if missing_signatures:
        for sig in missing_signatures:
            print_error(f"Missing signature section: {sig}")
        return False
    
    # Check for signature grid layout
    if 'signature-grid' in template_content:
        print_success("Signature grid layout found")
    else:
        print_error("Signature grid layout not found")
        return False
    
    return len(missing_signatures) == 0

def validate_branding_compliance(root):
    """Validate OSUS branding compliance"""
    print_info("Validating OSUS branding compliance...")
    
    template_content = ET.tostring(root, encoding='unicode')
    
    # Check for OSUS brand colors
    brand_colors = ['#1f4788', '#2563eb']
    found_colors = 0
    
    for color in brand_colors:
        if color in template_content:
            print_success(f"Found OSUS brand color: {color}")
            found_colors += 1
        else:
            print_warning(f"OSUS brand color not found: {color}")
    
    # Check for OSUS references
    if 'OSUS Properties' in template_content:
        print_success("OSUS Properties branding found")
    else:
        print_warning("OSUS Properties branding not found")
    
    return found_colors >= 1

def main():
    """Main validation function"""
    print(f"{Colors.BOLD}Enhanced Payment Voucher Template Validation{Colors.ENDC}")
    print("=" * 55)
    
    # Get the template file path
    current_dir = Path(__file__).parent
    template_path = current_dir / "account_payment_final" / "views" / "payment_voucher_template_enhanced.xml"
    
    if not template_path.exists():
        print_error(f"Template file not found: {template_path}")
        sys.exit(1)
    
    # Run validations
    validations = []
    
    # 1. XML Syntax Validation
    valid_xml, root = validate_xml_syntax(template_path)
    validations.append(("XML Syntax", valid_xml))
    
    if not valid_xml:
        print_error("Cannot proceed with further validations due to XML syntax errors")
        sys.exit(1)
    
    # 2. Template Structure Validation
    valid_structure = validate_template_structure(root)
    validations.append(("Template Structure", valid_structure))
    
    # 3. Field References Validation
    valid_fields = validate_field_references(root)
    validations.append(("Field References", valid_fields))
    
    # 4. Single Page Optimization Validation
    valid_optimization = validate_single_page_optimization(root)
    validations.append(("Single Page Optimization", valid_optimization))
    
    # 5. Signature Sections Validation
    valid_signatures = validate_signature_sections(root)
    validations.append(("Signature Sections", valid_signatures))
    
    # 6. Branding Compliance Validation
    valid_branding = validate_branding_compliance(root)
    validations.append(("OSUS Branding", valid_branding))
    
    # Summary
    print("\n" + "=" * 55)
    print(f"{Colors.BOLD}Validation Summary{Colors.ENDC}")
    print("=" * 55)
    
    passed = 0
    total = len(validations)
    
    for name, result in validations:
        if result:
            print_success(f"{name}: PASSED")
            passed += 1
        else:
            print_error(f"{name}: FAILED")
    
    print("\n" + "=" * 55)
    if passed == total:
        print_success(f"All validations passed! ({passed}/{total})")
        print_info("Enhanced payment voucher template is ready for production!")
        sys.exit(0)
    else:
        print_error(f"Validation failed! ({passed}/{total} passed)")
        print_info("Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
