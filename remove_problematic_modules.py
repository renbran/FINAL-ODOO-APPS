#!/usr/bin/env python3
"""
Remove Problematic Odoo Modules
This script identifies and removes modules that are not installable or cause conflicts.
"""

import os
import shutil
import json
from pathlib import Path

class ModuleCleaner:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.backup_path = self.base_path.parent / "backup_removed_modules"
        self.removed_modules = []
        self.kept_modules = []
        
    def load_analysis_report(self):
        """Load the previous analysis report"""
        report_path = self.base_path.parent / "module_analysis_report.json"
        if report_path.exists():
            with open(report_path, 'r') as f:
                return json.load(f)
        return None
    
    def create_backup_directory(self):
        """Create backup directory for removed modules"""
        if not self.backup_path.exists():
            self.backup_path.mkdir(parents=True)
        print(f"📁 Backup directory created: {self.backup_path}")
    
    def backup_and_remove_module(self, module_name, reason):
        """Backup a module to backup directory and remove from custom"""
        source_path = self.base_path / module_name
        if not source_path.exists():
            print(f"⚠️  Module {module_name} not found, skipping...")
            return False
        
        backup_module_path = self.backup_path / module_name
        
        try:
            # Copy to backup
            shutil.copytree(source_path, backup_module_path, dirs_exist_ok=True)
            # Remove from custom
            shutil.rmtree(source_path)
            
            self.removed_modules.append({
                'name': module_name,
                'reason': reason,
                'backup_location': str(backup_module_path)
            })
            
            print(f"✅ Removed {module_name} - {reason}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove {module_name}: {str(e)}")
            return False
    
    def resolve_duplicate_modules(self):
        """Resolve duplicate module conflicts by keeping the better version"""
        
        # Budget modules conflict - keep om_account_budget (newer, cleaner)
        print("\n🔧 Resolving budget module conflict...")
        if (self.base_path / "base_account_budget").exists():
            self.backup_and_remove_module("base_account_budget", "Duplicate budget module - keeping om_account_budget")
        
        # Property management conflict - keep property_sale_management (more comprehensive)
        print("\n🔧 Resolving property management conflict...")
        if (self.base_path / "property_management").exists():
            self.backup_and_remove_module("property_management", "Duplicate property module - keeping property_sale_management")
    
    def remove_modules_with_missing_dependencies(self):
        """Remove modules that have critical missing dependencies"""
        
        modules_to_remove = [
            # Modules with missing enterprise dependencies
            ("advanced_property_management", "Missing base_geolocalize dependency"),
            ("app_odoo_customize", "Missing base_setup and app_common dependencies"),
            ("base_accounting_kit", "Missing account_check_printing dependency"),
            ("dashboard_custom", "Missing spreadsheet_dashboard dependency"),
            ("hr_payroll_community", "Missing hr_contract and hr_holidays dependencies"),
            ("hr_payroll_account_community", "Depends on hr_payroll_community which has missing deps"),
            ("hr_uae_extended", "Missing hr_holidays dependency"),
            ("mx_elearning_plus", "Missing website_slides dependency"),
            ("theme_levelup", "Missing website_blog dependency"),
            ("uae_wps_report", "Missing hr_holidays dependency"),
            ("website_custom_contact_us", "Missing website_sale dependency"),
            ("website_subscription_package", "Missing website_sale dependency"),
        ]
        
        print("\n🔧 Removing modules with missing dependencies...")
        for module_name, reason in modules_to_remove:
            self.backup_and_remove_module(module_name, reason)
    
    def remove_conflicting_theme_modules(self):
        """Remove conflicting theme modules, keep only one main theme"""
        
        # Keep muk_web_theme as it's most comprehensive, remove others
        themes_to_remove = [
            ("backend_theme_infinito", "Multiple themes conflict - keeping muk_web_theme"),
            ("legion_enterprise_theme", "Multiple themes conflict - keeping muk_web_theme"),
            ("theme_levelup", "Multiple themes conflict - keeping muk_web_theme"),
            ("dark_mode_knk", "Theme conflict - keeping muk_web_theme"),
        ]
        
        print("\n🔧 Removing conflicting theme modules...")
        for module_name, reason in themes_to_remove:
            self.backup_and_remove_module(module_name, reason)
    
    def remove_redundant_dashboard_modules(self):
        """Remove redundant dashboard modules to prevent UI conflicts"""
        
        # Keep core dashboards, remove redundant ones
        dashboards_to_remove = [
            ("dashboard_custom", "Already removed for missing deps"),
            ("elite_sales_dashboard", "Redundant - keeping oe_sale_dashboard_17"),
            ("dashboard_sale", "Redundant - keeping oe_sale_dashboard_17"),
        ]
        
        print("\n🔧 Removing redundant dashboard modules...")
        for module_name, reason in dashboards_to_remove:
            if (self.base_path / module_name).exists():  # Check if not already removed
                self.backup_and_remove_module(module_name, reason)
    
    def remove_redundant_property_modules(self):
        """Remove redundant property management modules"""
        
        # Keep the most comprehensive ones
        property_modules_to_remove = [
            ("real_estate_for_teaching", "Redundant - keeping property_sale_management and odoo_real_estate"),
            ("rental_management", "Old version - keeping property_sale_management"),
            ("advanced_property_management", "Already removed for missing deps"),
        ]
        
        print("\n🔧 Removing redundant property modules...")
        for module_name, reason in property_modules_to_remove:
            if (self.base_path / module_name).exists():
                self.backup_and_remove_module(module_name, reason)
    
    def remove_duplicate_accounting_modules(self):
        """Remove duplicate accounting modules"""
        
        # Keep om_account_accountant, remove base_accounting_kit
        print("\n🔧 Resolving accounting module conflict...")
        if (self.base_path / "base_accounting_kit").exists():
            self.backup_and_remove_module("base_accounting_kit", "Duplicate accounting module - keeping om_account_accountant")
    
    def remove_version_incompatible_modules(self):
        """Remove modules with version compatibility issues"""
        
        version_incompatible = [
            ("ace_remove_powered_by_odoo", "Version 16.0 - incompatible with Odoo 17"),
        ]
        
        print("\n🔧 Removing version incompatible modules...")
        for module_name, reason in version_incompatible:
            self.backup_and_remove_module(module_name, reason)
    
    def remove_nested_modules(self):
        """Remove problematic nested modules"""
        
        nested_module_path = self.base_path / "app_odoo_customize" / "invoice_multi_approval"
        if nested_module_path.exists():
            try:
                shutil.rmtree(nested_module_path)
                print("✅ Removed nested module: app_odoo_customize/invoice_multi_approval")
            except Exception as e:
                print(f"❌ Failed to remove nested module: {str(e)}")
    
    def remove_duplicate_dynamic_dashboard(self):
        """Remove duplicate dynamic dashboard module"""
        
        duplicate_path = self.base_path / "odoo_dynamic_dashboard-17.0.2.0.1"
        if duplicate_path.exists():
            self.backup_and_remove_module("odoo_dynamic_dashboard-17.0.2.0.1", "Duplicate of odoo_dynamic_dashboard")
    
    def clean_modules(self):
        """Main method to clean all problematic modules"""
        
        print("🚀 Starting Module Cleanup Process...")
        print("=" * 60)
        
        # Create backup directory
        self.create_backup_directory()
        
        # Remove various types of problematic modules
        self.resolve_duplicate_modules()
        self.remove_modules_with_missing_dependencies()
        self.remove_conflicting_theme_modules()
        self.remove_redundant_dashboard_modules()
        self.remove_redundant_property_modules()
        self.remove_duplicate_accounting_modules()
        self.remove_version_incompatible_modules()
        self.remove_nested_modules()
        self.remove_duplicate_dynamic_dashboard()
        
        # Generate report
        self.generate_cleanup_report()
    
    def generate_cleanup_report(self):
        """Generate a report of the cleanup process"""
        
        print("\n📊 CLEANUP REPORT")
        print("=" * 60)
        print(f"Total modules removed: {len(self.removed_modules)}")
        print(f"Backup location: {self.backup_path}")
        
        if self.removed_modules:
            print("\n🗑️  REMOVED MODULES")
            print("-" * 40)
            for i, module in enumerate(self.removed_modules, 1):
                print(f"{i:2d}. {module['name']}")
                print(f"    Reason: {module['reason']}")
                print(f"    Backup: {module['backup_location']}")
                print()
        
        # Save cleanup report
        cleanup_report = {
            'timestamp': str(Path().cwd()),
            'total_removed': len(self.removed_modules),
            'backup_location': str(self.backup_path),
            'removed_modules': self.removed_modules
        }
        
        report_file = self.base_path.parent / "cleanup_report.json"
        with open(report_file, 'w') as f:
            json.dump(cleanup_report, f, indent=2)
        
        print(f"💾 Cleanup report saved to: {report_file}")
        
        print("\n🎯 RECOMMENDATIONS")
        print("-" * 40)
        print("1. Test your Odoo instance after cleanup")
        print("2. Check for any missing functionality")
        print("3. Install missing dependencies if needed")
        print("4. Backup is available if you need to restore any module")
        print("\n✅ Cleanup completed successfully!")

def main():
    base_path = r"d:\GitHub\osus_main\odoo\custom"
    
    cleaner = ModuleCleaner(base_path)
    
    # Ask for confirmation
    print("⚠️  WARNING: This will remove problematic modules from your Odoo installation.")
    print("A backup will be created before removal.")
    print(f"Modules will be moved to: {cleaner.backup_path}")
    
    response = input("\nDo you want to proceed? (y/N): ").strip().lower()
    
    if response == 'y' or response == 'yes':
        cleaner.clean_modules()
    else:
        print("❌ Cleanup cancelled.")

if __name__ == "__main__":
    main()
