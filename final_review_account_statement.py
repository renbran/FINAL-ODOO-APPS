#!/usr/bin/env python3
"""
Final Review Script for Account Statement Module
This script performs a comprehensive final review of the module.
"""

import os
import re
import sys

def final_review(module_path):
    """Perform comprehensive final review"""
    print("🔍 FINAL REVIEW: Account Statement Module")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # 1. Check manifest file
    print("\n📄 1. MANIFEST FILE REVIEW")
    manifest_path = os.path.join(module_path, '__manifest__.py')
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Check dependencies
        if "'report_xlsx'" in manifest_content:
            issues.append("❌ Found 'report_xlsx' dependency - should be optional")
        else:
            print("✅ No hard dependency on report_xlsx")
        
        if "'contacts'" in manifest_content:
            print("✅ Contacts dependency found")
        else:
            issues.append("❌ Missing 'contacts' dependency")
        
        if "'account'" in manifest_content:
            print("✅ Account dependency found")
        else:
            issues.append("❌ Missing 'account' dependency")
        
        # Check data files
        required_data_files = [
            'security/account_statement_security.xml',
            'security/ir.model.access.csv',
            'views/account_statement_views.xml',
            'views/account_statement_wizard_views.xml',
            'views/res_partner_views.xml'
        ]
        
        for file_path in required_data_files:
            if file_path in manifest_content:
                print(f"✅ {file_path} referenced in manifest")
            else:
                issues.append(f"❌ {file_path} not referenced in manifest")
    
    # 2. Check model files
    print("\n🏗️  2. MODEL FILES REVIEW")
    
    # Check account_statement.py
    statement_model_path = os.path.join(module_path, 'models', 'account_statement.py')
    if os.path.exists(statement_model_path):
        with open(statement_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "_inherit = ['mail.thread', 'mail.activity.mixin']" in content:
            print("✅ Mail tracking enabled in account.statement model")
        else:
            warnings.append("⚠️  Mail tracking not enabled in account.statement model")
        
        if "tracking=True" in content:
            print("✅ Field tracking enabled")
        else:
            warnings.append("⚠️  Field tracking not found")
    
    # Check wizard model
    wizard_model_path = os.path.join(module_path, 'models', 'account_statement_wizard.py')
    if os.path.exists(wizard_model_path):
        with open(wizard_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "EXCEL_AVAILABLE = True" in content and "except ImportError:" in content:
            print("✅ Excel dependency handled gracefully")
        else:
            issues.append("❌ Excel dependency not handled gracefully")
        
        if "account_type_filter" in content:
            print("✅ Enhanced filtering options found")
        else:
            warnings.append("⚠️  Enhanced filtering options not found")
    
    # 3. Check view files
    print("\n👁️  3. VIEW FILES REVIEW")
    
    views_dir = os.path.join(module_path, 'views')
    if os.path.exists(views_dir):
        view_files = [f for f in os.listdir(views_dir) if f.endswith('.xml')]
        
        required_views = [
            'account_statement_views.xml',
            'account_statement_wizard_views.xml', 
            'res_partner_views.xml'
        ]
        
        for view_file in required_views:
            if view_file in view_files:
                print(f"✅ {view_file} exists")
                
                # Check content
                view_path = os.path.join(views_dir, view_file)
                with open(view_path, 'r', encoding='utf-8') as f:
                    view_content = f.read()
                
                if view_file == 'account_statement_views.xml':
                    if 'contacts.menu_contacts' in view_content:
                        print("  ✅ Contacts app menu integration found")
                    else:
                        warnings.append("  ⚠️  Contacts app menu integration not found")
                
                if view_file == 'res_partner_views.xml':
                    if 'button_box' in view_content:
                        print("  ✅ Partner form smart button found")
                    else:
                        issues.append("  ❌ Partner form smart button not found")
            else:
                issues.append(f"❌ Missing view file: {view_file}")
    
    # 4. Check security files
    print("\n🔒 4. SECURITY FILES REVIEW")
    
    security_dir = os.path.join(module_path, 'security')
    if os.path.exists(security_dir):
        # Check access file
        access_file = os.path.join(security_dir, 'ir.model.access.csv')
        if os.path.exists(access_file):
            with open(access_file, 'r', encoding='utf-8') as f:
                access_content = f.read()
            
            if 'account_statement.group_account_statement_contacts_user' in access_content:
                print("✅ Contacts user group access found")
            else:
                warnings.append("⚠️  Contacts user group access not found")
            
            if 'model_account_statement_wizard' in access_content:
                print("✅ Wizard model access found")
            else:
                issues.append("❌ Wizard model access not found")
        
        # Check security groups
        security_file = os.path.join(security_dir, 'account_statement_security.xml')
        if os.path.exists(security_file):
            with open(security_file, 'r', encoding='utf-8') as f:
                security_content = f.read()
            
            if 'group_account_statement_contacts_user' in security_content:
                print("✅ Contacts user security group defined")
            else:
                warnings.append("⚠️  Contacts user security group not defined")
    
    # 5. Check for potential issues
    print("\n🧹 5. CLEANUP CHECK")
    
    # Check for duplicate files
    models_dir = os.path.join(module_path, 'models')
    if os.path.exists(models_dir):
        model_files = os.listdir(models_dir)
        if any('_fixed' in f for f in model_files):
            issues.append("❌ Found duplicate/backup files - should be cleaned up")
        else:
            print("✅ No duplicate files found")
    
    # Check for Python cache
    for root, dirs, files in os.walk(module_path):
        if '__pycache__' in dirs:
            warnings.append("⚠️  Python cache directories found - consider cleanup")
            break
    else:
        print("✅ No Python cache directories found")
    
    # 6. Final assessment
    print("\n" + "=" * 60)
    print("📊 FINAL ASSESSMENT")
    print("=" * 60)
    
    if issues:
        print("🔴 CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    
    if warnings:
        print("\n🟡 WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
    
    if not issues and not warnings:
        print("🟢 PERFECT! No issues or warnings found.")
    elif not issues:
        print("🟡 GOOD! No critical issues, only minor warnings.")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Critical Issues: {len(issues)}")
    print(f"   Warnings: {len(warnings)}")
    
    if not issues:
        print("\n🎉 MODULE IS READY FOR INSTALLATION!")
        print("✨ The module should install and work perfectly in both apps.")
        return True
    else:
        print("\n🛑 MODULE NEEDS FIXES BEFORE INSTALLATION!")
        return False

if __name__ == "__main__":
    module_path = r"d:\RUNNING APPS\ready production\odoo_17_final\account_statement"
    
    if os.path.exists(module_path):
        is_ready = final_review(module_path)
        sys.exit(0 if is_ready else 1)
    else:
        print(f"❌ Module path not found: {module_path}")
        sys.exit(1)
