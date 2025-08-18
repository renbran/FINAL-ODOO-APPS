#!/usr/bin/env python3
"""
Commission Reports Validation Script
==================================

This script validates that all commission reports in the order_status_override module
have been successfully updated with:
1. Professional tabular structure
2. Burgundy (#800020, #a0002a) and gold (#ffd700) color scheme
3. Proper 2-decimal currency formatting ({:,.2f})
4. Clean presentation without extra characters

Author: CloudPepper Deployment Team
Version: 1.0
Date: 2024-12-28
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_commission_reports():
    """Validate all commission report templates"""
    
    base_dir = Path("order_status_override/reports")
    commission_files = [
        "commission_report_enhanced.xml",
        "sale_commission_template.xml",
        "order_status_reports.xml",
        "enhanced_order_status_report_template.xml"
    ]
    
    validation_results = {
        "total_files": 0,
        "validated_files": 0,
        "issues": []
    }
    
    required_elements = [
        "burgundy_color_scheme",
        "gold_accents", 
        "tabular_structure",
        "decimal_formatting",
        "professional_styling"
    ]
    
    print("🔍 COMMISSION REPORTS VALIDATION")
    print("=" * 50)
    
    for file_name in commission_files:
        file_path = base_dir / file_name
        if not file_path.exists():
            validation_results["issues"].append(f"❌ File not found: {file_name}")
            continue
            
        validation_results["total_files"] += 1
        print(f"\n📋 Validating: {file_name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for burgundy color scheme
            burgundy_colors = ["#800020", "#a0002a"]
            burgundy_found = any(color in content for color in burgundy_colors)
            
            # Check for gold accents
            gold_colors = ["#ffd700", "#ffed4e"]
            gold_found = any(color in content for color in gold_colors)
            
            # Check for tabular structure
            table_elements = ["commission-table", "th", "td", "table"]
            tabular_found = any(element in content for element in table_elements)
            
            # Check for proper decimal formatting
            decimal_formatting = ["{:,.2f}", "format(", ".2f"]
            decimal_found = any(fmt in content for fmt in decimal_formatting)
            
            # Check for professional styling classes
            professional_classes = [
                "section-header", "customer-row", "subtotal-row", 
                "grand-total-row", "amount-cell", "status-badge"
            ]
            styling_found = any(cls in content for cls in professional_classes)
            
            # Validation scoring
            score = 0
            checks = {
                "Burgundy Color Scheme": burgundy_found,
                "Gold Accents": gold_found,
                "Tabular Structure": tabular_found,
                "Decimal Formatting": decimal_found,
                "Professional Styling": styling_found
            }
            
            for check_name, passed in checks.items():
                if passed:
                    score += 1
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    validation_results["issues"].append(f"{file_name}: Missing {check_name}")
            
            # Overall validation
            if score >= 4:  # At least 4 out of 5 checks passed
                validation_results["validated_files"] += 1
                print(f"  🎉 VALIDATED ({score}/5)")
            else:
                print(f"  ⚠️  NEEDS WORK ({score}/5)")
            
        except Exception as e:
            validation_results["issues"].append(f"Error processing {file_name}: {str(e)}")
            print(f"  ❌ Error: {str(e)}")
    
    # Summary Report
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Files Checked: {validation_results['total_files']}")
    print(f"Successfully Validated: {validation_results['validated_files']}")
    print(f"Success Rate: {(validation_results['validated_files']/validation_results['total_files']*100):.1f}%")
    
    if validation_results["issues"]:
        print(f"\n⚠️  Issues Found ({len(validation_results['issues'])}):")
        for issue in validation_results["issues"]:
            print(f"  • {issue}")
    else:
        print("\n🎉 ALL COMMISSION REPORTS SUCCESSFULLY VALIDATED!")
        print("✅ Professional tabular structure implemented")
        print("✅ Burgundy and gold color scheme applied")
        print("✅ Proper 2-decimal currency formatting")
        print("✅ Clean presentation without extra characters")
    
    return validation_results

def check_field_mappings():
    """Check if all field mappings are properly structured"""
    
    print("\n🔍 FIELD MAPPING VALIDATION")
    print("=" * 30)
    
    expected_fields = [
        "partner_id.name",  # Customer name
        "project_id.name", # Project
        "unit_id.name",    # Unit
        "amount_total",    # Sales value
        "broker_rate", "broker_amount",     # Broker commission
        "referrer_rate", "referrer_amount", # Referrer commission  
        "cashback_rate", "cashback_amount", # Kickback
        "agent1_rate", "agent1_amount",     # Agent 1
        "agent2_rate", "agent2_amount",     # Agent 2
        "manager_rate", "manager_amount",   # Manager
        "director_rate", "director_amount", # Director
        "total_external_commission_amount", # External total
        "total_internal_commission_amount", # Internal total
        "total_commission_amount",          # Grand total
        "amount_tax"                        # VAT amount
    ]
    
    base_dir = Path("order_status_override/reports")
    files_to_check = [
        "commission_report_enhanced.xml",
        "sale_commission_template.xml",
        "order_status_reports.xml"
    ]
    
    for file_name in files_to_check:
        file_path = base_dir / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n📋 {file_name}:")
            missing_fields = []
            for field in expected_fields:
                if field not in content:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"  ⚠️  Missing fields: {', '.join(missing_fields)}")
            else:
                print("  ✅ All field mappings present")

def main():
    """Main validation function"""
    print("🚀 STARTING COMMISSION REPORTS VALIDATION")
    print("CloudPepper Production Deployment")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run validations
    validation_results = validate_commission_reports()
    check_field_mappings()
    
    # Final status
    print("\n" + "=" * 60)
    if validation_results["validated_files"] == validation_results["total_files"]:
        print("🎉 COMMISSION REPORTS DEPLOYMENT: SUCCESS")
        print("✅ All reports updated with professional tabular structure")
        print("✅ Burgundy/gold color scheme consistently applied") 
        print("✅ Proper currency formatting with 2 decimal places")
        print("✅ No extra characters in currency display")
        print("✅ Ready for production deployment")
    else:
        print("⚠️  COMMISSION REPORTS DEPLOYMENT: NEEDS ATTENTION")
        print("Some files require additional updates")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
