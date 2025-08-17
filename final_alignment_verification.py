#!/usr/bin/env python3
"""
Final Alignment Verification Script
Ensures complete view-model compatibility for CloudPepper deployment
"""

import os
import ast
import xml.etree.ElementTree as ET
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_sale_order_alignment():
    """Check alignment between sale_order model and views"""
    
    print("🔍 FINAL ALIGNMENT VERIFICATION")
    print("=" * 60)
    
    # Paths
    model_path = "order_status_override/models/sale_order.py"
    view_path = "order_status_override/views/order_views_assignment.xml"
    
    # Check if files exist
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
        
    if not os.path.exists(view_path):
        print(f"❌ View file not found: {view_path}")
        return False
    
    # Extract action methods from model
    print("🔍 Extracting action methods from model...")
    with open(model_path, 'r', encoding='utf-8') as f:
        model_content = f.read()
    
    # Find all action methods using regex
    action_methods = set()
    for match in re.finditer(r'def (action_[a-zA-Z_]+)\(', model_content):
        action_methods.add(match.group(1))
    
    print(f"✅ Found {len(action_methods)} action methods in model:")
    for method in sorted(action_methods):
        print(f"   • {method}")
    
    # Extract referenced action methods from view
    print("\n🔍 Extracting action references from view...")
    with open(view_path, 'r', encoding='utf-8') as f:
        view_content = f.read()
    
    # Find all action references using regex
    view_actions = set()
    for match in re.finditer(r'name="(action_[a-zA-Z_]+)"', view_content):
        view_actions.add(match.group(1))
    
    print(f"✅ Found {len(view_actions)} action references in view:")
    for action in sorted(view_actions):
        print(f"   • {action}")
    
    # Check for missing methods
    print("\n🔍 Checking alignment...")
    missing_methods = view_actions - action_methods
    extra_methods = action_methods - view_actions
    
    if missing_methods:
        print(f"❌ Missing action methods in model:")
        for method in sorted(missing_methods):
            print(f"   • {method}")
    else:
        print("✅ All view action references have corresponding model methods")
    
    if extra_methods:
        print(f"ℹ️ Extra action methods in model (not referenced in views):")
        for method in sorted(extra_methods):
            print(f"   • {method}")
    
    # Extract computed fields from model
    print("\n🔍 Extracting computed fields from model...")
    computed_fields = set()
    for match in re.finditer(r'(\w+)\s*=\s*fields\.[A-Z]\w*\([^)]*compute=', model_content):
        computed_fields.add(match.group(1))
    
    print(f"✅ Found {len(computed_fields)} computed fields in model:")
    for field in sorted(computed_fields):
        print(f"   • {field}")
    
    # Extract field references from view
    print("\n🔍 Extracting field references from view...")
    view_fields = set()
    for match in re.finditer(r'invisible="not ([a-zA-Z_]+)"', view_content):
        view_fields.add(match.group(1))
    
    print(f"✅ Found {len(view_fields)} field references in view:")
    for field in sorted(view_fields):
        print(f"   • {field}")
    
    # Check field alignment
    print("\n🔍 Checking field alignment...")
    missing_fields = view_fields - computed_fields
    
    if missing_fields:
        print(f"❌ Missing computed fields in model:")
        for field in sorted(missing_fields):
            print(f"   • {field}")
    else:
        print("✅ All view field references have corresponding computed fields")
    
    # Overall result
    print("\n" + "=" * 60)
    print("📊 ALIGNMENT SUMMARY:")
    print(f"   • Action methods in model: {len(action_methods)}")
    print(f"   • Action references in view: {len(view_actions)}")
    print(f"   • Missing action methods: {len(missing_methods)}")
    print(f"   • Computed fields in model: {len(computed_fields)}")
    print(f"   • Field references in view: {len(view_fields)}")
    print(f"   • Missing computed fields: {len(missing_fields)}")
    
    is_aligned = len(missing_methods) == 0 and len(missing_fields) == 0
    
    if is_aligned:
        print("\n🎉 PERFECT ALIGNMENT! Ready for CloudPepper deployment!")
        return True
    else:
        print("\n⚠️ ALIGNMENT ISSUES DETECTED! Please fix before deployment.")
        return False

if __name__ == "__main__":
    success = check_sale_order_alignment()
    exit(0 if success else 1)
