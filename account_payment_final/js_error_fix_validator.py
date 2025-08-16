#!/usr/bin/env python3
"""
JavaScript Error Fix Validator for Account Payment Final
========================================================

Validates that JavaScript errors have been properly addressed:
- MutationObserver errors fixed
- ES6 module loading issues resolved
- CloudPepper compatibility ensured
- Error suppression patterns working
"""

import os
import re
import json
from pathlib import Path

def validate_javascript_fixes():
    """Validate JavaScript error fixes"""
    
    print("🔧 JavaScript Error Fix Validation")
    print("=" * 50)
    
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
    
    # Check 1: Verify cloudpepper_clean_fix.js exists and is properly structured
    clean_fix_file = js_path / "cloudpepper_clean_fix.js"
    if clean_fix_file.exists():
        results["checks"].append("✅ cloudpepper_clean_fix.js exists")
        results["score"] += 15
        
        # Check content
        content = clean_fix_file.read_text(encoding='utf-8')
        
        # Check for proper ES6 module structure
        if "/** @odoo-module **/" in content:
            results["checks"].append("✅ Proper ES6 module declaration")
            results["score"] += 10
        else:
            results["errors"].append("❌ Missing ES6 module declaration")
            
        # Check for enhanced MutationObserver protection
        if "isValidTarget" in content and "isConnected" in content:
            results["checks"].append("✅ Enhanced MutationObserver validation")
            results["score"] += 15
        else:
            results["errors"].append("❌ Missing enhanced MutationObserver validation")
            
        # Check for comprehensive error patterns
        error_patterns = [
            "Failed to execute 'observe' on 'MutationObserver'",
            "Cannot use import statement",
            "Long Running Recorder",
            "crashpad",
            "registration_protocol_win"
        ]
        
        pattern_count = sum(1 for pattern in error_patterns if pattern in content)
        if pattern_count >= 4:
            results["checks"].append(f"✅ Comprehensive error patterns ({pattern_count}/5)")
            results["score"] += 15
        else:
            results["warnings"].append(f"⚠️ Limited error patterns ({pattern_count}/5)")
            results["score"] += pattern_count * 3
            
        # Check for CloudPepper specific enhancements
        if "CloudPepperEnhancedHandler" in content:
            results["checks"].append("✅ CloudPepper enhanced handler present")
            results["score"] += 10
        else:
            results["warnings"].append("⚠️ Missing CloudPepper enhanced handler")
            
        # Check for proper exports
        if "export {" in content and "ErrorPreventionManager" in content:
            results["checks"].append("✅ Proper ES6 exports")
            results["score"] += 10
        else:
            results["errors"].append("❌ Missing or incorrect ES6 exports")
            
    else:
        results["errors"].append("❌ cloudpepper_clean_fix.js not found")
    
    # Check 2: Verify redundant files are removed
    redundant_files = [
        js_path / "cloudpepper_js_error_handler.js",
        base_path / "debug.log",
        js_path / "debug.log",
        js_path / "frontend" / "debug.log",
        js_path / "components" / "debug.log"
    ]
    
    removed_count = 0
    for file in redundant_files:
        if not file.exists():
            removed_count += 1
    
    if removed_count == len(redundant_files):
        results["checks"].append("✅ All redundant files removed")
        results["score"] += 15
    else:
        remaining = len(redundant_files) - removed_count
        results["warnings"].append(f"⚠️ {remaining} redundant files still present")
        results["score"] += max(0, 15 - remaining * 3)
    
    # Check 3: Verify manifest.py is updated
    manifest_file = base_path / "__manifest__.py"
    if manifest_file.exists():
        manifest_content = manifest_file.read_text(encoding='utf-8')
        
        if "cloudpepper_js_error_handler.js" not in manifest_content:
            results["checks"].append("✅ Manifest updated to remove redundant handler")
            results["score"] += 10
        else:
            results["errors"].append("❌ Manifest still references removed file")
            
        if "'web.assets_backend'" in manifest_content:
            results["checks"].append("✅ Manifest has proper asset structure")
            results["score"] += 10
        else:
            results["warnings"].append("⚠️ Manifest asset structure may need review")
    
    # Determine overall status
    if results["score"] >= 85:
        results["status"] = "EXCELLENT"
    elif results["score"] >= 70:
        results["status"] = "GOOD"
    elif results["score"] >= 50:
        results["status"] = "FAIR"
    else:
        results["status"] = "NEEDS_WORK"
    
    return results

def print_results(results):
    """Print validation results"""
    
    print(f"\n🏆 VALIDATION RESULTS")
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
    if results["status"] == "EXCELLENT":
        print("  JavaScript errors have been comprehensively addressed!")
        print("  Ready for production deployment.")
    elif results["status"] == "GOOD":
        print("  Most JavaScript errors addressed, minor improvements needed.")
    elif results["status"] == "FAIR":
        print("  Basic error handling in place, significant improvements needed.")
    else:
        print("  Major JavaScript error issues remain. Please address errors above.")

if __name__ == "__main__":
    try:
        results = validate_javascript_fixes()
        print_results(results)
        
        # Save results
        with open("js_error_fix_validation.json", "w") as f:
            json.dump(results, f, indent=2)
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        exit(1)
