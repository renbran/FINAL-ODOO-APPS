#!/usr/bin/env python3
"""
Commission AX CloudPepper Emergency Deployment Fix
Validates and fixes critical deployment issues for CloudPepper
"""

import os
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_security_files():
    """Validate security files for CloudPepper deployment"""
    print("🔧 Validating Commission AX Security Files...")
    
    # Check ir.model.access.csv
    csv_file = Path("commission_ax/security/ir.model.access.csv")
    if not csv_file.exists():
        print("❌ ir.model.access.csv not found!")
        return False
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) < 2:
                print("❌ ir.model.access.csv has insufficient data")
                return False
            print(f"✅ ir.model.access.csv validated - {len(rows)-1} access rules")
    except Exception as e:
        print(f"❌ Error reading ir.model.access.csv: {e}")
        return False
    
    # Check security.xml
    xml_file = Path("commission_ax/security/security.xml")
    if not xml_file.exists():
        print("❌ security.xml not found!")
        return False
    
    try:
        ET.parse(xml_file)
        print("✅ security.xml validated")
    except Exception as e:
        print(f"❌ Error parsing security.xml: {e}")
        return False
    
    return True

def validate_manifest():
    """Validate manifest file"""
    print("\n🔧 Validating Commission AX Manifest...")
    
    manifest_file = Path("commission_ax/__manifest__.py")
    if not manifest_file.exists():
        print("❌ __manifest__.py not found!")
        return False
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if security files are referenced
        if 'security/ir.model.access.csv' not in content:
            print("❌ ir.model.access.csv not referenced in manifest")
            return False
            
        if 'security/security.xml' not in content:
            print("❌ security.xml not referenced in manifest")
            return False
            
        print("✅ Manifest validated - security files properly referenced")
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def check_model_definition():
    """Check if commission.ax model is properly defined"""
    print("\n🔧 Validating Commission AX Model Definition...")
    
    model_file = Path("commission_ax/models/commission_ax.py")
    if not model_file.exists():
        print("❌ commission_ax.py model file not found!")
        return False
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "_name = 'commission.ax'" not in content:
            print("❌ commission.ax model not properly defined")
            return False
            
        print("✅ Commission AX model properly defined")
        return True
        
    except Exception as e:
        print(f"❌ Error reading model file: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Commission AX CloudPepper Deployment Validation")
    print("=" * 55)
    
    os.chdir(Path(__file__).parent)
    
    all_valid = True
    
    # Run validations
    if not validate_security_files():
        all_valid = False
    
    if not validate_manifest():
        all_valid = False
        
    if not check_model_definition():
        all_valid = False
    
    print("\n" + "=" * 55)
    if all_valid:
        print("🎉 ALL VALIDATIONS PASSED - READY FOR CLOUDPEPPER DEPLOYMENT!")
        print("✅ Security files validated")
        print("✅ Manifest configuration correct")
        print("✅ Model definition verified")
        print("\n🚀 Deploy commission_ax module to CloudPepper now!")
    else:
        print("❌ VALIDATION FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        print("🔧 Address the errors above before proceeding")
    
    return all_valid

if __name__ == "__main__":
    main()
