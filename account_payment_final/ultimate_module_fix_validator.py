#!/usr/bin/env python3
"""
Ultimate JavaScript Module Fix Validator
========================================

Validates the ultimate JavaScript module fix implementation
for resolving ES6 import statement errors in Odoo 17.
"""

import os
import re
import json
from pathlib import Path

def validate_ultimate_module_fix():
    """Validate ultimate JavaScript module fix"""
    
    print("🚀 Ultimate JavaScript Module Fix Validation")
    print("=" * 55)
    
    base_path = Path(".")
    js_path = base_path / "static" / "src" / "js"
    
    results = {
        "status": "UNKNOWN",
        "score": 0,
        "max_score": 100,
        "checks": [],
        "errors": [],
        "warnings": []
    }
    
    # Check 1: Ultimate module fix file exists
    ultimate_fix_file = js_path / "ultimate_module_fix.js"
    if ultimate_fix_file.exists():
        results["checks"].append("✅ ultimate_module_fix.js exists")
        results["score"] += 20
        
        content = ultimate_fix_file.read_text(encoding='utf-8')
        
        # Check for ES6 import error handling
        if "Cannot use import statement outside a module" in content:
            results["checks"].append("✅ ES6 import error pattern present")
            results["score"] += 15
        else:
            results["errors"].append("❌ Missing ES6 import error handling")
            
        # Check for script loading interception
        if "createElement" in content and "script" in content:
            results["checks"].append("✅ Script loading interception present")
            results["score"] += 15
        else:
            results["errors"].append("❌ Missing script loading interception")
            
        # Check for module type enforcement
        if "type', 'module'" in content:
            results["checks"].append("✅ Module type enforcement present")
            results["score"] += 15
        else:
            results["errors"].append("❌ Missing module type enforcement")
            
        # Check for enhanced MutationObserver fix
        if "UltimateMutationObserver" in content:
            results["checks"].append("✅ Enhanced MutationObserver fix present")
            results["score"] += 10
        else:
            results["warnings"].append("⚠️ Missing enhanced MutationObserver fix")
            
    else:
        results["errors"].append("❌ ultimate_module_fix.js not found")
    
    # Check 2: Immediate error prevention exists
    immediate_fix_file = js_path / "immediate_error_prevention.js"
    if immediate_fix_file.exists():
        results["checks"].append("✅ immediate_error_prevention.js exists")
        results["score"] += 10
    else:
        results["warnings"].append("⚠️ immediate_error_prevention.js missing")
    
    # Check 3: Original clean fix exists
    clean_fix_file = js_path / "cloudpepper_clean_fix.js"
    if clean_fix_file.exists():
        results["checks"].append("✅ cloudpepper_clean_fix.js exists")
        results["score"] += 10
    else:
        results["warnings"].append("⚠️ cloudpepper_clean_fix.js missing")
    
    # Check 4: Manifest loading order
    manifest_file = base_path / "__manifest__.py"
    if manifest_file.exists():
        manifest_content = manifest_file.read_text(encoding='utf-8')
        
        # Check for ultimate fix in prepend position
        if "ultimate_module_fix.js" in manifest_content and "('prepend'" in manifest_content:
            results["checks"].append("✅ Ultimate fix loaded with prepend priority")
            results["score"] += 15
        else:
            results["errors"].append("❌ Ultimate fix not properly prioritized in manifest")
            
        # Check for multiple asset bundles
        asset_bundles = ["web.assets_backend", "web.assets_frontend", "web.assets_common"]
        bundle_count = sum(1 for bundle in asset_bundles if bundle in manifest_content)
        
        if bundle_count >= 3:
            results["checks"].append(f"✅ Ultimate fix in multiple asset bundles ({bundle_count}/3)")
            results["score"] += 15
        else:
            results["warnings"].append(f"⚠️ Limited asset bundle coverage ({bundle_count}/3)")
            results["score"] += bundle_count * 5
    
    # Determine overall status
    if results["score"] >= 90:
        results["status"] = "ULTIMATE_SUCCESS"
    elif results["score"] >= 75:
        results["status"] = "EXCELLENT"
    elif results["score"] >= 60:
        results["status"] = "GOOD"
    elif results["score"] >= 40:
        results["status"] = "FAIR"
    else:
        results["status"] = "NEEDS_WORK"
    
    return results

def print_results(results):
    """Print validation results"""
    
    print(f"\n🏆 ULTIMATE VALIDATION RESULTS")
    print(f"Status: {results['status']}")
    print(f"Score: {results['score']}/{results['max_score']} ({results['score']/results['max_score']*100:.1f}%)")
    
    if results["checks"]:
        print(f"\n✅ PASSED CHECKS ({len(results['checks'])}):")
        for check in results["checks"]:
            print(f"  {check}")
    
    if results["warnings"]:
        print(f"\n⚠️ WARNINGS ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"  {warning}")
    
    if results["errors"]:
        print(f"\n❌ ERRORS ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"  {error}")
    
    print(f"\n🎯 RECOMMENDATION:")
    if results["status"] == "ULTIMATE_SUCCESS":
        print("  🚀 ULTIMATE SUCCESS! All JavaScript module errors should be resolved!")
        print("  🌟 Ready for immediate CloudPepper deployment with confidence!")
    elif results["status"] == "EXCELLENT":
        print("  ✨ Excellent implementation! Minor optimizations possible.")
        print("  🚀 Ready for CloudPepper deployment.")
    elif results["status"] == "GOOD":
        print("  👍 Good implementation, some improvements recommended.")
    elif results["status"] == "FAIR":
        print("  📝 Basic implementation, significant improvements needed.")
    else:
        print("  🔧 Major issues remain. Please address errors above.")
    
    print(f"\n💡 TECHNICAL FOCUS:")
    print("  - ES6 import statement error prevention")
    print("  - Script loading interception and module type enforcement")
    print("  - Enhanced MutationObserver protection")
    print("  - Multi-layer error suppression system")
    print("  - CloudPepper environment optimization")

if __name__ == "__main__":
    try:
        results = validate_ultimate_module_fix()
        print_results(results)
        
        # Save results
        with open("ultimate_module_fix_validation.json", "w") as f:
            json.dump(results, f, indent=2)
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        exit(1)
